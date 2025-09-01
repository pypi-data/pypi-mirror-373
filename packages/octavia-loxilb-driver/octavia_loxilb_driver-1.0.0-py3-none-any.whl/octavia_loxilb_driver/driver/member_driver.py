# octavia_loxilb_driver/driver/member_driver.py
"""Enhanced Member Management Driver for LoxiLB with Zero-Downtime Operations."""

import time

from octavia_lib.common import constants as lib_consts
from oslo_log import log as logging

from octavia_loxilb_driver.common import exceptions, utils

LOG = logging.getLogger(__name__)


def extract_member_attr(member, key, default=None):
    """Safely extract attribute from dict or object."""
    if isinstance(member, dict):
        return member.get(key, default)
    return getattr(member, key, default)


class MemberDriver:
    """Enhanced Member Management Driver for LoxiLB with Zero-Downtime Operations.
    
    This driver handles Octavia member operations with improved efficiency and
    reliability. It prioritizes endpoint API operations over service recreation
    to eliminate unnecessary downtime during member management.
    
    Key Features:
    - Zero-downtime member additions/removals using endpoint APIs
    - Fallback to service recreation only when necessary
    - Enhanced error handling and state validation
    - Performance optimization for high-traffic scenarios
    """

    def __init__(self, api_client, resource_mapper, config):
        """Initialize the MemberDriver.
        
        Args:
            api_client: LoxiLB API client instance
            resource_mapper: Resource mapper with ID mapping capabilities
            config: Driver configuration object
        """
        self.api_client = api_client
        self.resource_mapper = resource_mapper
        self.config = config

    def create(self, member, pool=None, loadbalancer=None):
        """Create a member.

        Creates a new member by storing member configuration in metadata and updating
        the associated LoxiLB service endpoints. In LoxiLB, members are not standalone
        resources but are part of the service endpoint configuration.

        Args:
            member: The member object from Octavia containing:
                - id: Member UUID
                - address: IP address of the backend server
            pool: The pool object from database
            loadbalancer: The loadbalancer object from database
                - protocol_port: Port number for the backend service
                - weight: Weight for load balancing (1-256)
                - admin_state_up: Administrative state
                - monitor_address: Optional monitoring IP address
                - monitor_port: Optional monitoring port
                - name: Member name
                - subnet_id: Subnet ID for the member
                - pool_id: Associated pool ID
                - backup: Whether this is a backup member

        Returns:
            dict: Status information for Octavia

        Raises:
            LoxiLBOperationException: If the member creation fails
            LoxiLBValidationException: If the member configuration is invalid
        """
        member_id = extract_member_attr(member, "id") or extract_member_attr(member, "member_id")
        address = extract_member_attr(member, "address") or extract_member_attr(member, "ip_address")
        protocol_port = extract_member_attr(member, "protocol_port")
        name = extract_member_attr(member, "name")
        weight = extract_member_attr(member, "weight", 1)
        admin_state_up = extract_member_attr(member, "admin_state_up")
        if admin_state_up is None:
            admin_state_up = extract_member_attr(member, "enabled", True)
        subnet_id = extract_member_attr(member, "subnet_id")
        pool_id = extract_member_attr(member, "pool_id")
        backup = extract_member_attr(member, "backup", False)
        monitor_address = extract_member_attr(member, "monitor_address")
        monitor_port = extract_member_attr(member, "monitor_port")
        
        LOG.info("Creating member %s with address %s:%s", member_id, address, protocol_port)
        
        try:
            # Debug: Log all attributes of input arguments (member, pool, loadbalancer)
            LOG.debug("Member attributes: %s", vars(member) if not isinstance(member, dict) else member)
            LOG.debug("Pool attributes: %s", vars(pool) if pool and not isinstance(pool, dict) else pool)
            LOG.debug("Loadbalancer attributes: %s", vars(loadbalancer) if loadbalancer and not isinstance(loadbalancer, dict) else loadbalancer)            

            # Step 1: Validate member configuration
            self._validate_member_config(member)
            # Step 2: Check if member already exists to prevent conflicts
            existing_mapping = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, member_id
            )
            if existing_mapping:
                LOG.warning("Member %s already has mapping %s, updating instead", member_id, existing_mapping)
                return self.update(member, {}, pool, loadbalancer)
            # Step 3: Generate member identifier for mapping
            member_mapping_key = f"member-{member_id}"
            # Step 4: Store member configuration in metadata for tracking
            utils.store_id_mapping(
                self.resource_mapper.id_mapping_cache,
                member_id,
                member_mapping_key,
                "member",
                {
                    "member_name": name,
                    "address": address,
                    "protocol_port": protocol_port,
                    "weight": weight,
                    "admin_state_up": admin_state_up,
                    "monitor_address": monitor_address,
                    "monitor_port": monitor_port,
                    "subnet_id": subnet_id,
                    "pool_id": pool_id,
                    "backup": backup,
                    "created_by": "member_driver"
                }
            )
            # Step 5: Update the associated pool's LoxiLB service
            if pool_id:
                try:
                    self._update_pool_service_for_member_change(member)
                except Exception as e:
                    LOG.warning("Failed to update pool service for new member %s: %s", member_id, e)
            LOG.info("Successfully created member %s", member_id)
            # Step 6: Return status information to Octavia
            return member_id
        except exceptions.LoxiLBValidationException:
            # Re-raise validation exceptions as-is
            raise
        except Exception as e:
            LOG.error("Failed to create member %s: %s", member_id, e)
            raise exceptions.LoxiLBOperationException(
                operation="create_member",
                resource_type="member",
                resource_id=member_id,
                reason=str(e),
            )

    def update(self, old_member, member_updates, pool=None, loadbalancer=None):
        """Update a member.

        Updates an existing member by modifying its configuration and updating
        the associated LoxiLB service endpoints.

        Args:
            old_member: The member object before the update
            member_updates: Dictionary with the changed attributes
            pool: The pool object from database
            loadbalancer: The loadbalancer object from database

        Returns:
            dict: Status information for Octavia

        Raises:
            LoxiLBOperationException: If the member update fails
        """
        member_id = extract_member_attr(old_member, "id") or extract_member_attr(old_member, "member_id")
        LOG.info("Updating member %s with changes: %s", member_id, list(member_updates.keys()))
        try:
            # Step 1: Get existing member mapping
            member_mapping_key = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, member_id
            )
            if not member_mapping_key:
                LOG.warning("No ID mapping found for member %s during update", member_id)
                # Create the member if it doesn't exist
                merged_member = dict(old_member) if isinstance(old_member, dict) else old_member.__dict__.copy()
                merged_member.update(member_updates)
                return self.create(merged_member, pool, loadbalancer)
            # Step 2: Get current metadata
            current_metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache, member_id
            )
            # Step 3: Handle configuration updates
            metadata_updates = {}
            for key, value in member_updates.items():
                if key in ["name", "address", "protocol_port", "weight", "admin_state_up", "monitor_address", "monitor_port", "backup"]:
                    metadata_key = f"member_{key}" if key == "name" else key
                    metadata_updates[metadata_key] = value
            # Store updated metadata
            if metadata_updates:
                self._update_member_metadata(member_id, metadata_updates)
            # Step 4: Update the associated LoxiLB service
            updated_member = dict(old_member) if isinstance(old_member, dict) else old_member.__dict__.copy()
            updated_member.update(member_updates)
            pool_id = extract_member_attr(updated_member, "pool_id")
            if current_metadata.get("pool_id") or pool_id:
                try:
                    self._update_pool_service_for_member_change(updated_member)
                    LOG.info("Updated LoxiLB service for member %s changes", member_id)
                except Exception as e:
                    LOG.warning("Failed to update pool service for member %s: %s", member_id, e)
            LOG.info("Successfully updated member %s", member_id)
            return member_id
        except Exception as e:
            LOG.error("Failed to update member %s: %s", member_id, e)
            raise exceptions.LoxiLBOperationException(
                operation="update_member",
                resource_type="member",
                resource_id=member_id,
                reason=str(e),
            )

    def delete(self, member, pool=None, loadbalancer=None):
        """Delete a member with zero-downtime endpoint API operations.

        Enhanced deletion that prioritizes endpoint API operations over service
        recreation to eliminate unnecessary service outages during member removal.

        Args:
            member: The member object from Octavia
            pool: The pool object from database
            loadbalancer: The loadbalancer object from database

        Returns:
            dict: Status information for Octavia
        """
        member_id = extract_member_attr(member, "id") or extract_member_attr(member, "member_id")
        address = extract_member_attr(member, "address") or extract_member_attr(member, "ip_address")
        protocol_port = extract_member_attr(member, "protocol_port")
        LOG.info("Deleting member %s with zero-downtime endpoint operation", member_id) # member_id: 78566868-a474-403e-a23f-54d3f568b862: member-78566868-a474-403e-a23f-54d3f568b862
        try:
            # Step 1: Get member mapping and metadata
            member_mapping_key = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, member_id
            )
            member_metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache, member_id
            )
            if not member_mapping_key:
                LOG.info("No mapping found for member %s, it may already be deleted", member_id)
                return member_id
            # Step 2: Coordinate with health monitor driver to remove endpoint probes
            pool_id = member_metadata.get("pool_id") if member_metadata else None
            if pool_id:
                try:
                    self._cleanup_health_monitor_endpoints(pool_id, address, protocol_port)
                except Exception as e:
                    LOG.warning("Failed to cleanup health monitor endpoints for member %s: %s", member_id, e)
            # # Step 3: Try zero-downtime endpoint deletion first
            # try:
            #     # FIXME: No meaning of loxilb endpoint API. It's used just endpointg monitoring.
            #     endpoint_deleted = self._delete_member_via_endpoint_api(member, member_mapping_key)
            #     if endpoint_deleted:
            #         LOG.info("Successfully deleted member %s via endpoint API (zero-downtime)", member_id)
            #         utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, member_id)
            #         return member_id                

            # except Exception as e:
            #     LOG.warning("Endpoint API deletion failed for member %s: %s", member_id, e)
            #     LOG.info("Falling back to service recreation method")
            # Step 4: Fallback to service recreation method
            if pool_id:
                try:
                    LOG.warning("Using service recreation for member %s deletion (brief downtime)", member_id)
                    self._update_pool_service_for_member_change(member, removing_member=True)
                    LOG.info("Removed member %s endpoint from LoxiLB service via recreation", member_id)
                except Exception as e:
                    LOG.warning("Failed to remove member %s from LoxiLB service: %s", member_id, e)
            # Step 5: Remove ID mapping and clean up references
            utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, member_id)
            LOG.info("Successfully deleted member %s", member_id)
            return member_id
        except Exception as e:
            LOG.error("Failed to delete member %s: %s", member_id, e)
            utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, member_id)
            return member_id

    def get(self, member_id):
        """Get member information.

        Retrieves member information from stored metadata since members are not
        standalone resources in LoxiLB.

        Args:
            member_id: UUID of the member

        Returns:
            dict: Member information in Octavia format

        Raises:
            LoxiLBResourceNotFoundException: If member is not found
        """
        LOG.debug("Getting member %s", member_id)

        try:
            # Step 1: Get member mapping
            member_mapping_key = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, member_id
            )

            if not member_mapping_key:
                raise exceptions.LoxiLBResourceNotFoundException(
                    resource_type="member",
                    resource_id=member_id,
                    endpoint="metadata_storage"
                )

            # Step 2: Get member metadata
            metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache, member_id
            )

            if not metadata:
                raise exceptions.LoxiLBResourceNotFoundException(
                    resource_type="member",
                    resource_id=member_id,
                    endpoint="metadata_storage"
                )

            # Step 3: Convert metadata to Octavia format
            member_data = {
                "id": member_id,
                "name": metadata.get("member_name", f"member-{member_id[:8]}"),
                "address": metadata.get("address"),
                "protocol_port": metadata.get("protocol_port"),
                "weight": metadata.get("weight", 1),
                "admin_state_up": metadata.get("admin_state_up", True),
                "operating_status": lib_consts.ONLINE if metadata.get("admin_state_up", True) else lib_consts.OFFLINE,
                "provisioning_status": lib_consts.ACTIVE,
                "monitor_address": metadata.get("monitor_address"),
                "monitor_port": metadata.get("monitor_port"),
                "subnet_id": metadata.get("subnet_id"),
                "pool_id": metadata.get("pool_id"),
                "backup": metadata.get("backup", False),
                "created_at": metadata.get("created_at"),
                "updated_at": metadata.get("updated_at"),
                "project_id": None,  # Not available - would need OpenStack context
            }

            return member_data

        except Exception as e:
            LOG.error("Failed to get member %s: %s", member_id, e)
            raise

    def get_all(self):
        """Get all members managed by this driver.

        Returns:
            list: List of member dictionaries in Octavia format
        """
        LOG.debug("Getting all members")

        try:
            members = []

            # Get all member mappings from cache
            for octavia_id, loxilb_key in self.resource_mapper.id_mapping_cache["octavia_to_loxilb"].items():
                metadata = utils.get_id_mapping_metadata(
                    self.resource_mapper.id_mapping_cache, octavia_id
                )
                
                # Only process member mappings
                if metadata.get("resource_type") == "member":
                    try:
                        member_data = self.get(octavia_id)
                        members.append(member_data)
                    except exceptions.LoxiLBResourceNotFoundException:
                        LOG.warning("Member %s mapping exists but metadata not found", octavia_id)
                        # Clean up orphaned mapping
                        utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, octavia_id)

            return members

        except Exception as e:
            LOG.error("Failed to get all members: %s", e)
            return []

    # Helper methods

    def _validate_member_config(self, member):
        """Validate member configuration.
        
        Args:
            member: Member object to validate
            
        Raises:
            LoxiLBValidationException: If validation fails
        """
        
        errors = []
        member_id = extract_member_attr(member, "id") or extract_member_attr(member, "member_id")
        address = extract_member_attr(member, "address") or extract_member_attr(member, "ip_address")
        protocol_port = extract_member_attr(member, "protocol_port")
        weight = extract_member_attr(member, "weight", 1)
        monitor_port = extract_member_attr(member, "monitor_port")
        # Required fields
        if not member_id:
            errors.append("Member ID is required")
        if not address:
            errors.append("Member address is required")
        if not protocol_port:
            errors.append("Member protocol port is required")
        # Validate IP address format
        if address:
            import ipaddress
            try:
                ipaddress.ip_address(address)
            except ValueError:
                errors.append(f"Invalid IP address format: {address}")
        # Validate port range
        if protocol_port and not (1 <= protocol_port <= 65535):
            errors.append(f"Protocol port must be between 1 and 65535, got: {protocol_port}")
        # Validate weight
        if weight and not (0 <= weight <= 256):
            errors.append(f"Weight must be between 0 and 256, got: {weight}")
        # Validate monitor port if provided
        if monitor_port and not (1 <= monitor_port <= 65535):
            errors.append(f"Monitor port must be between 1 and 65535, got: {monitor_port}")
        if errors:
            raise exceptions.LoxiLBValidationException(
                resource_type="member",
                validation_errors=errors
            )

    def _update_member_metadata(self, member_id, updates):
        """Update member metadata with timestamp tracking.
        
        Args:
            member_id: Member UUID
            updates: Dictionary of updates to apply to metadata
        """
        # Get existing metadata
        metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, member_id
        )
        
        if metadata:
            # Get the LoxiLB key for this member
            loxilb_key = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, member_id
            )
            
            # Update metadata with new values and timestamp
            updated_metadata = {**metadata, **updates, "updated_at": time.time()}
            
            # Store updated metadata
            utils.store_id_mapping(
                self.resource_mapper.id_mapping_cache,
                member_id,
                loxilb_key,
                "member",
                updated_metadata
            )

    def _update_pool_service_for_member_change(self, member, removing_member=False):
        """Update the LoxiLB service when member configuration changes.
        
        Args:
            member: Member object with current configuration
            removing_member: Boolean indicating if member is being removed
        """
        member_id = extract_member_attr(member, "id")
        if not member_id:
            LOG.debug("Member %s has no associated member, skipping service update", member_id)
            return

        # Get pool mapping to find the listener
        member_mapping = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, member_id
        )

        if not member_mapping:
            LOG.warning("No member mapping found for member %s, cannot update service", member_id)
            return

        # Get member metadata
        member_metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, member_id
        )

        # Get pool metadata
        pool_id = member_metadata.get("pool_id")
        
        pool_metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, pool_id
        )

        if not pool_metadata:
            LOG.warning("No pool metadata found for pool %s", pool_id)
            return
        else:
            LOG.info("Using pool metadata for pool %s: %s", pool_id, pool_metadata)

        # Fix: Check for listeners list, fallback to listener_id
        listener_id = pool_metadata.get("listener_id")
        
        if not listener_id:
            LOG.warning("No listener ID found in pool metadata for pool %s", pool_id)
            return
        else :
            LOG.info("Using listener ID %s from pool metadata for pool %s", listener_id, pool_id)

        # Get listener mapping and metadata
        listener_mapping = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, listener_id
        )

        if not listener_mapping:
            LOG.warning("No listener mapping found for listener %s", listener_id)
            return

        listener_metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, listener_id
        )

        if not listener_metadata:
            LOG.warning("No listener metadata found for listener %s", listener_id)
            return

        loadbalancer_id = listener_metadata.get("lb_id")
        
        if not loadbalancer_id:
            LOG.warning("No loadbalancer ID found in listener metadata for listener %s", listener_id)
            return
        LOG.info("Using loadbalancer ID %s from listener metadata for listener %s", 
                 loadbalancer_id, listener_id)

        loadbalancer_metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, loadbalancer_id
        )

        if not loadbalancer_metadata:
            LOG.warning("No loadbalancer metadata found for loadbalancer %s", loadbalancer_id)
            return  
        
        LOG.info("Using loadbalancer metadata for loadbalancer %s: %s", loadbalancer_id, loadbalancer_metadata)        

        try:
            # Get all active members for the pool
            pool_members = self._get_active_pool_members(pool_id)
            
            # If removing a member, exclude it from the list
            if removing_member:
                pool_members = [m for m in pool_members if extract_member_attr(m, "id") != extract_member_attr(member, "id")]
            else:
                # Add/update the current member in the list
                existing_member_index = None
                for i, m in enumerate(pool_members):
                    if extract_member_attr(m, "id") == extract_member_attr(member, "id"):
                        existing_member_index = i
                        break
                
                if existing_member_index is not None:
                    pool_members[existing_member_index] = member
                else:
                    pool_members.append(member)

            # Reconstruct the LoxiLB configuration with updated members
            loadbalancer = {
                "id": listener_metadata.get("lb_id"),
                "vip": {"ip_address": loadbalancer_metadata.get("external_ip")}
            }

            pool_config = {
                "id": pool_id,
                "lb_algorithm": pool_metadata.get("lb_algorithm", "ROUND_ROBIN"),
                "protocol": pool_metadata.get("protocol", "HTTP"),
                "members": pool_members
            }

            listener = {
                "id": listener_id,
                "protocol": listener_metadata.get("protocol", "HTTP").upper(),
                "protocol_port": listener_metadata.get("port"),
                "default_pool": pool_config
            }

            # Generate updated LoxiLB configuration
            loxilb_config = self.resource_mapper.loadbalancer_to_loxilb(
                loadbalancer, listener, pool_config
            )

            # Update or delete the service in LoxiLB depending on pool_members
            # FIXME: After test
            if len(pool_members) < 1:
                LOG.info("No members left in pool %s, deleting loadbalancer %s", pool_id, 
                         loadbalancer.get("id"))
                self.api_client.delete_loadbalancer_rule(
                    loadbalancer_metadata.get("external_ip"),
                    loadbalancer_metadata.get("port"),
                    loadbalancer_metadata.get("protocol"),
                    loadbalancer.get("id")
                )
            else:
                self.api_client.create_loadbalancer(loxilb_config)
            
            LOG.info("Successfully updated LoxiLB service for member %s changes", pool_id)

        except Exception as e:
            LOG.error("Failed to update LoxiLB service for member %s: %s", pool_id, e)
            raise exceptions.LoxiLBOperationException(
                operation="update_service_for_member",
                resource_type="member",
                resource_id=pool_id,
                reason=str(e)
            )

    def _get_active_pool_members(self, pool_id):
        """Get all active members for a given pool.
        
        Args:
            pool_id: Pool UUID
            
        Returns:
            list: List of active member dictionaries
        """
        members = []
        
        # Get all member mappings from cache
        for octavia_id, loxilb_key in self.resource_mapper.id_mapping_cache["octavia_to_loxilb"].items():
            metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache, octavia_id
            )
            
            # Only process member mappings for this pool
            if (metadata.get("resource_type") == "member" and 
                metadata.get("pool_id") == pool_id and
                metadata.get("admin_state_up", True)):
                
                member_data = {
                    "id": octavia_id,
                    "address": metadata.get("address"),
                    "protocol_port": metadata.get("protocol_port"),
                    "weight": metadata.get("weight", 1),
                    "admin_state_up": metadata.get("admin_state_up", True),
                    "backup": metadata.get("backup", False)
                }
                members.append(member_data)
        
        return members

    def _delete_member_via_endpoint_api(self, member, member_mapping_key):
        """Delete member using LoxiLB endpoint API for zero-downtime operation.
        
        This method uses the endpoint API to remove a member without affecting
        the entire service, eliminating unnecessary downtime.
        
        Args:
            member: The member object from Octavia
            member_mapping_key: LoxiLB key for the member
            
        Returns:
            bool: True if successfully deleted via endpoint API
            
        Raises:
            Exception: If endpoint API deletion fails
        """
        member_id = extract_member_attr(member, "id") or extract_member_attr(member, "member_id")
        member_address = extract_member_attr(member, "address") or extract_member_attr(member, "ip_address")
        member_port = extract_member_attr(member, "protocol_port")
        
        try:
            # Construct endpoint key from member mapping
            # Format: service_key:member_address:member_port
            # member_mapping_key == member-78566868-a474-403e-a23f-54d3f568b862
            # member_id == 78566868-a474-403e-a23f-54d3f568b862
            parts = member_mapping_key.split(":")
            if len(parts) >= 5:
                # Extract endpoint identifier
                endpoint_ip = parts[3]  # member address
                endpoint_port = parts[4]  # member port
                
                # Verify this matches the member we're deleting
                if endpoint_ip == member_address and int(endpoint_port) == member_port:
                    # Use endpoint API to delete this specific endpoint
                    endpoint_key = f"{endpoint_ip}:{endpoint_port}"
                    
                    # Check if endpoint exists first
                    endpoints = self.api_client.get_endpoints()
                    endpoint_exists = any(
                        ep.get("endpointIP") == endpoint_ip and 
                        ep.get("targetPort") == endpoint_port 
                        for ep in endpoints
                    )
                    
                    if endpoint_exists:
                        # Delete the endpoint
                        self.api_client.delete_endpoint(endpoint_key)
                        LOG.info("Successfully deleted endpoint %s for member %s", 
                                endpoint_key, member_id)
                        return True
                    else:
                        LOG.info("Endpoint %s for member %s already deleted", 
                                endpoint_key, member_id)
                        return True
                else:
                    LOG.warning("Member mapping key mismatch for member %s", member_id)
                    return False
            else:
                LOG.warning("Invalid member mapping key format for member %s: %s", 
                           member_id, member_mapping_key)
                return False
                
        except Exception as e:
            LOG.error("Endpoint API deletion failed for member %s: %s", member_id, e)
            raise

    def _cleanup_health_monitor_endpoints(self, pool_id, member_address, member_port):
        """Clean up health monitor endpoint probes for a deleted member.
        
        This method coordinates with the health monitor driver to ensure that
        when a member is deleted, any associated health monitoring endpoints
        are also properly removed.
        
        Args:
            pool_id: Pool UUID that the member belonged to
            member_address: IP address of the deleted member
            member_port: Port of the deleted member
        """
        try:
            # Import health monitor driver here to avoid circular imports
            try:
                from octavia_loxilb_driver.driver.healthmonitor_driver import HealthMonitorDriver
            except ImportError as ie:
                LOG.error("Failed to import HealthMonitorDriver in member_driver.py: %s", ie)
                return
            except Exception as e:
                LOG.error("Unexpected error importing HealthMonitorDriver: %s", e)
                return
            # Create a health monitor driver instance with the same configuration
            health_monitor_driver = HealthMonitorDriver(
                self.api_client, 
                self.resource_mapper, 
                self.config
            )
            # Call the health monitor driver to remove endpoint probes for this member
            probe_removed = health_monitor_driver.remove_member_endpoint_probe(
                pool_id, member_address, member_port
            )
            if probe_removed:
                LOG.info("Successfully cleaned up health monitor endpoint probes for member %s:%s", 
                        member_address, member_port)
            else:
                LOG.debug("No health monitor endpoint probes found for member %s:%s", 
                         member_address, member_port)
        except Exception as e:
            LOG.error("Failed to cleanup health monitor endpoints for member %s:%s: %s", 
                     member_address, member_port, e)
            # Don't raise - this is cleanup and shouldn't prevent member deletion
