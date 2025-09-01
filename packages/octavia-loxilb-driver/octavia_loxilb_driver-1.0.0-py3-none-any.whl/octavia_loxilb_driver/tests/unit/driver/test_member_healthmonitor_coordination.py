"""Unit tests for member-health monitor coordination functionality."""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock constants instead of importing octavia_lib directly
class MockConstants:
    """Mock Octavia constants for testing."""
    ACTIVE = 'ACTIVE'
    DELETED = 'DELETED'
    ERROR = 'ERROR'
    OFFLINE = 'OFFLINE'
    ONLINE = 'ONLINE'

lib_consts = MockConstants()

from octavia_loxilb_driver.driver.member_driver import MemberDriver
from octavia_loxilb_driver.driver.healthmonitor_driver import HealthMonitorDriver


class TestMemberHealthMonitorCoordination(unittest.TestCase):
    """Test coordination between member and health monitor drivers."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MagicMock()
        self.api_client = MagicMock()
        self.resource_mapper = MagicMock()
        
        # Set up ID mapping cache
        self.resource_mapper.id_mapping_cache = {
            "octavia_to_loxilb": {
                "member-123": "member-pool-123:tcp:10.0.0.10:8080",
                "healthmonitor-456": "healthmonitor-pool-123:http"
            },
            "loxilb_to_octavia": {
                "member-pool-123:tcp:10.0.0.10:8080": "member-123",
                "healthmonitor-pool-123:http": "healthmonitor-456"
            },
            "metadata": {
                "member-123": {
                    "resource_type": "member",
                    "address": "10.0.0.10",
                    "protocol_port": 8080,
                    "pool_id": "pool-123",
                    "admin_state_up": True,
                    "created_by": "member_driver"
                },
                "healthmonitor-456": {
                    "resource_type": "healthmonitor",
                    "type": "HTTP",
                    "pool_id": "pool-123",
                    "endpoints_created": ["10.0.0.10", "10.0.0.11"],
                    "created_by": "healthmonitor_driver"
                }
            }
        }
        
        self.member_driver = MemberDriver(self.api_client, self.resource_mapper, self.config)
        self.hm_driver = HealthMonitorDriver(self.api_client, self.resource_mapper, self.config)

    @patch('octavia_loxilb_driver.common.utils.get_loxilb_key_from_octavia_id')
    @patch('octavia_loxilb_driver.common.utils.get_id_mapping_metadata')
    @patch('octavia_loxilb_driver.common.utils.store_id_mapping')
    def test_health_monitor_remove_member_endpoint_probe(self, mock_store_mapping, mock_get_metadata, mock_get_key):
        """Test health monitor endpoint probe removal for a specific member."""
        
        # Setup mocks
        mock_get_metadata.side_effect = lambda cache, obj_id: cache["metadata"].get(obj_id)
        mock_get_key.return_value = "healthmonitor-pool-123:http"
        
        # Test the endpoint probe removal
        result = self.hm_driver.remove_member_endpoint_probe("pool-123", "10.0.0.10", 8080)
        
        # Verify API call was made
        self.api_client.delete_endpoint.assert_called_once_with("10.0.0.10:8080")
        
        # Verify metadata update was called
        mock_store_mapping.assert_called_once()
        
        # Verify result
        self.assertTrue(result)

    @patch('octavia_loxilb_driver.common.utils.get_loxilb_key_from_octavia_id')
    @patch('octavia_loxilb_driver.common.utils.get_id_mapping_metadata')
    def test_health_monitor_remove_member_endpoint_probe_no_health_monitors(self, mock_get_metadata, mock_get_key):
        """Test endpoint probe removal when no health monitors exist for the pool."""
        
        # Setup mocks to return no health monitors
        mock_get_metadata.side_effect = lambda cache, obj_id: None
        
        # Test the endpoint probe removal
        result = self.hm_driver.remove_member_endpoint_probe("pool-999", "10.0.0.10", 8080)
        
        # Verify no API calls were made
        self.api_client.delete_endpoint.assert_not_called()
        
        # Verify result
        self.assertFalse(result)

    def test_member_cleanup_health_monitor_endpoints(self):
        """Test member driver health monitor cleanup coordination."""
        
        # Setup mock health monitor driver  
        mock_hm_driver = MagicMock()
        mock_hm_driver.remove_member_endpoint_probe.return_value = True
        
        # Patch the HealthMonitorDriver class at the import location
        with patch('octavia_loxilb_driver.driver.healthmonitor_driver.HealthMonitorDriver') as mock_hm_driver_class:
            mock_hm_driver_class.return_value = mock_hm_driver
            
            # Test the cleanup method
            self.member_driver._cleanup_health_monitor_endpoints("pool-123", "10.0.0.10", 8080)
        
        # Verify health monitor driver was instantiated
        mock_hm_driver_class.assert_called_once_with(
            self.api_client, self.resource_mapper, self.config
        )
        
        # Verify endpoint probe removal was called
        mock_hm_driver.remove_member_endpoint_probe.assert_called_once_with(
            "pool-123", "10.0.0.10", 8080
        )

    def test_member_cleanup_health_monitor_endpoints_failure(self):
        """Test member driver health monitor cleanup with failure (should not raise)."""
        
        # Setup mock health monitor driver to raise an exception
        mock_hm_driver = MagicMock()
        mock_hm_driver.remove_member_endpoint_probe.side_effect = Exception("Test error")
        
        # Test the cleanup method - should not raise
        with patch('octavia_loxilb_driver.driver.healthmonitor_driver.HealthMonitorDriver') as mock_hm_driver_class:
            mock_hm_driver_class.return_value = mock_hm_driver
            
            try:
                self.member_driver._cleanup_health_monitor_endpoints("pool-123", "10.0.0.10", 8080)
            except Exception as e:
                self.fail(f"Health monitor cleanup should not raise exceptions: {e}")

    @patch('octavia_loxilb_driver.common.utils.get_loxilb_key_from_octavia_id')
    @patch('octavia_loxilb_driver.common.utils.get_id_mapping_metadata') 
    @patch('octavia_loxilb_driver.common.utils.remove_id_mapping')
    def test_member_delete_with_health_monitor_coordination(self, 
                                                           mock_remove_mapping, mock_get_metadata, 
                                                           mock_get_key):
        """Test complete member deletion with health monitor coordination."""
        
        # Setup mocks for proper key format
        mock_get_key.return_value = "member:pool-123:tcp:10.0.0.10:8080"  # Fixed format
        mock_get_metadata.return_value = {
            "resource_type": "member",
            "address": "10.0.0.10",
            "protocol_port": 8080,
            "pool_id": "pool-123",
            "admin_state_up": True
        }
        
        # Mock health monitor driver
        mock_hm_driver = MagicMock()
        mock_hm_driver.remove_member_endpoint_probe.return_value = True
        
        # Test member object
        member = {
            "id": "member-123",
            "address": "10.0.0.10",
            "protocol_port": 8080,
            "pool_id": "pool-123"
        }
        
        # Execute deletion with patched health monitor driver
        with patch('octavia_loxilb_driver.driver.healthmonitor_driver.HealthMonitorDriver') as mock_hm_driver_class:
            mock_hm_driver_class.return_value = mock_hm_driver
            result = self.member_driver.delete(member)
        
        # Verify health monitor cleanup was called - this is the main focus of this test
        mock_hm_driver.remove_member_endpoint_probe.assert_called_once_with(
            "pool-123", "10.0.0.10", 8080
        )
        
        # Verify mapping removal
        mock_remove_mapping.assert_called_once()
        
        # Verify result
        self.assertEqual(result["status"]["provisioning_status"], lib_consts.DELETED)

    def test_health_monitor_get_pool_health_monitors(self):
        """Test getting health monitors for a specific pool."""
        
        with patch('octavia_loxilb_driver.common.utils.get_id_mapping_metadata') as mock_get_metadata:
            # Mock metadata function to return our test data
            def side_effect(cache, obj_id):
                return cache["metadata"].get(obj_id)
            mock_get_metadata.side_effect = side_effect
            
            # Test getting health monitors for pool-123
            health_monitors = self.hm_driver._get_pool_health_monitors("pool-123")
            
            # Should find healthmonitor-456
            self.assertEqual(len(health_monitors), 1)
            self.assertIn("healthmonitor-456", health_monitors)

    def test_health_monitor_get_pool_health_monitors_no_matches(self):
        """Test getting health monitors for a pool with no health monitors."""
        
        with patch('octavia_loxilb_driver.common.utils.get_id_mapping_metadata') as mock_get_metadata:
            # Mock metadata function to return our test data
            def side_effect(cache, obj_id):
                return cache["metadata"].get(obj_id)
            mock_get_metadata.side_effect = side_effect
            
            # Test getting health monitors for non-existent pool
            health_monitors = self.hm_driver._get_pool_health_monitors("pool-999")
            
            # Should find no health monitors
            self.assertEqual(len(health_monitors), 0)


if __name__ == '__main__':
    unittest.main()
