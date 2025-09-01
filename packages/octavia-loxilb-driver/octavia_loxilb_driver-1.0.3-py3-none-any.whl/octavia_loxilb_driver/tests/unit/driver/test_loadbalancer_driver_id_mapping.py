"""Unit tests for ID mapping in load balancer driver."""

import unittest
from unittest import mock
import json

from octavia_loxilb_driver.common import exceptions, utils
from octavia_loxilb_driver.driver import loadbalancer_driver
from octavia_loxilb_driver.resource_mapping import mapper


class TestLoadBalancerDriverIDMapping(unittest.TestCase):
    """Test ID mapping functionality in LoadBalancerDriver."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = mock.MagicMock()
        self.api_client = mock.MagicMock()
        self.resource_mapper = mapper.ResourceMapper(self.config)
        
        self.driver = loadbalancer_driver.LoadBalancerDriver(
            self.api_client, self.resource_mapper, self.config
        )
        
        # Sample test data
        self.sample_loadbalancer = {
            "loadbalancer_id": "lb-12345",
            "vip_address": "192.168.1.100",
            "listeners": [
                {
                    "id": "listener-12345",
                    "protocol": "HTTP",
                    "protocol_port": 80,
                    "default_pool": {
                        "id": "pool-12345",
                        "protocol": "HTTP",
                        "lb_algorithm": "ROUND_ROBIN",
                        "members": [
                            {
                                "id": "member-1",
                                "address": "10.0.0.10",
                                "protocol_port": 8080,
                                "weight": 1,
                                "admin_state_up": True
                            }
                        ]
                    }
                }
            ]
        }
        
        self.loxilb_service_key = "192.168.1.100:80/tcp"
        
    def test_create_stores_id_mapping(self):
        """Test that create operation stores ID mapping."""
        # Mock API client responses
        self.api_client.get_loadbalancer.side_effect = exceptions.LoxiLBResourceNotFoundException(
            resource_type="loadbalancer", 
            resource_id="lb-12345"
        )
        self.api_client.create_loadbalancer.return_value = {"status": "success"}
        
        # Execute create
        self.driver.create(self.sample_loadbalancer)
        
        # Verify ID mapping was stored
        stored_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, "lb-12345"
        )
        self.assertEqual(stored_key, self.loxilb_service_key)
        
        # Verify metadata was stored
        metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, "lb-12345"
        )
        self.assertEqual(metadata["resource_type"], "loadbalancer")
        self.assertEqual(metadata["external_ip"], "192.168.1.100")
        self.assertEqual(metadata["port"], 80)
        self.assertEqual(metadata["protocol"], "tcp")
        
    def test_delete_removes_id_mapping(self):
        """Test that delete operation removes ID mapping."""
        # Pre-store mapping
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "lb-12345",
            self.loxilb_service_key,
            "loadbalancer",
            {"test": "data"}
        )
        
        # Mock API client
        self.api_client.delete_loadbalancer.return_value = {"status": "success"}
        
        # Execute delete
        self.driver.delete(self.sample_loadbalancer)
        
        # Verify mapping was removed
        stored_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, "lb-12345"
        )
        self.assertIsNone(stored_key)
        
    def test_get_uses_id_mapping(self):
        """Test that get operation uses ID mapping efficiently."""
        # Pre-store mapping
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "lb-12345",
            self.loxilb_service_key,
            "loadbalancer",
            {"test": "data"}
        )
        
        # Mock API responses
        mock_loxilb_service = {
            "serviceArguments": {
                "externalIP": "192.168.1.100",
                "port": 80,
                "protocol": "tcp",
                "name": "test-lb"
            },
            "endpoints": [
                {
                    "endpointIP": "10.0.0.10",
                    "targetPort": 8080,
                    "weight": 1,
                    "state": "active"
                }
            ]
        }
        self.api_client.get_loadbalancer.return_value = mock_loxilb_service
        
        # Execute get
        result = self.driver.get("lb-12345")
        
        # Verify API was called with correct service key
        self.api_client.get_loadbalancer.assert_called_once_with(self.loxilb_service_key)
        
        # Verify result has correct ID
        self.assertEqual(result["id"], "lb-12345")
        
    def test_get_recovers_missing_mapping(self):
        """Test that get operation can recover from missing ID mapping."""
        # Don't pre-store mapping to simulate lost mapping
        
        # Mock API responses
        mock_loxilb_services = [
            {
                "serviceArguments": {
                    "externalIP": "192.168.1.100",
                    "port": 80,
                    "protocol": "tcp",
                    "name": "test-lb"
                },
                "endpoints": []
            }
        ]
        self.api_client.list_loadbalancers.return_value = mock_loxilb_services
        self.api_client.get_loadbalancer.return_value = mock_loxilb_services[0]
        
        # Generate expected deterministic ID
        expected_id = utils.generate_deterministic_id(
            "loadbalancer",
            external_ip="192.168.1.100",
            port=80,
            protocol="tcp"
        )
        
        # Execute get with deterministic ID
        result = self.driver.get(expected_id)
        
        # Verify mapping was recovered
        stored_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, expected_id
        )
        self.assertEqual(stored_key, self.loxilb_service_key)
        
        # Verify result
        self.assertEqual(result["id"], expected_id)
        
    def test_get_all_maintains_mappings(self):
        """Test that get_all operation maintains ID mappings."""
        # Mock API responses
        mock_loxilb_services = [
            {
                "serviceArguments": {
                    "externalIP": "192.168.1.100",
                    "port": 80,
                    "protocol": "tcp",
                    "name": "test-lb-1"
                },
                "endpoints": []
            },
            {
                "serviceArguments": {
                    "externalIP": "192.168.1.101",
                    "port": 443,
                    "protocol": "tcp",
                    "name": "test-lb-2"
                },
                "endpoints": []
            }
        ]
        self.api_client.list_loadbalancers.return_value = mock_loxilb_services
        
        # Execute get_all
        results = self.driver.get_all()
        
        # Verify results
        self.assertEqual(len(results), 2)
        
        # Verify mappings were created
        for result in results:
            lb_id = result["id"]
            stored_key = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, lb_id
            )
            self.assertIsNotNone(stored_key)
            
    def test_deterministic_id_consistency(self):
        """Test that deterministic IDs are consistent across calls."""
        # Generate IDs multiple times with same parameters
        id1 = utils.generate_deterministic_id(
            "loadbalancer",
            external_ip="192.168.1.100",
            port=80,
            protocol="tcp"
        )
        
        id2 = utils.generate_deterministic_id(
            "loadbalancer",
            external_ip="192.168.1.100",
            port=80,
            protocol="tcp"
        )
        
        # Should be identical
        self.assertEqual(id1, id2)
        
        # Different parameters should generate different IDs
        id3 = utils.generate_deterministic_id(
            "loadbalancer",
            external_ip="192.168.1.101",
            port=80,
            protocol="tcp"
        )
        
        self.assertNotEqual(id1, id3)
        
    def test_id_mapping_cache_operations(self):
        """Test all ID mapping cache operations."""
        cache = utils.create_id_mapping_cache()
        
        # Test storing
        utils.store_id_mapping(
            cache,
            "octavia-id-123",
            "loxilb-key-456",
            "loadbalancer",
            {"test": "metadata"}
        )
        
        # Test retrieval
        loxilb_key = utils.get_loxilb_key_from_octavia_id(cache, "octavia-id-123")
        self.assertEqual(loxilb_key, "loxilb-key-456")
        
        octavia_id = utils.get_octavia_id_from_loxilb_key(cache, "loxilb-key-456")
        self.assertEqual(octavia_id, "octavia-id-123")
        
        # Test metadata
        metadata = utils.get_id_mapping_metadata(cache, "octavia-id-123")
        self.assertEqual(metadata["resource_type"], "loadbalancer")
        self.assertEqual(metadata["test"], "metadata")
        
        # Test removal
        utils.remove_id_mapping(cache, "octavia-id-123")
        
        loxilb_key = utils.get_loxilb_key_from_octavia_id(cache, "octavia-id-123")
        self.assertIsNone(loxilb_key)
        
    def test_recovery_from_persistent_storage(self):
        """Test recovery of ID mappings from persistent storage."""
        import tempfile
        import os
        
        # Create temporary storage file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            storage_data = {
                "octavia_to_loxilb": {
                    "lb-12345": "192.168.1.100:80/tcp",
                    "lb-67890": "192.168.1.101:443/tcp"
                },
                "loxilb_to_octavia": {
                    "192.168.1.100:80/tcp": "lb-12345",
                    "192.168.1.101:443/tcp": "lb-67890"
                },
                "resource_metadata": {
                    "lb-12345": {
                        "resource_type": "loadbalancer",
                        "external_ip": "192.168.1.100",
                        "port": 80,
                        "protocol": "tcp"
                    }
                },
                "version": "1.0"
            }
            json.dump(storage_data, f)
            temp_path = f.name
        
        try:
            # Create cache with storage path
            cache = utils.create_id_mapping_cache(temp_path)
            
            # Verify mappings were loaded
            self.assertEqual(len(cache["octavia_to_loxilb"]), 2)
            self.assertEqual(cache["octavia_to_loxilb"]["lb-12345"], "192.168.1.100:80/tcp")
            self.assertEqual(cache["loxilb_to_octavia"]["192.168.1.100:80/tcp"], "lb-12345")
            
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_recovery_from_loxilb_scan(self):
        """Test recovery by scanning LoxiLB services."""
        # Mock API client to return services
        mock_services = [
            {
                "serviceArguments": {
                    "externalIP": "192.168.1.100",
                    "port": 80,
                    "protocol": "tcp",
                    "name": "test-service-1"
                },
                "endpoints": []
            },
            {
                "serviceArguments": {
                    "externalIP": "192.168.1.101", 
                    "port": 443,
                    "protocol": "tcp",
                    "name": "test-service-2"
                },
                "endpoints": []
            }
        ]
        
        mock_api_client = mock.MagicMock()
        mock_api_client.list_loadbalancers.return_value = mock_services
        
        # Create empty cache
        cache = utils.create_id_mapping_cache()
        
        # Perform recovery
        recovered_count = utils.recover_id_mappings_from_loxilb(
            cache, mock_api_client, self.resource_mapper
        )
        
        # Verify recovery
        self.assertEqual(recovered_count, 2)
        self.assertEqual(len(cache["octavia_to_loxilb"]), 2)
        
        # Verify deterministic IDs were generated
        for service in mock_services:
            service_args = service["serviceArguments"]
            expected_id = utils.generate_deterministic_id(
                "loadbalancer",
                external_ip=service_args["externalIP"],
                port=service_args["port"],
                protocol=service_args["protocol"]
            )
            
            service_key = utils.get_loxilb_service_key(
                service_args["externalIP"],
                service_args["port"],
                service_args["protocol"]
            )
            
            self.assertIn(expected_id, cache["octavia_to_loxilb"])
            self.assertEqual(cache["octavia_to_loxilb"][expected_id], service_key)

    def test_driver_startup_recovery(self):
        """Test driver startup behavior."""
        # Mock LoxiLB services
        mock_services = [
            {
                "serviceArguments": {
                    "externalIP": "192.168.1.100",
                    "port": 80,
                    "protocol": "tcp"
                },
                "endpoints": []
            }
        ]
        
        # Mock API client
        mock_api_client = mock.MagicMock()
        mock_api_client.list_loadbalancers.return_value = mock_services
        
        # Test recovery function directly
        cache = utils.create_id_mapping_cache()
        recovered_count = utils.recover_id_mappings_from_loxilb(
            cache, mock_api_client, self.resource_mapper
        )
        
        # Verify recovery worked
        self.assertEqual(recovered_count, 1)
        self.assertEqual(len(cache["octavia_to_loxilb"]), 1)

    def test_mapping_consistency_check(self):
        """Test basic mapping consistency operations."""
        # Pre-populate cache with some mappings
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "lb-12345",
            "192.168.1.100:80/tcp",
            "loadbalancer",
            {}
        )
        
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "lb-orphaned",
            "192.168.1.999:80/tcp",  # This service doesn't exist in LoxiLB
            "loadbalancer",
            {}
        )
        
        # Verify cache operations work
        self.assertEqual(len(self.resource_mapper.id_mapping_cache["octavia_to_loxilb"]), 2)
        
        # Test mapping retrieval
        key1 = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, "lb-12345"
        )
        self.assertEqual(key1, "192.168.1.100:80/tcp")
        
        key2 = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, "lb-orphaned"
        )
        self.assertEqual(key2, "192.168.1.999:80/tcp")

    def test_persistent_storage_operations(self):
        """Test saving and loading from persistent storage."""
        import tempfile
        import os
        
        # Create temporary storage file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            # Create cache with storage
            cache = utils.create_id_mapping_cache(temp_path)
            
            # Add some mappings
            utils.store_id_mapping(
                cache,
                "test-lb-1",
                "192.168.1.100:80/tcp",
                "loadbalancer",
                {"test": "metadata"}
            )
            
            utils.store_id_mapping(
                cache,
                "test-lb-2", 
                "192.168.1.101:443/tcp",
                "loadbalancer",
                {"another": "metadata"}
            )
            
            # Verify file was created and has content
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r') as f:
                data = json.load(f)
                self.assertIn("octavia_to_loxilb", data)
                self.assertEqual(len(data["octavia_to_loxilb"]), 2)
            
            # Create new cache from same storage
            cache2 = utils.create_id_mapping_cache(temp_path)
            
            # Verify mappings were loaded
            self.assertEqual(len(cache2["octavia_to_loxilb"]), 2)
            self.assertEqual(cache2["octavia_to_loxilb"]["test-lb-1"], "192.168.1.100:80/tcp")
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_recovery_on_operation_failure(self):
        """Test that operations trigger recovery when mappings are missing."""
        # Clear the cache to simulate missing mappings
        self.resource_mapper.id_mapping_cache["octavia_to_loxilb"].clear()
        self.resource_mapper.id_mapping_cache["loxilb_to_octavia"].clear()
        
        # Mock API to return a service for recovery
        mock_services = [
            {
                "serviceArguments": {
                    "externalIP": "192.168.1.100",
                    "port": 80,
                    "protocol": "tcp"
                },
                "endpoints": []
            }
        ]
        self.api_client.list_loadbalancers.return_value = mock_services
        self.api_client.get_loadbalancer.return_value = mock_services[0]
        
        # Generate the deterministic ID that should be recovered
        expected_id = utils.generate_deterministic_id(
            "loadbalancer",
            external_ip="192.168.1.100",
            port=80,
            protocol="tcp"
        )
        
        # Try to get the load balancer (should trigger recovery)
        result = self.driver.get(expected_id)
        
        # Verify recovery occurred and mapping was restored
        stored_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, expected_id
        )
        self.assertEqual(stored_key, "192.168.1.100:80/tcp")
        self.assertEqual(result["id"], expected_id)
        

if __name__ == "__main__":
    unittest.main()
