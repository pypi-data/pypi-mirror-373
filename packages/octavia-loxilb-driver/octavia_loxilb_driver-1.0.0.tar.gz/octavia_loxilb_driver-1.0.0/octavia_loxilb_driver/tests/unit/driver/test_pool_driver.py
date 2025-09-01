"""Unit tests for Pool driver."""

import unittest
from unittest import mock
import time

from octavia_loxilb_driver.common import exceptions, utils
from octavia_loxilb_driver.driver import pool_driver
from octavia_loxilb_driver.resource_mapping import mapper


class TestPoolDriver(unittest.TestCase):
    """Test Pool driver functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = mock.MagicMock()
        self.api_client = mock.MagicMock()
        self.resource_mapper = mapper.ResourceMapper(self.config)
        
        self.driver = pool_driver.PoolDriver(
            self.api_client, self.resource_mapper, self.config
        )
        
        # Sample test data
        self.sample_pool = {
            "id": "pool-12345",
            "name": "test-pool",
            "description": "Test pool for unit tests",
            "protocol": "HTTP",
            "lb_algorithm": "ROUND_ROBIN",
            "session_persistence": None,
            "admin_state_up": True,
            "listener_id": "listener-67890",
            "loadbalancer_id": "lb-abcdef",
            "members": [
                {
                    "id": "member-1",
                    "address": "10.0.0.10",
                    "protocol_port": 8080,
                    "weight": 1,
                    "admin_state_up": True
                },
                {
                    "id": "member-2",
                    "address": "10.0.0.11", 
                    "protocol_port": 8080,
                    "weight": 1,
                    "admin_state_up": True
                }
            ]
        }

    def test_create_stores_pool_metadata(self):
        """Test that create operation stores pool metadata."""
        # Mock API client (no actual LoxiLB calls for pool creation)
        self.api_client.create_loadbalancer.return_value = {"status": "success"}
        
        # Execute create
        result = self.driver.create(self.sample_pool)
        
        # Verify metadata was stored
        stored_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, "pool-12345"
        )
        self.assertEqual(stored_key, "pool-pool-12345")
        
        # Verify metadata content
        metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, "pool-12345"
        )
        self.assertEqual(metadata["resource_type"], "pool")
        self.assertEqual(metadata["pool_name"], "test-pool")
        self.assertEqual(metadata["lb_algorithm"], "ROUND_ROBIN")
        self.assertEqual(metadata["protocol"], "HTTP")
        
        # Verify response
        self.assertEqual(result["status"]["id"], "pool-12345")
        self.assertEqual(result["status"]["provisioning_status"], "ACTIVE")

    def test_create_with_validation_error(self):
        """Test create with invalid pool configuration."""
        invalid_pool = {
            "id": "pool-invalid",
            "protocol": "INVALID_PROTOCOL",  # Invalid protocol
            "lb_algorithm": "ROUND_ROBIN"
        }
        
        with self.assertRaises(exceptions.LoxiLBValidationException) as context:
            self.driver.create(invalid_pool)
        
        # Verify validation error details
        self.assertIn("Unsupported pool protocol", str(context.exception))

    def test_update_modifies_metadata(self):
        """Test that update operation modifies stored metadata."""
        # Pre-store pool metadata
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "pool-12345",
            "pool-pool-12345",
            "pool",
            {
                "pool_name": "old-pool",
                "lb_algorithm": "ROUND_ROBIN",
                "admin_state_up": True,
                "listener_id": "listener-67890"
            }
        )
        
        # Mock API client
        self.api_client.create_loadbalancer.return_value = {"status": "success"}
        
        # Execute update
        updates = {
            "name": "updated-pool",
            "lb_algorithm": "LEAST_CONNECTIONS"
        }
        result = self.driver.update(self.sample_pool, updates)
        
        # Verify metadata was updated
        metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, "pool-12345"
        )
        self.assertEqual(metadata["pool_name"], "updated-pool")
        self.assertEqual(metadata["lb_algorithm"], "LEAST_CONNECTIONS")
        self.assertIsNotNone(metadata.get("updated_at"))
        
        # Verify response
        self.assertEqual(result["status"]["provisioning_status"], "ACTIVE")

    def test_update_admin_state_down(self):
        """Test updating pool admin state to down."""
        # Pre-store pool metadata
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "pool-12345",
            "pool-pool-12345", 
            "pool",
            {"admin_state_up": True, "listener_id": "listener-67890"}
        )
        
        # Execute update with admin_state_up = False
        updates = {"admin_state_up": False}
        result = self.driver.update(self.sample_pool, updates)
        
        # Verify metadata reflects disabled state
        metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, "pool-12345"
        )
        self.assertFalse(metadata["admin_state_up"])
        
        # Verify response shows offline status
        self.assertEqual(result["status"]["operating_status"], "OFFLINE")

    def test_delete_removes_metadata(self):
        """Test that delete operation removes pool metadata."""
        # Pre-store pool metadata
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "pool-12345",
            "pool-pool-12345",
            "pool",
            {"listener_id": "listener-67890"}
        )
        
        # Mock API client
        self.api_client.create_loadbalancer.return_value = {"status": "success"}
        
        # Execute delete
        result = self.driver.delete(self.sample_pool)
        
        # Verify metadata was removed
        stored_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, "pool-12345"
        )
        self.assertIsNone(stored_key)
        
        # Verify response
        self.assertEqual(result["status"]["provisioning_status"], "DELETED")

    def test_delete_nonexistent_pool(self):
        """Test deleting a pool that doesn't exist (idempotent)."""
        # Execute delete without pre-storing metadata
        result = self.driver.delete(self.sample_pool)
        
        # Should succeed without error
        self.assertEqual(result["status"]["provisioning_status"], "DELETED")

    def test_get_pool_from_metadata(self):
        """Test retrieving pool information from metadata."""
        # Pre-store pool metadata
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "pool-12345",
            "pool-pool-12345",
            "pool",
            {
                "pool_name": "test-pool",
                "pool_description": "Test pool",
                "lb_algorithm": "ROUND_ROBIN",
                "protocol": "HTTP",
                "admin_state_up": True,
                "listener_id": "listener-67890",
                "loadbalancer_id": "lb-abcdef",
                "members": [{"id": "member-1"}],
                "created_at": time.time()
            }
        )
        
        # Execute get
        result = self.driver.get("pool-12345")
        
        # Verify pool data
        self.assertEqual(result["id"], "pool-12345")
        self.assertEqual(result["name"], "test-pool")
        self.assertEqual(result["description"], "Test pool")
        self.assertEqual(result["lb_algorithm"], "ROUND_ROBIN")
        self.assertEqual(result["protocol"], "HTTP")
        self.assertEqual(result["listener_id"], "listener-67890")
        self.assertEqual(len(result["members"]), 1)

    def test_get_nonexistent_pool(self):
        """Test getting a pool that doesn't exist."""
        with self.assertRaises(exceptions.LoxiLBResourceNotFoundException):
            self.driver.get("nonexistent-pool")

    def test_get_all_pools(self):
        """Test retrieving all pools."""
        # Pre-store multiple pool metadata entries
        for i in range(3):
            pool_id = f"pool-{i}"
            utils.store_id_mapping(
                self.resource_mapper.id_mapping_cache,
                pool_id,
                f"pool-{pool_id}",
                "pool",
                {"pool_name": f"pool-{i}", "admin_state_up": True}
            )
        
        # Also store a non-pool mapping to verify filtering
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "listener-123",
            "192.168.1.100:80/tcp",
            "listener",
            {"external_ip": "192.168.1.100"}
        )
        
        # Execute get_all
        result = self.driver.get_all()
        
        # Verify only pools are returned
        self.assertEqual(len(result), 3)
        pool_ids = [pool["id"] for pool in result]
        self.assertIn("pool-0", pool_ids)
        self.assertIn("pool-1", pool_ids)
        self.assertIn("pool-2", pool_ids)

    def test_validate_pool_config_success(self):
        """Test successful pool configuration validation."""
        valid_pool = {
            "id": "pool-valid",
            "protocol": "HTTP",
            "lb_algorithm": "ROUND_ROBIN"
        }
        
        # Should not raise any exception
        self.driver._validate_pool_config(valid_pool)

    def test_validate_pool_config_missing_fields(self):
        """Test pool validation with missing required fields."""
        invalid_pool = {}  # Missing all required fields
        
        with self.assertRaises(exceptions.LoxiLBValidationException) as context:
            self.driver._validate_pool_config(invalid_pool)
        
        errors = str(context.exception)
        self.assertIn("Pool ID is required", errors)
        self.assertIn("Pool protocol is required", errors)

    def test_validate_pool_config_invalid_algorithm(self):
        """Test pool validation with invalid load balancing algorithm."""
        invalid_pool = {
            "id": "pool-invalid",
            "protocol": "HTTP",
            "lb_algorithm": "INVALID_ALGORITHM"
        }
        
        with self.assertRaises(exceptions.LoxiLBValidationException) as context:
            self.driver._validate_pool_config(invalid_pool)
        
        self.assertIn("Unsupported load balancing algorithm", str(context.exception))

    def test_validate_pool_config_invalid_session_persistence(self):
        """Test pool validation with invalid session persistence."""
        invalid_pool = {
            "id": "pool-invalid",
            "protocol": "HTTP",
            "lb_algorithm": "ROUND_ROBIN",
            "session_persistence": {"type": "INVALID_TYPE"}
        }
        
        with self.assertRaises(exceptions.LoxiLBValidationException) as context:
            self.driver._validate_pool_config(invalid_pool)
        
        self.assertIn("Unsupported session persistence type", str(context.exception))

    def test_update_pool_metadata_tracks_timestamp(self):
        """Test that metadata updates include timestamps."""
        # Pre-store pool metadata
        initial_time = time.time()
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "pool-12345",
            "pool-pool-12345",
            "pool",
            {"pool_name": "old-name", "created_at": initial_time}
        )
        
        # Wait a bit to ensure different timestamp
        time.sleep(0.1)
        
        # Execute metadata update
        self.driver._update_pool_metadata("pool-12345", {"pool_name": "new-name"})
        
        # Verify timestamp was updated
        metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, "pool-12345"
        )
        self.assertEqual(metadata["pool_name"], "new-name")
        self.assertGreater(metadata["updated_at"], initial_time)

    def test_update_listener_service_for_pool(self):
        """Test updating LoxiLB service when pool changes."""
        # Pre-store listener metadata
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "listener-67890",
            "192.168.1.100:80/tcp",
            "listener",
            {
                "external_ip": "192.168.1.100",
                "port": 80,
                "protocol": "tcp",
                "loadbalancer_id": "lb-abcdef"
            }
        )
        
        # Mock API client
        self.api_client.create_loadbalancer.return_value = {"status": "success"}
        
        # Execute service update
        pool_with_listener = {**self.sample_pool, "listener_id": "listener-67890"}
        self.driver._update_listener_service_for_pool(pool_with_listener)
        
        # Verify API was called
        self.api_client.create_loadbalancer.assert_called_once()

    def test_update_listener_service_no_listener(self):
        """Test service update when pool has no associated listener."""
        pool_without_listener = {**self.sample_pool, "listener_id": None}
        
        # Should complete without error or API calls
        self.driver._update_listener_service_for_pool(pool_without_listener)
        
        # Verify no API calls were made
        self.api_client.create_loadbalancer.assert_not_called()

    def test_create_updates_existing_pool(self):
        """Test that creating an existing pool performs an update."""
        # Pre-store pool metadata
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "pool-12345",
            "pool-pool-12345",
            "pool",
            {"pool_name": "existing-pool"}
        )
        
        # Mock the update method
        with mock.patch.object(self.driver, 'update') as mock_update:
            mock_update.return_value = {"status": {"id": "pool-12345"}}
            
            # Execute create
            result = self.driver.create(self.sample_pool)
            
            # Verify update was called instead of create
            mock_update.assert_called_once_with(self.sample_pool, {})


if __name__ == '__main__':
    unittest.main()
