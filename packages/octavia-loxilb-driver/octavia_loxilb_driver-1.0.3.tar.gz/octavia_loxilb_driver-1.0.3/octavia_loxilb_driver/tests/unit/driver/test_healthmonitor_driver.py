"""Unit tests for Endpoint-based Health Monitor driver."""

import unittest
from unittest import mock

# Use mock constants instead of importing octavia_lib directly
class MockConstants:
    """Mock Octavia constants for testing."""
    HEALTH_MONITOR_HTTP = 'HTTP'
    HEALTH_MONITOR_HTTPS = 'HTTPS' 
    HEALTH_MONITOR_TCP = 'TCP'
    HEALTH_MONITOR_UDP = 'UDP_CONNECT'
    HEALTH_MONITOR_PING = 'PING'
    
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'
    ACTIVE = 'ACTIVE'
    DELETED = 'DELETED'
    DISABLED = 'DISABLED'
    ERROR = 'ERROR'
    DEGRADED = 'DEGRADED'
    NO_MONITOR = 'NO_MONITOR'

lib_consts = MockConstants()

from octavia_loxilb_driver.common import constants, exceptions
from octavia_loxilb_driver.driver import healthmonitor_driver


class MockHealthMonitor:
    """Mock health monitor object for testing."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'healthmonitor-12345')
        self.type = kwargs.get('type', lib_consts.HEALTH_MONITOR_HTTP)
        self.delay = kwargs.get('delay', 5)
        self.timeout = kwargs.get('timeout', 3)
        self.max_retries = kwargs.get('max_retries', 3)
        self.max_retries_down = kwargs.get('max_retries_down', 3)
        self.admin_state_up = kwargs.get('admin_state_up', True)
        self.pool_id = kwargs.get('pool_id', 'pool-abcdef')
        self.name = kwargs.get('name', 'test-healthmonitor')
        self.http_method = kwargs.get('http_method', 'GET')
        self.url_path = kwargs.get('url_path', '/health')
        self.expected_codes = kwargs.get('expected_codes', '200')


class TestHealthMonitorDriver(unittest.TestCase):
    """Test Endpoint-based Health Monitor driver functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = mock.MagicMock()
        self.api_client = mock.MagicMock()
        self.resource_mapper = mock.MagicMock()
        
        self.driver = healthmonitor_driver.HealthMonitorDriver(
            self.api_client, self.resource_mapper, self.config
        )
        
        # Sample test data
        self.sample_healthmonitor = MockHealthMonitor()
        
        self.sample_pool_members = [
            {
                'id': 'member-1',
                'address': '10.0.0.10', 
                'protocol_port': 8080,
                'weight': 1
            },
            {
                'id': 'member-2',
                'address': '10.0.0.11',
                'protocol_port': 8080,
                'weight': 2
            }
        ]

    def test_create_healthmonitor_success(self):
        """Test successful health monitor creation."""
        # Mock pool members
        self.resource_mapper.get_resource_metadata.return_value = {
            'members': self.sample_pool_members
        }
        
        # Mock API client success
        self.api_client.create_endpoint.return_value = {'status': 'success'}
        
        result = self.driver.create(self.sample_healthmonitor)
        
        # Verify result
        self.assertEqual(result['id'], 'healthmonitor-12345')
        self.assertEqual(result['operating_status'], lib_consts.ONLINE)
        self.assertEqual(result['provisioning_status'], lib_consts.ACTIVE)
        
        # Verify store_resource_metadata was called
        self.assertEqual(self.resource_mapper.store_resource_metadata.call_count, 2)
        
        # Verify endpoint creation for each member
        self.assertEqual(self.api_client.create_endpoint.call_count, 2)

    def test_create_healthmonitor_with_validation_error(self):
        """Test health monitor creation with validation error."""
        invalid_hm = MockHealthMonitor(type='INVALID_TYPE')
        
        with self.assertRaises(exceptions.UnsupportedOptionError):
            self.driver.create(invalid_hm)

    def test_create_healthmonitor_with_endpoint_failure(self):
        """Test health monitor creation with endpoint creation failure."""
        # Mock pool members
        self.resource_mapper.get_resource_metadata.return_value = {
            'members': self.sample_pool_members
        }
        
        # Mock API client failure for one endpoint
        def side_effect(*args, **kwargs):
            if 'hm-healthmonitor-12345-10.0.0.10' in str(args):
                raise Exception("Endpoint creation failed")
            return {'status': 'success'}
        
        self.api_client.create_endpoint.side_effect = side_effect
        
        result = self.driver.create(self.sample_healthmonitor)
        
        # Should still succeed but only create one endpoint
        self.assertEqual(result['operating_status'], lib_consts.ONLINE)
        
        # Should still call store_resource_metadata with created endpoints
        self.assertEqual(self.resource_mapper.store_resource_metadata.call_count, 2)

    def test_update_healthmonitor_success(self):
        """Test successful health monitor update."""
        # Mock existing metadata
        existing_metadata = {
            'id': 'healthmonitor-12345',
            'type': lib_consts.HEALTH_MONITOR_HTTP,
            'endpoints_created': ['10.0.0.10', '10.0.0.11']
        }
        self.resource_mapper.get_resource_metadata.return_value = existing_metadata
        
        # Mock pool members
        pool_metadata = {'members': self.sample_pool_members}
        self.resource_mapper.get_resource_metadata.side_effect = [
            existing_metadata, pool_metadata
        ]
        
        result = self.driver.update(self.sample_healthmonitor)
        
        # Verify result
        self.assertEqual(result['id'], 'healthmonitor-12345')
        self.assertEqual(result['operating_status'], lib_consts.ONLINE)
        
        # Verify delete and create endpoints were called
        self.assertEqual(self.api_client.delete_endpoint.call_count, 2)
        self.assertEqual(self.api_client.create_endpoint.call_count, 2)

    def test_update_healthmonitor_not_found(self):
        """Test updating non-existent health monitor."""
        self.resource_mapper.get_resource_metadata.return_value = None
        
        with self.assertRaises(exceptions.DriverError):
            self.driver.update(self.sample_healthmonitor)

    def test_delete_healthmonitor_success(self):
        """Test successful health monitor deletion."""
        existing_metadata = {
            'id': 'healthmonitor-12345',
            'type': lib_consts.HEALTH_MONITOR_HTTP,
            'endpoints_created': ['10.0.0.10', '10.0.0.11']
        }
        self.resource_mapper.get_resource_metadata.return_value = existing_metadata
        
        result = self.driver.delete(self.sample_healthmonitor)
        
        # Verify result
        self.assertEqual(result['id'], 'healthmonitor-12345')
        self.assertEqual(result['operating_status'], lib_consts.OFFLINE)
        self.assertEqual(result['provisioning_status'], lib_consts.DELETED)
        
        # Verify endpoints were deleted
        self.assertEqual(self.api_client.delete_endpoint.call_count, 2)
        
        # Verify metadata was deleted
        self.resource_mapper.delete_resource_metadata.assert_called_once_with(
            'healthmonitor', 'healthmonitor-12345'
        )

    def test_delete_healthmonitor_not_found(self):
        """Test deleting non-existent health monitor."""
        self.resource_mapper.get_resource_metadata.return_value = None
        
        result = self.driver.delete(self.sample_healthmonitor)
        
        # Should still succeed (idempotent)
        self.assertEqual(result['provisioning_status'], lib_consts.DELETED)

    def test_get_healthmonitor_success(self):
        """Test successful health monitor retrieval."""
        metadata = {
            'id': 'healthmonitor-12345',
            'type': lib_consts.HEALTH_MONITOR_HTTP,
            'delay': 5,
            'timeout': 3,
            'admin_state_up': True,
            'endpoints_created': ['10.0.0.10']
        }
        self.resource_mapper.get_resource_metadata.return_value = metadata
        
        # Mock endpoint status
        self.api_client.get_endpoints.return_value = [
            {'hostName': '10.0.0.10/32'}
        ]
        
        result = self.driver.get('healthmonitor-12345')
        
        # Verify result
        self.assertEqual(result['id'], 'healthmonitor-12345')
        self.assertEqual(result['operating_status'], lib_consts.ONLINE)

    def test_get_healthmonitor_not_found(self):
        """Test getting non-existent health monitor."""
        self.resource_mapper.get_resource_metadata.return_value = None
        
        with self.assertRaises(exceptions.DriverError):
            self.driver.get('nonexistent-healthmonitor')

    def test_get_all_healthmonitors(self):
        """Test getting all health monitors."""
        all_metadata = {
            'healthmonitor-1': {
                'id': 'healthmonitor-1',
                'type': lib_consts.HEALTH_MONITOR_HTTP,
                'admin_state_up': True,
                'endpoints_created': []
            },
            'healthmonitor-2': {
                'id': 'healthmonitor-2', 
                'type': lib_consts.HEALTH_MONITOR_TCP,
                'admin_state_up': True,
                'endpoints_created': []
            }
        }
        self.resource_mapper.get_all_resource_metadata.return_value = all_metadata
        
        # Mock endpoint status
        self.api_client.get_endpoints.return_value = []
        
        results = self.driver.get_all()
        
        # Verify results
        self.assertEqual(len(results), 2)
        hm_ids = [hm['id'] for hm in results]
        self.assertIn('healthmonitor-1', hm_ids)
        self.assertIn('healthmonitor-2', hm_ids)

    def test_get_stats_not_supported(self):
        """Test that get_stats raises UnsupportedOptionError."""
        with self.assertRaises(exceptions.UnsupportedOptionError):
            self.driver.get_stats('healthmonitor-12345')

    def test_validate_healthmonitor_success(self):
        """Test successful health monitor validation."""
        # Should not raise exception
        self.driver._validate_healthmonitor(self.sample_healthmonitor)

    def test_validate_healthmonitor_unsupported_type(self):
        """Test validation with unsupported health monitor type."""
        invalid_hm = MockHealthMonitor(type='INVALID_TYPE')
        
        with self.assertRaises(exceptions.UnsupportedOptionError):
            self.driver._validate_healthmonitor(invalid_hm)

    def test_validate_healthmonitor_invalid_timing(self):
        """Test validation with invalid timing parameters."""
        # Delay too small
        invalid_hm = MockHealthMonitor(delay=0)
        with self.assertRaises(exceptions.UnsupportedOptionError):
            self.driver._validate_healthmonitor(invalid_hm)
        
        # Timeout >= delay
        invalid_hm = MockHealthMonitor(delay=5, timeout=5)
        with self.assertRaises(exceptions.UnsupportedOptionError):
            self.driver._validate_healthmonitor(invalid_hm)

    def test_validate_healthmonitor_invalid_retries(self):
        """Test validation with invalid retry parameters."""
        invalid_hm = MockHealthMonitor(max_retries=15)
        
        with self.assertRaises(exceptions.UnsupportedOptionError):
            self.driver._validate_healthmonitor(invalid_hm)

    def test_validate_healthmonitor_invalid_http_method(self):
        """Test validation with invalid HTTP method."""
        invalid_hm = MockHealthMonitor(
            type=lib_consts.HEALTH_MONITOR_HTTP,
            http_method='INVALID_METHOD'
        )
        
        with self.assertRaises(exceptions.UnsupportedOptionError):
            self.driver._validate_healthmonitor(invalid_hm)

    def test_build_healthmonitor_metadata(self):
        """Test building health monitor metadata."""
        metadata = self.driver._build_healthmonitor_metadata(self.sample_healthmonitor)
        
        # Verify metadata content
        self.assertEqual(metadata['id'], 'healthmonitor-12345')
        self.assertEqual(metadata['type'], lib_consts.HEALTH_MONITOR_HTTP)
        self.assertEqual(metadata['delay'], 5)
        self.assertEqual(metadata['timeout'], 3)
        self.assertEqual(metadata['max_retries'], 3)
        self.assertEqual(metadata['admin_state_up'], True)
        self.assertEqual(metadata['pool_id'], 'pool-abcdef')
        self.assertIn('created_at', metadata)
        self.assertIn('updated_at', metadata)

    def test_build_endpoint_config_http(self):
        """Test building LoxiLB endpoint configuration for HTTP health monitor."""
        member = {'address': '10.0.0.10', 'protocol_port': 8080}
        
        config = self.driver._build_endpoint_config(self.sample_healthmonitor, member)
        
        # Verify endpoint configuration
        self.assertEqual(config['hostName'], '10.0.0.10/32')
        self.assertEqual(config['name'], 'hm-healthmonitor-12345-10.0.0.10')
        self.assertEqual(config['inactiveReTries'], 3)
        self.assertEqual(config['probeType'], 'http')
        self.assertEqual(config['probeDuration'], 5)
        self.assertEqual(config['probePort'], 8080)
        self.assertEqual(config['probeReq'], '/health')
        self.assertEqual(config['probeResp'], '200')

    def test_build_endpoint_config_tcp(self):
        """Test building LoxiLB endpoint configuration for TCP health monitor."""
        tcp_hm = MockHealthMonitor(type=lib_consts.HEALTH_MONITOR_TCP)
        member = {'address': '10.0.0.10', 'protocol_port': 8080}
        
        config = self.driver._build_endpoint_config(tcp_hm, member)
        
        # Verify endpoint configuration
        self.assertEqual(config['probeType'], 'tcp')
        self.assertNotIn('probeReq', config)
        self.assertNotIn('probeResp', config)

    def test_get_pool_members_success(self):
        """Test getting pool members successfully."""
        pool_metadata = {'members': self.sample_pool_members}
        self.resource_mapper.get_resource_metadata.return_value = pool_metadata
        
        members = self.driver._get_pool_members('pool-abcdef')
        
        # Verify members
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0]['address'], '10.0.0.10')
        self.assertEqual(members[1]['address'], '10.0.0.11')

    def test_get_pool_members_not_found(self):
        """Test getting pool members when pool not found."""
        self.resource_mapper.get_resource_metadata.return_value = None
        
        members = self.driver._get_pool_members('nonexistent-pool')
        
        # Should return empty list
        self.assertEqual(len(members), 0)

    def test_delete_endpoint_probes(self):
        """Test deleting endpoint probes."""
        metadata = {
            'endpoints_created': ['10.0.0.10', '10.0.0.11'],
            'type': lib_consts.HEALTH_MONITOR_HTTP
        }
        
        self.driver._delete_endpoint_probes('healthmonitor-12345', metadata)
        
        # Verify delete_endpoint was called for each endpoint
        self.assertEqual(self.api_client.delete_endpoint.call_count, 2)

    def test_determine_operating_status_disabled(self):
        """Test determining operating status when admin_state_up is False."""
        metadata = {'admin_state_up': False}
        
        status = self.driver._determine_operating_status(metadata)
        
        self.assertEqual(status, constants.DISABLED)

    def test_determine_operating_status_no_endpoints(self):
        """Test determining operating status with no endpoints."""
        metadata = {'admin_state_up': True, 'endpoints_created': []}
        
        status = self.driver._determine_operating_status(metadata)
        
        self.assertEqual(status, lib_consts.NO_MONITOR)

    def test_determine_operating_status_online(self):
        """Test determining operating status when all endpoints are online."""
        metadata = {
            'admin_state_up': True,
            'endpoints_created': ['10.0.0.10', '10.0.0.11']
        }
        
        # Mock all endpoints found
        self.api_client.get_endpoints.return_value = [
            {'hostName': '10.0.0.10/32'},
            {'hostName': '10.0.0.11/32'}
        ]
        
        status = self.driver._determine_operating_status(metadata)
        
        self.assertEqual(status, lib_consts.ONLINE)

    def test_determine_operating_status_degraded(self):
        """Test determining operating status when some endpoints are offline."""
        metadata = {
            'admin_state_up': True,
            'endpoints_created': ['10.0.0.10', '10.0.0.11']
        }
        
        # Mock only one endpoint found
        self.api_client.get_endpoints.return_value = [
            {'hostName': '10.0.0.10/32'}
        ]
        
        status = self.driver._determine_operating_status(metadata)
        
        self.assertEqual(status, lib_consts.DEGRADED)

    def test_determine_operating_status_error(self):
        """Test determining operating status when API call fails."""
        metadata = {
            'admin_state_up': True,
            'endpoints_created': ['10.0.0.10']
        }
        
        # Mock API failure
        self.api_client.get_endpoints.side_effect = Exception("API failure")
        
        status = self.driver._determine_operating_status(metadata)
        
        self.assertEqual(status, lib_consts.ERROR)

    def test_update_member_status_success(self):
        """Test updating member status successfully."""
        member_metadata = {
            'address': '10.0.0.10',
            'protocol_port': 8080,
            'protocol': 'tcp'
        }
        self.resource_mapper.get_resource_metadata.return_value = member_metadata
        
        result = self.driver.update_member_status('member-1', lib_consts.ONLINE)
        
        # Verify result
        self.assertEqual(result['id'], 'member-1')
        self.assertEqual(result['operating_status'], lib_consts.ONLINE)
        
        # Verify set_endpoint_host_state was called
        self.api_client.set_endpoint_host_state.assert_called_once()

    def test_update_member_status_member_not_found(self):
        """Test updating member status when member not found."""
        self.resource_mapper.get_resource_metadata.return_value = None
        
        with self.assertRaises(exceptions.DriverError):
            self.driver.update_member_status('nonexistent-member', lib_consts.ONLINE)


if __name__ == "__main__":
    unittest.main()
