"""Unit tests for Member driver."""

import unittest
from unittest import mock
import time

from octavia_loxilb_driver.common import exceptions, utils
from octavia_loxilb_driver.driver import member_driver
from octavia_loxilb_driver.resource_mapping import mapper


class TestMemberDriver(unittest.TestCase):
    """Test Member driver functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = mock.MagicMock()
        self.api_client = mock.MagicMock()
        self.resource_mapper = mapper.ResourceMapper(self.config)
        
        self.driver = member_driver.MemberDriver(
            self.api_client, self.resource_mapper, self.config
        )
        
        # Sample test data
        self.sample_member = {
            "id": "member-12345",
            "name": "test-member",
            "address": "10.0.0.10",
            "protocol_port": 8080,
            "weight": 1,
            "admin_state_up": True,
            "monitor_address": "10.0.0.10",
            "monitor_port": 8080,
            "subnet_id": "subnet-67890",
            "pool_id": "pool-abcdef",
            "backup": False
        }
        
        self.sample_pool_metadata = {
            "resource_type": "pool",
            "pool_name": "test-pool",
            "lb_algorithm": "ROUND_ROBIN",
            "protocol": "HTTP",
            "listener_id": "listener-12345",
            "created_at": time.time()
        }
        
        self.sample_listener_metadata = {
            "resource_type": "listener",
            "external_ip": "192.168.1.100",
            "port": 80,
            "protocol": "HTTP",
            "loadbalancer_id": "lb-12345",
            "created_at": time.time()
        }

    def test_create_stores_member_metadata(self):
        """Test that create operation stores member metadata correctly."""
        result = self.driver.create(self.sample_member)
        
        # Verify successful response
        self.assertEqual(result["status"]["id"], "member-12345")
        self.assertEqual(result["status"]["provisioning_status"], "ACTIVE")
        self.assertEqual(result["status"]["operating_status"], "ONLINE")
        
        # Verify metadata is stored
        metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, "member-12345"
        )
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["address"], "10.0.0.10")
        self.assertEqual(metadata["protocol_port"], 8080)
        self.assertEqual(metadata["weight"], 1)
        self.assertEqual(metadata["pool_id"], "pool-abcdef")

    def test_create_updates_existing_member(self):
        """Test that create operation updates existing member if mapping exists."""
        # Pre-store a member mapping
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "member-12345",
            "member-member-12345",
            "member",
            {"address": "10.0.0.9", "protocol_port": 8080}
        )
        
        result = self.driver.create(self.sample_member)
        
        # Should still succeed
        self.assertEqual(result["status"]["id"], "member-12345")

    def test_create_with_validation_error(self):
        """Test member creation with validation errors."""
        invalid_member = {
            "id": "member-invalid",
            # Missing required fields
        }
        
        with self.assertRaises(exceptions.LoxiLBValidationException):
            self.driver.create(invalid_member)

    def test_update_modifies_metadata(self):
        """Test that update operation modifies member metadata."""
        # Create initial member
        self.driver.create(self.sample_member)
        
        updates = {
            "weight": 5,
            "admin_state_up": False
        }
        
        result = self.driver.update(self.sample_member, updates)
        
        # Verify response
        self.assertEqual(result["status"]["id"], "member-12345")
        self.assertEqual(result["status"]["operating_status"], "OFFLINE")
        
        # Verify metadata is updated
        metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, "member-12345"
        )
        self.assertEqual(metadata["weight"], 5)
        self.assertEqual(metadata["admin_state_up"], False)

    def test_update_admin_state_down(self):
        """Test member update with admin state disabled."""
        # Create initial member
        self.driver.create(self.sample_member)
        
        updates = {"admin_state_up": False}
        result = self.driver.update(self.sample_member, updates)
        
        self.assertEqual(result["status"]["operating_status"], "OFFLINE")

    def test_update_pool_service_for_member_change(self):
        """Test that member changes trigger pool service updates."""
        # Setup pool and listener metadata
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "pool-abcdef",
            "pool-pool-abcdef",
            "pool",
            self.sample_pool_metadata
        )
        
        utils.store_id_mapping(
            self.resource_mapper.id_mapping_cache,
            "listener-12345",
            "listener-listener-12345",
            "listener",
            self.sample_listener_metadata
        )
        
        # Create member
        self.driver.create(self.sample_member)
        
        # Verify API client was called
        self.api_client.create_loadbalancer.assert_called()

    def test_delete_removes_metadata(self):
        """Test that delete operation removes member metadata."""
        # Create member first
        self.driver.create(self.sample_member)
        
        # Verify member exists
        stored_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, "member-12345"
        )
        self.assertIsNotNone(stored_key)
        
        # Delete member
        result = self.driver.delete(self.sample_member)
        
        # Verify response
        self.assertEqual(result["status"]["id"], "member-12345")
        self.assertEqual(result["status"]["provisioning_status"], "DELETED")
        
        # Verify mapping is removed
        stored_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, "member-12345"
        )
        self.assertIsNone(stored_key)

    def test_delete_nonexistent_member(self):
        """Test deleting a member that doesn't exist."""
        result = self.driver.delete(self.sample_member)
        
        # Should succeed (idempotent)
        self.assertEqual(result["status"]["id"], "member-12345")
        self.assertEqual(result["status"]["provisioning_status"], "DELETED")

    def test_get_member_from_metadata(self):
        """Test retrieving member information from metadata."""
        # Create member first
        self.driver.create(self.sample_member)
        
        # Get member
        member_data = self.driver.get("member-12345")
        
        # Verify member data
        self.assertEqual(member_data["id"], "member-12345")
        self.assertEqual(member_data["address"], "10.0.0.10")
        self.assertEqual(member_data["protocol_port"], 8080)
        self.assertEqual(member_data["weight"], 1)
        self.assertEqual(member_data["pool_id"], "pool-abcdef")

    def test_get_nonexistent_member(self):
        """Test getting a member that doesn't exist."""
        with self.assertRaises(exceptions.LoxiLBResourceNotFoundException):
            self.driver.get("nonexistent-member")

    def test_get_all_members(self):
        """Test getting all members."""
        # Create multiple members
        member1 = self.sample_member.copy()
        member2 = self.sample_member.copy()
        member2["id"] = "member-67890"
        member2["address"] = "10.0.0.11"
        
        self.driver.create(member1)
        self.driver.create(member2)
        
        # Get all members
        members = self.driver.get_all()
        
        # Verify we get both members
        self.assertEqual(len(members), 2)
        member_ids = [m["id"] for m in members]
        self.assertIn("member-12345", member_ids)
        self.assertIn("member-67890", member_ids)

    def test_validate_member_config_success(self):
        """Test successful member configuration validation."""
        # Should not raise any exception
        self.driver._validate_member_config(self.sample_member)

    def test_validate_member_config_missing_fields(self):
        """Test member validation with missing required fields."""
        invalid_member = {
            "id": "member-invalid"
            # Missing address and protocol_port
        }
        
        with self.assertRaises(exceptions.LoxiLBValidationException) as context:
            self.driver._validate_member_config(invalid_member)
        
        errors = str(context.exception)
        self.assertIn("Member address is required", errors)
        self.assertIn("Member protocol port is required", errors)

    def test_validate_member_config_invalid_ip(self):
        """Test member validation with invalid IP address."""
        invalid_member = self.sample_member.copy()
        invalid_member["address"] = "invalid-ip"
        
        with self.assertRaises(exceptions.LoxiLBValidationException) as context:
            self.driver._validate_member_config(invalid_member)
        
        self.assertIn("Invalid IP address format", str(context.exception))

    def test_validate_member_config_invalid_port(self):
        """Test member validation with invalid port numbers."""
        invalid_member = self.sample_member.copy()
        invalid_member["protocol_port"] = 70000  # Out of range
        
        with self.assertRaises(exceptions.LoxiLBValidationException) as context:
            self.driver._validate_member_config(invalid_member)
        
        self.assertIn("Protocol port must be between 1 and 65535", str(context.exception))

    def test_validate_member_config_invalid_weight(self):
        """Test member validation with invalid weight."""
        invalid_member = self.sample_member.copy()
        invalid_member["weight"] = 300  # Out of range
        
        with self.assertRaises(exceptions.LoxiLBValidationException) as context:
            self.driver._validate_member_config(invalid_member)
        
        self.assertIn("Weight must be between 0 and 256", str(context.exception))

    def test_update_member_metadata_tracks_timestamp(self):
        """Test that member metadata updates include timestamps."""
        # Create member first
        self.driver.create(self.sample_member)
        
        # Get initial metadata
        initial_metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, "member-12345"
        )
        
        # Wait a moment and update
        time.sleep(0.1)
        self.driver._update_member_metadata("member-12345", {"weight": 5})
        
        # Get updated metadata
        updated_metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, "member-12345"
        )
        
        # Verify timestamp was updated
        self.assertGreater(
            updated_metadata["updated_at"], 
            initial_metadata.get("updated_at", 0)
        )
        self.assertEqual(updated_metadata["weight"], 5)

    def test_get_active_pool_members(self):
        """Test getting active members for a specific pool."""
        # Create members in different pools
        member1 = self.sample_member.copy()
        member2 = self.sample_member.copy()
        member2["id"] = "member-67890"
        member2["address"] = "10.0.0.11"
        
        member3 = self.sample_member.copy()
        member3["id"] = "member-99999"
        member3["pool_id"] = "different-pool"
        
        self.driver.create(member1)
        self.driver.create(member2)
        self.driver.create(member3)
        
        # Get active members for the test pool
        active_members = self.driver._get_active_pool_members("pool-abcdef")
        
        # Should only return members from the specified pool
        self.assertEqual(len(active_members), 2)
        member_ids = [m["id"] for m in active_members]
        self.assertIn("member-12345", member_ids)
        self.assertIn("member-67890", member_ids)
        self.assertNotIn("member-99999", member_ids)

    def test_get_active_pool_members_excludes_disabled(self):
        """Test that disabled members are excluded from active member list."""
        # Create active member
        member1 = self.sample_member.copy()
        self.driver.create(member1)
        
        # Create disabled member
        member2 = self.sample_member.copy()
        member2["id"] = "member-67890"
        member2["admin_state_up"] = False
        self.driver.create(member2)
        
        # Get active members
        active_members = self.driver._get_active_pool_members("pool-abcdef")
        
        # Should only return the active member
        self.assertEqual(len(active_members), 1)
        self.assertEqual(active_members[0]["id"], "member-12345")


if __name__ == "__main__":
    unittest.main()
