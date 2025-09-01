# octavia_loxilb_driver/driver/pool_driver.py
"""Pool Management Driver for LoxiLB."""

import time
import pprint

from octavia_lib.common import constants as lib_consts
from oslo_log import log as logging

from octavia_loxilb_driver.common import exceptions, utils
from octavia_loxilb_driver.driver.utils import type_utils

LOG = logging.getLogger(__name__)

# General-purpose attribute extraction function
def extract_attr(obj, key, default=None):
    """Safely extract attribute from dict or object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

class PoolDriver:
    """
    Pool Management Driver for LoxiLB.

    This driver is now stateless and expects all resource relationships and metadata
    (listener, loadbalancer, etc.) to be passed explicitly via method arguments.
    The controller/worker is responsible for managing all resource relationships,
    collecting necessary context, and passing it to the driver. Direct access to
    resource mapping cache is deprecated and will be removed in future cleanups.

    Methods:
        create(pool, listener_metadata, loadbalancer_metadata):
            Create a pool. Requires all necessary metadata/context to be passed.
        update(old_pool, pool_updates, listener_metadata, loadbalancer_metadata):
            Update a pool. Requires all necessary metadata/context to be passed.
        delete(pool, listener_metadata, loadbalancer_metadata):
            Delete a pool. Requires all necessary metadata/context to be passed.
        _update_listener_service_for_pool(pool, listener_metadata, loadbalancer_metadata):
            Internal helper to update LoxiLB service. Requires explicit metadata.
    """

    def __init__(self, api_client, resource_mapper, config):
        """Initialize the PoolDriver.
        
        Args:
            api_client: LoxiLB API client instance
            resource_mapper: Resource mapper with ID mapping capabilities
            config: Driver configuration object
        """
        self.api_client = api_client
        self.resource_mapper = resource_mapper
        self.config = config

    def create(self, pool, listener_metadata=None, loadbalancer_metadata=None):
        """
        Create a pool.

        This method is stateless. All required context (listener/loadbalancer metadata)
        must be passed by the controller/worker. Direct cache access is deprecated.

        Args:
            pool: The pool object from Octavia
            listener_metadata: Metadata for the associated listener (dict, required if pool references a listener)
            loadbalancer_metadata: Metadata for the associated loadbalancer (dict, required if pool references a loadbalancer)

        Returns:
            dict: Status information for Octavia

        Raises:
            LoxiLBOperationException: If the pool creation fails
            LoxiLBValidationException: If the pool configuration is invalid
        """
        # Use type_utils to handle both dictionary and object types
        pool_id = type_utils.get_id(pool, id_attr="id", fallback_attrs=["pool_id"])
        lb_algorithm = type_utils.get_attribute(pool, "lb_algorithm", "ROUND_ROBIN")
            
        LOG.info("Creating pool %s with algorithm %s", 
                pool_id, 
                lb_algorithm)

        # Debug log to print full pool attributes
        pool_attrs = extract_attr(pool, "__dict__", pool) if not isinstance(pool, dict) else pool
        LOG.debug("Pool input attributes:\n%s", pprint.pformat(pool_attrs))
        LOG.debug("Listener metadata: %s", pprint.pformat(listener_metadata))
        LOG.debug("Loadbalancer metadata: %s", pprint.pformat(loadbalancer_metadata))

        try:
            # Step 1: Validate pool configuration
            self._validate_pool_config(pool)

            # Step 2: Check if pool already exists to prevent conflicts
            existing_mapping = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, pool_id
            )
            
            if existing_mapping:
                LOG.warning("Pool %s already has mapping %s, updating instead", 
                           pool_id, existing_mapping)
                return self.update(pool, {})

            # Step 3: Generate pool identifier for mapping
            # Pools don't have direct LoxiLB equivalents, so we use the pool ID as the key
            pool_mapping_key = f"pool-{pool_id}"

            # Step 4: Extract pool attributes based on type
            # Debug log to print full pool attributes


            # Use type_utils to extract all pool attributes
            name = type_utils.get_attribute(pool, "name")
            description = type_utils.get_attribute(pool, "description")
            protocol = type_utils.get_attribute(pool, "protocol", "HTTP")
            session_persistence = type_utils.get_attribute(pool, "session_persistence")
            admin_state_up = type_utils.get_attribute(pool, "admin_state_up", True)
            listener_id = type_utils.get_attribute(pool, "listener_id")
            # Flexible extraction for listener_id
            if not listener_id and listener_metadata:
                listener_id = extract_attr(listener_metadata, "id")
            loadbalancer_id = type_utils.get_attribute(pool, "loadbalancer_id")
            # Flexible extraction for loadbalancer_id
            if not loadbalancer_id and loadbalancer_metadata:
                loadbalancer_id = extract_attr(loadbalancer_metadata, "id")
            members = type_utils.get_attribute(pool, "members", []) or []
                
            # Store pool configuration in metadata for later use
            utils.store_id_mapping(
                self.resource_mapper.id_mapping_cache,
                pool_id,
                pool_mapping_key,
                "pool",
                {
                    "pool_name": name,
                    "pool_description": description,
                    "lb_algorithm": lb_algorithm,
                    "protocol": protocol,
                    "session_persistence": session_persistence,
                    "admin_state_up": admin_state_up,
                    "listener_id": listener_id,
                    "loadbalancer_id": loadbalancer_id,
                    "members": members,
                    "created_by": "pool_driver"
                }
            )

            # Step 5: If pool is associated with an existing listener, update the LoxiLB service
            has_listener = bool(type_utils.get_attribute(pool, "listener_id"))
            listener_update_failed = False
            if has_listener and listener_metadata and loadbalancer_metadata:
                try:
                    self._update_listener_service_for_pool(pool, listener_metadata, loadbalancer_metadata)
                except Exception as e:
                    LOG.warning("Failed to update listener service for new pool %s: %s", pool_id, e)
                    listener_update_failed = True
                    
            # Ensure pool metadata is updated to reflect the pool is active, even if listener update failed
            self._update_pool_metadata(pool_id, {"status": lib_consts.ACTIVE})
            
            if listener_update_failed:
                LOG.info("Pool %s created successfully but listener service update failed. Pool is still marked as ACTIVE.", pool_id)

            LOG.info("Successfully created pool %s", pool_id)

            # Step 6: Return status information to Octavia
            # Get admin_state_up based on type
            admin_state_up = type_utils.get_attribute(pool, "admin_state_up", True)
                
            return {
                "status": {
                    "id": pool_id,
                    "provisioning_status": lib_consts.ACTIVE,
                    "operating_status": lib_consts.ONLINE if admin_state_up else lib_consts.OFFLINE
                }
            }

        except exceptions.LoxiLBValidationException:
            # Re-raise validation exceptions as-is
            raise
        except Exception as e:
            LOG.error("Failed to create pool %s: %s", pool_id, e)
            raise exceptions.LoxiLBOperationException(
                operation="create_pool",
                resource_type="pool",
                resource_id=pool_id,
                reason=str(e),
            )

    def update(self, old_pool, pool_updates, listener_metadata=None, loadbalancer_metadata=None):
        """
        Update a pool.

        This method is stateless. All required context (listener/loadbalancer metadata)
        must be passed by the controller/worker. Direct cache access is deprecated.

        Args:
            old_pool: The pool object or dictionary before the update
            pool_updates: Dictionary with the changed attributes
            listener_metadata: Metadata for the associated listener (dict, required if pool references a listener)
            loadbalancer_metadata: Metadata for the associated loadbalancer (dict, required if pool references a loadbalancer)

        Returns:
            dict: Status information for Octavia

        Raises:
            LoxiLBOperationException: If the pool update fails
        """
        # Use type_utils to handle both dictionary and object types
        pool_id = type_utils.get_id(old_pool, id_attr="id", fallback_attrs=["pool_id"])
            
        LOG.info("Updating pool %s with changes: %s", pool_id, pool_updates.keys())

        try:
            # Remove direct cache access: controller/worker must pass listener/loadbalancer metadata
            # TODO: Remove metadata storage when controller/worker fully manages state
            current_metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache, pool_id
            )
            if not current_metadata:
                LOG.warning("No ID mapping found for pool %s during update", pool_id)
                # Create the pool if it doesn't exist
                # Merge old_pool with updates for creation
                if isinstance(old_pool, dict):
                    new_pool = {**old_pool, **pool_updates}
                else:
                    # Convert object to dict and apply updates using extract_attr
                    new_pool = {}
                    for attr in dir(old_pool):
                        if not attr.startswith('_') and not callable(extract_attr(old_pool, attr)):
                            new_pool[attr] = extract_attr(old_pool, attr)
                    new_pool.update(pool_updates)
                return self.create(new_pool, listener_metadata, loadbalancer_metadata)

            # Step 2: Get current metadata
            # current_metadata = utils.get_id_mapping_metadata(
            #     self.resource_mapper.id_mapping_cache, pool_id
            # )

            # Step 3: Handle admin state changes
            if "admin_state_up" in pool_updates:
                admin_state = pool_updates["admin_state_up"]
                if not admin_state:
                    LOG.info("Disabling pool %s", pool_id)
                    # Update metadata to reflect disabled state
                    self._update_pool_metadata(pool_id, {"admin_state_up": False})
                    
                    # Update any associated listener services
                    if current_metadata.get("listener_id") and listener_metadata and loadbalancer_metadata:
                        try:
                            self._update_listener_service_for_pool({**old_pool, **pool_updates}, listener_metadata, loadbalancer_metadata)
                        except Exception as e:
                            LOG.warning("Failed to update listener for disabled pool %s: %s", pool_id, e)
                    
                    return {
                        "status": {
                            "id": pool_id,
                            "provisioning_status": lib_consts.ACTIVE,
                            "operating_status": lib_consts.OFFLINE
                        }
                    }

            # Step 4: Handle configuration updates
            updated_metadata = {**current_metadata}
            
            # Update metadata with new values
            for key, value in pool_updates.items():
                if key in ["name", "description", "lb_algorithm", "protocol", "session_persistence", "admin_state_up"]:
                    metadata_key = f"pool_{key}" if key in ["name", "description"] else key
                    updated_metadata[metadata_key] = value

            # Store updated metadata
            self._update_pool_metadata(pool_id, updated_metadata)

            # Step 5: Update any associated LoxiLB services
            updated_pool = {**old_pool, **pool_updates}
            if current_metadata.get("listener_id") and listener_metadata and loadbalancer_metadata:
                try:
                    self._update_listener_service_for_pool(updated_pool, listener_metadata, loadbalancer_metadata)
                    LOG.info("Updated LoxiLB service for pool %s changes", pool_id)
                except Exception as e:
                    LOG.warning("Failed to update listener service for pool %s: %s", pool_id, e)

            LOG.info("Successfully updated pool %s", pool_id)

            # Step 6: Return status information to Octavia
            # Get admin_state_up based on type
            admin_state_up = type_utils.get_attribute(updated_pool, "admin_state_up", True)
                
            return {
                "status": {
                    "id": pool_id,
                    "provisioning_status": lib_consts.ACTIVE,
                    "operating_status": lib_consts.ONLINE if admin_state_up else lib_consts.OFFLINE
                }
            }

        except Exception as e:
            LOG.error("Failed to update pool %s: %s", pool_id, e)
            raise exceptions.LoxiLBOperationException(
                operation="update_pool",
                resource_type="pool",
                resource_id=pool_id,
                reason=str(e),
            )

    def delete(self, pool, listener_metadata=None, loadbalancer_metadata=None):
        """
        Delete a pool.

        This method is stateless. All required context (listener/loadbalancer metadata)
        must be passed by the controller/worker. Direct cache access is deprecated.

        Args:
            pool: The pool object or dictionary from Octavia
            listener_metadata: Metadata for the associated listener (dict, required if pool references a listener)
            loadbalancer_metadata: Metadata for the associated loadbalancer (dict, required if pool references a loadbalancer)

        Returns:
            dict: Status information for Octavia
        """
        # Use type_utils to handle both dictionary and object types
        pool_id = type_utils.get_id(pool, id_attr="id", fallback_attrs=["pool_id"])
            
        LOG.info("Deleting pool %s", pool_id)

        try:
            metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache, pool_id
            )
            # If the pool is associated with a listener, clear the listener's default_pool_id
            listener_id = metadata.get("listener_id") if metadata else None
            if listener_id:
                # Attempt to clear default_pool_id in DB
                from octavia.db import api as db_apis
                from octavia.db import repositories as repo
                session = db_apis.get_session()
                listener_repo = repo.ListenerRepository()
                listener = listener_repo.get(session, id=listener_id)
                if listener and getattr(listener, "default_pool_id", None) == pool_id:
                    listener_repo.update(session, listener_id, default_pool_id=None)
                    LOG.info("Cleared default_pool_id for listener %s after pool %s deletion", listener_id, pool_id)
            if not metadata:
                LOG.info("No mapping found for pool %s, it may already be deleted", pool_id)
                return {
                    "status": {
                        "id": pool_id,
                        "provisioning_status": lib_consts.DELETED,
                        "operating_status": lib_consts.OFFLINE
                    }
                }
            if metadata.get("listener_id") and listener_metadata and loadbalancer_metadata:
                try:
                    empty_pool = {**pool, "members": []}
                    self._update_listener_service_for_pool(empty_pool, listener_metadata, loadbalancer_metadata)
                    LOG.info("Cleared pool %s endpoints from LoxiLB service", pool_id)
                except Exception as e:
                    LOG.warning("Failed to clear pool %s from LoxiLB service: %s", pool_id, e)
            utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, pool_id)
            LOG.info("Successfully deleted pool %s", pool_id)
            return {
                "status": {
                    "id": pool_id,
                    "provisioning_status": lib_consts.DELETED,
                    "operating_status": lib_consts.OFFLINE
                }
            }
        except Exception as e:
            LOG.error("Failed to delete pool %s: %s", pool_id, e)
            utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, pool_id)
            return {
                "status": {
                    "id": pool_id,
                    "provisioning_status": lib_consts.ERROR,
                    "operating_status": lib_consts.OFFLINE
                }
            }

    def get(self, pool_id):
        """Get pool information.

        Retrieves pool information from stored metadata since pools are not
        standalone resources in LoxiLB.

        Args:
            pool_id: UUID of the pool

        Returns:
            dict: Pool information in Octavia format

        Raises:
            LoxiLBResourceNotFoundException: If pool is not found
        """
        LOG.debug("Getting pool %s", pool_id)

        try:
            # Step 1: Get pool mapping
            pool_mapping_key = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, pool_id
            )

            if not pool_mapping_key:
                raise exceptions.LoxiLBResourceNotFoundException(
                    resource_type="pool",
                    resource_id=pool_id,
                    endpoint="metadata_storage"
                )

            # Step 2: Get pool metadata
            metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache, pool_id
            )

            if not metadata:
                raise exceptions.LoxiLBResourceNotFoundException(
                    resource_type="pool",
                    resource_id=pool_id,
                    endpoint="metadata_storage"
                )

            # Step 3: Convert metadata to Octavia format
            pool_data = {
                "id": pool_id,
                "name": metadata.get("pool_name", f"pool-{pool_id[:8]}"),
                "description": metadata.get("pool_description", ""),
                "lb_algorithm": metadata.get("lb_algorithm", "ROUND_ROBIN"),
                "protocol": metadata.get("protocol", "HTTP"),
                "session_persistence": metadata.get("session_persistence"),
                "admin_state_up": metadata.get("admin_state_up", True),
                "operating_status": lib_consts.ONLINE if metadata.get("admin_state_up", True) else lib_consts.OFFLINE,
                "provisioning_status": lib_consts.ACTIVE,
                "created_at": metadata.get("created_at"),
                "updated_at": metadata.get("updated_at"),
                "project_id": None,  # Not available - would need OpenStack context
                "listener_id": metadata.get("listener_id"),
                "loadbalancer_id": metadata.get("loadbalancer_id"),
                "members": metadata.get("members", []),
                "health_monitor_id": metadata.get("health_monitor_id"),
            }

            return pool_data

        except Exception as e:
            LOG.error("Failed to get pool %s: %s", pool_id, e)
            raise

    def get_all(self):
        """Get all pools managed by this driver.

        Returns:
            list: List of pool dictionaries in Octavia format
        """
        LOG.debug("Getting all pools")

        try:
            pools = []

            # Get all pool mappings from cache
            for octavia_id, loxilb_key in self.resource_mapper.id_mapping_cache["octavia_to_loxilb"].items():
                metadata = utils.get_id_mapping_metadata(
                    self.resource_mapper.id_mapping_cache, octavia_id
                )
                
                # Only process pool mappings
                if metadata.get("resource_type") == "pool":
                    try:
                        pool_data = self.get(octavia_id)
                        pools.append(pool_data)
                    except exceptions.LoxiLBResourceNotFoundException:
                        LOG.warning("Pool %s mapping exists but metadata not found", octavia_id)
                        # Clean up orphaned mapping
                        utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, octavia_id)

            return pools

        except Exception as e:
            LOG.error("Failed to get all pools: %s", e)
            return []

    # Helper methods

    def _extract_session_persistence(self, pool):
        """Extract session persistence configuration from pool.
        
        Args:
            pool: Pool object or dictionary
            
        Returns:
            dict: Session persistence configuration or None
        """
        return type_utils.get_attribute(pool, "session_persistence")

    def _validate_pool_config(self, pool):
        """Validate pool configuration.
        
        Args:
            pool: Pool object or dictionary to validate
            
        Raises:
            LoxiLBValidationException: If validation fails
        """
        errors = []

        # Use type_utils to handle both dictionary and object types
        pool_id = type_utils.get_id(pool, id_attr="id", fallback_attrs=["pool_id"])
        protocol = type_utils.get_attribute(pool, "protocol")
        protocol_str = type_utils.get_attribute(pool, "protocol", "").upper() if protocol else ""
        lb_algorithm = type_utils.get_attribute(pool, "lb_algorithm", "ROUND_ROBIN")
            
        # Debug log to help diagnose ID issues
        LOG.debug("Validating pool with ID: %s", pool_id)
            
        # Required fields validation
        if not pool_id:
            # If we're in create mode, the pool ID should be provided by Octavia
            # Log more details about the pool object to help diagnose
            if not isinstance(pool, dict):
                LOG.error("Pool object missing ID. Pool attributes: %s", 
                          ", ".join([attr for attr in dir(pool) 
                                    if not attr.startswith('_') and not callable(getattr(pool, attr))]))
            errors.append("Pool ID is required")

        if not protocol:
            errors.append("Pool protocol is required")

        # Validate protocol
        supported_protocols = ["HTTP", "HTTPS", "TCP", "UDP", "SCTP"]
        if protocol_str not in supported_protocols:
            errors.append(f"Unsupported pool protocol: {protocol_str}")

        # Validate load balancing algorithm
        # Octavia standard algorithms
        octavia_algorithms = ["ROUND_ROBIN", "LEAST_CONNECTIONS", "SOURCE_IP", "SOURCE_IP_PORT"]
        # LoxiLB extended algorithms (for advanced use cases)
        loxilb_extended_algorithms = ["PRIORITY"]
        supported_algorithms = octavia_algorithms + loxilb_extended_algorithms
        
        if lb_algorithm not in supported_algorithms:
            errors.append(f"Unsupported load balancing algorithm: {lb_algorithm}. "
                         f"Supported: {', '.join(supported_algorithms)}")

        # Validate session persistence if provided
        session_persistence = extract_attr(pool, "session_persistence")
            
        if session_persistence:
            # Handle both dict and object types for session_persistence
            persistence_type = extract_attr(session_persistence, "type")
                
            if persistence_type not in ["SOURCE_IP", "HTTP_COOKIE", "APP_COOKIE"]:
                errors.append(f"Unsupported session persistence type: {persistence_type}")

        if errors:
            raise exceptions.LoxiLBValidationException(
                resource_type="pool",
                validation_errors=errors
            )

    def _update_pool_metadata(self, pool_id, updates):
        """Update pool metadata with timestamp tracking.
        
        Args:
            pool_id: Pool UUID
            updates: Dictionary of updates to apply to metadata
        """
        # Get existing metadata
        metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, pool_id
        )
        
        if metadata:
            # Update metadata with new values and timestamp
            updated_metadata = {**metadata, **updates, "updated_at": time.time()}
            
            # Store updated metadata
            utils.store_id_mapping(
                self.resource_mapper.id_mapping_cache,
                pool_id,
                metadata.get("loxilb_key"),
                "pool",
                updated_metadata
            )

    def _update_listener_service_for_pool(self, pool, listener_metadata=None, loadbalancer_metadata=None):
        """
        Update the LoxiLB service when pool configuration changes.

        This method is stateless. All required context (listener/loadbalancer metadata)
        must be passed by the controller/worker. Direct cache access is deprecated.

        Args:
            pool: Pool object or dictionary with current configuration
            listener_metadata: Metadata for the associated listener (dict, required)
            loadbalancer_metadata: Metadata for the associated loadbalancer (dict, required)
        """
        pool_id = type_utils.get_id(pool, id_attr="id", fallback_attrs=["pool_id"])
        listener_id = type_utils.get_attribute(pool, "listener_id")
        
        if not listener_id:
            LOG.debug("Pool %s has no associated listener, skipping service update", pool_id)
            return
        if not listener_metadata or not loadbalancer_metadata:
            LOG.warning("Listener/loadbalancer metadata required for pool %s update", pool_id)
            return
        try:
            loadbalancer = {
                "id": extract_attr(loadbalancer_metadata, "id"),
                "vip": {"ip_address": extract_attr(loadbalancer_metadata, "vip_ip")}
            }
            pool_dict = pool if isinstance(pool, dict) else {attr: getattr(pool, attr) for attr in dir(pool) if not attr.startswith('_') and not callable(getattr(pool, attr))}
            listener = {
                "id": listener_id,
                "protocol": extract_attr(listener_metadata, "protocol", "HTTP").upper(),
                "protocol_port": extract_attr(listener_metadata, "port"),
                "default_pool": pool_dict
            }
            loxilb_config = self.resource_mapper.loadbalancer_to_loxilb(
                loadbalancer, listener, pool_dict
            )
            self.api_client.create_loadbalancer(loxilb_config)
            LOG.info("Successfully updated LoxiLB service for pool %s changes", pool_id)
        except Exception as e:
            LOG.error("Failed to update LoxiLB service for pool %s: %s", pool_id, e)
            raise exceptions.LoxiLBOperationException(
                operation="update_listener_for_pool",
                resource_type="pool",
                resource_id=pool_id,
                reason=str(e)
            )

    # TODO: Refactor create, update, delete to remove all cache access and require controller/worker to pass all needed metadata
