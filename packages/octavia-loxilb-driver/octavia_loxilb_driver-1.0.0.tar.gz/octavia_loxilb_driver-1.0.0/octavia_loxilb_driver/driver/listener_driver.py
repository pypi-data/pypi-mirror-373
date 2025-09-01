# octavia_loxilb_driver/driver/listener_driver.py
"""Enhanced Listener Management Driver for LoxiLB with State Reconciliation."""

import time

from octavia_lib.common import constants as lib_consts
from oslo_log import log as logging

from octavia_loxilb_driver.common import exceptions, utils
from octavia_loxilb_driver.common.state_reconciler import StateReconciler

LOG = logging.getLogger(__name__)

# General-purpose attribute extraction function
def extract_attr(obj, key, default=None):
    """Safely extract attribute from dict or object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

class ListenerDriver:
    """Enhanced Listener Management Driver for LoxiLB with State Reconciliation.
    
    This driver handles Octavia listener operations by managing LoxiLB load balancer
    services. It includes critical fixes for the architectural mismatch between
    Octavia's granular resource model and LoxiLB's composite service model.
    
    Key Features:
    - Cascade delete detection and reconciliation
    - State consistency validation
    - Comprehensive logging of architectural impacts
    - Automatic cleanup of orphaned resources
    """
    
    @staticmethod
    def get_loadbalancer(listener):
        """Extract loadbalancer from listener object or dict.
        
        Args:
            listener: Listener object or dict
            
        Returns:
            Loadbalancer object or dict with ID
        """
        # For dictionary type
        # Use extract_attr to get loadbalancer or loadbalancer_id
        loadbalancer = extract_attr(listener, "loadbalancer", None)
        if not loadbalancer:
            lb_id = extract_attr(listener, "loadbalancer_id", None)
            if lb_id:
                LOG.info("Creating loadbalancer dict from ID: %s", lb_id)
                loadbalancer = {"id": lb_id}

        if loadbalancer is None:            
            LOG.warning("No loadbalancer found in listener")

        return loadbalancer

    def __init__(self, api_client, resource_mapper, config):
        """Initialize the ListenerDriver.
        
        Args:
            api_client: LoxiLB API client instance
            resource_mapper: Resource mapper with ID mapping capabilities
            config: Driver configuration object
        """
        self.api_client = api_client
        self.resource_mapper = resource_mapper
        self.config = config
        # Initialize state reconciler for architectural mismatch handling
        self.state_reconciler = StateReconciler(resource_mapper, api_client)

    def create(self, listener, loadbalancer):
        """Create a listener.

        Creates a new listener by setting up a LoxiLB load balancer service.
        The listener defines the frontend (VIP, port, protocol) of the load balancer.

        Args:
            listener: The listener object from Octavia containing:
                - id: Listener UUID
                - protocol: HTTP/HTTPS/TCP/UDP/TERMINATED_HTTPS/PROXY
                - protocol_port: Port number (1-65535)
                - default_pool: Associated pool (optional)
                - admin_state_up: Administrative state
                - connection_limit: Maximum connections (-1 for unlimited)
                - default_tls_container_ref: TLS certificate reference
                - sni_container_refs: SNI certificate references
                - insert_headers: Headers to insert
                - name: Listener name
                - description: Listener description
            loadbalancer: The loadbalancer object from Octavia containing:
                - id: LoadBalancer UUID
                - vip: VIP object with ip_address

        Returns:
            dict: Status information for Octavia

        Raises:
            LoxiLBOperationException: If the listener creation fails
            LoxiLBValidationException: If the listener configuration is invalid
        """
        # Handle both dictionary and object types
        listener_id = extract_attr(listener, "id") or extract_attr(listener, "listener_id")
        protocol = extract_attr(listener, "protocol")
        protocol_port = extract_attr(listener, "protocol_port")
            
        LOG.info("Creating listener %s on protocol %s:%s", 
                listener_id, 
                protocol, 
                protocol_port)

        try:
            # Step 1: Validate listener configuration
            self._validate_listener_config(listener)

            # Step 2: Get the pool information (may be None for TCP listeners without pool)
            pool = extract_attr(listener, "default_pool", None)

            # Step 3: Generate deterministic ID and service key for tracking
            external_ip = self._get_vip_address(loadbalancer)
            port = extract_attr(listener, "protocol_port")
            protocol = extract_attr(listener, "protocol", "HTTP").upper()

            # Generate deterministic ID for LoxiLB service key
            loxilb_service_key = utils.get_loxilb_service_key(
                external_ip, port, utils.map_octavia_protocol_to_loxilb(protocol)
            )

            # Step 4: Check if listener already exists to prevent conflicts
            existing_mapping = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, listener_id
            )
            
            if existing_mapping:
                LOG.warning("Listener %s already has mapping %s, updating instead", 
                           listener_id, existing_mapping)
                # If listener exists, perform update operation instead
                return self.update(listener, {})

            # Step 5: Create LoxiLB load balancer service
            loxilb_lb_config = self.resource_mapper.loadbalancer_to_loxilb(
                loadbalancer, listener, pool
            )
            
            # Check if we're using a placeholder pool
            is_placeholder_pool = False
            if isinstance(pool, dict) and pool.get('is_placeholder', False):
                is_placeholder_pool = True
                LOG.info(f"Using placeholder pool configuration for listener {listener_id}")
                
                # For placeholder pools, we need to modify the LoxiLB config to create a valid service
                # that doesn't actually route traffic to any backends
                if 'serviceArguments' in loxilb_lb_config:
                    # Set the mode to 'dnat' which doesn't require real backends
                    loxilb_lb_config['serviceArguments']['mode'] = 'dnat'
                    
                    # Set a dummy endpoint that won't be used but satisfies the API requirements
                    if 'endpoints' not in loxilb_lb_config or not loxilb_lb_config.get('endpoints'):
                        loxilb_lb_config['endpoints'] = [{
                            'name': f'placeholder-endpoint-{listener_id}',
                            'ip': '127.0.0.1',  # Loopback address as placeholder
                            'port': 9999,       # Arbitrary port
                            'weight': 1
                        }]

            # Apply listener-specific configuration
            admin_state_up = extract_attr(listener, "admin_state_up", True)
            name = extract_attr(listener, "name", None)
            description = extract_attr(listener, "description", None)
            connection_limit = extract_attr(listener, "connection_limit", None)
            default_tls_container_ref = extract_attr(listener, "default_tls_container_ref", None)

            self._apply_listener_config(loxilb_lb_config, listener)

            # Step 7: Create the service in LoxiLB
            result = self.api_client.create_loadbalancer(loxilb_lb_config)

            # Step 8: Store ID mapping for future operations
            lb_id = extract_attr(loadbalancer, "id", None)
                
            self.resource_mapper.store_mapping(
                resource_type="listener",
                octavia_id=listener_id,
                loxilb_id=loxilb_service_key,
                metadata={
                    "lb_id": lb_id,
                    "protocol": protocol,
                    "port": port,
                    "created_at": time.time(),
                    "updated_at": time.time(),
                    "pool_id": None if (isinstance(pool, dict) and pool.get('is_placeholder', False)) else (pool.get("id") if pool else None),
                    "has_placeholder_pool": True if (isinstance(pool, dict) and pool.get('is_placeholder', False)) else False,
                    "service_name": loxilb_lb_config.get("serviceArguments", {}).get("name"),
                    "listener_name": name,
                    "listener_description": description,
                    "connection_limit": connection_limit,
                    "admin_state_up": admin_state_up,
                    "tls_container_ref": default_tls_container_ref,
                    "created_by": "listener_driver"
                }
            )

            LOG.info("Successfully created listener %s with LoxiLB service %s", 
                    listener_id, loxilb_service_key)
                    
            # Force save mappings to ensure persistence
            storage_path = self.resource_mapper.id_mapping_cache.get("_storage_path")
            if storage_path:
                success = utils.save_id_mappings_to_storage(self.resource_mapper.id_mapping_cache)
                if success:
                    LOG.debug("Successfully saved ID mappings after listener creation")
                else:
                    LOG.error("Failed to save ID mappings after listener creation")

            # Step 9: Return status information to Octavia
            return {
                "status": {
                    "id": listener_id,
                    "provisioning_status": lib_consts.ACTIVE,
                    "operating_status": lib_consts.ONLINE if admin_state_up else lib_consts.OFFLINE
                }
            }

        except exceptions.LoxiLBValidationException:
            # Re-raise validation exceptions as-is
            raise
        except Exception as e:
            LOG.error("Failed to create listener %s: %s", listener_id, e)
            raise exceptions.LoxiLBOperationException(
                operation="create_listener",
                resource_type="listener",
                resource_id=listener_id,
                reason=str(e),
            )

    def update(self, old_listener, listener_updates, loadbalancer):
        """Update a listener.

        Updates an existing listener by modifying the LoxiLB load balancer service.
        Handles various update scenarios including admin state changes, protocol
        changes, and configuration updates.

        Args:
            old_listener: The listener object before the update
            listener_updates: Dictionary with the changed attributes
            loadbalancer: The loadbalancer object from Octavia

        Returns:
            dict: Status information for Octavia

        Raises:
            LoxiLBOperationException: If the listener update fails
        """
        listener_id = old_listener.get("id") or old_listener.get("listener_id")
        LOG.info("Updating listener %s with changes: %s", listener_id, listener_updates.keys())

        try:
            # Step 1: Get existing LoxiLB service mapping
            loxilb_service_key = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, listener_id
            )

            if not loxilb_service_key:
                LOG.warning("No ID mapping found for listener %s during update", listener_id)
                # Try to recover mapping or treat as new creation
                if self._should_create_on_missing_mapping(old_listener, listener_updates):
                    return self.create({**old_listener, **listener_updates}, loadbalancer)
                else:
                    raise exceptions.LoxiLBResourceNotFoundException(
                        resource_type="listener",
                        resource_id=listener_id,
                        endpoint="LoxiLB"
                    )

            # Step 2: Handle admin state changes
            if "admin_state_up" in listener_updates:
                admin_state = listener_updates["admin_state_up"]
                if not admin_state:
                    # Disable listener by deleting the service
                    LOG.info("Disabling listener %s by deleting LoxiLB service", listener_id)
                    self.delete(old_listener, loadbalancer)
                    return {
                        "status": {
                            "id": listener_id,
                            "provisioning_status": lib_consts.ACTIVE,
                            "operating_status": lib_consts.OFFLINE
                        }
                    }
                else:
                    # Re-enable listener by recreating the service
                    LOG.info("Re-enabling listener %s", listener_id)
                    # Remove existing mapping and recreate
                    utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, listener_id)
                    return self.create({**old_listener, **listener_updates}, loadbalancer)

            # Step 3: Handle configuration updates that require service recreation
            if self._requires_service_recreation(listener_updates):
                LOG.info("Listener %s updates require service recreation", listener_id)
                
                # Delete existing service
                self.delete(old_listener, loadbalancer)
                
                # Create new service with updated configuration
                return self.create({**old_listener, **listener_updates}, loadbalancer)

            # Step 4: Handle updates that can be applied without recreation
            # For most listener updates, LoxiLB requires service recreation
            # This is because LoxiLB doesn't support in-place service updates
            LOG.info("Applying listener %s updates via service recreation", listener_id)
            self.delete(old_listener, loadbalancer)
            return self.create({**old_listener, **listener_updates}, loadbalancer)

        except Exception as e:
            LOG.error("Failed to update listener %s: %s", listener_id, e)
            raise exceptions.LoxiLBOperationException(
                operation="update_listener",
                resource_type="listener", 
                resource_id=listener_id,
                reason=str(e),
            )

    def delete(self, listener):
        """Delete a listener with cascade awareness and state reconciliation.

        CRITICAL: This method addresses the architectural mismatch between Octavia's
        granular resource model and LoxiLB's composite service model. When a listener
        is deleted in LoxiLB, it cascade deletes the entire service including pools,
        members, and health monitors.

        Args:
            listener: The listener object from Octavia

        Returns:
            dict: Status information for Octavia with reconciliation details
        """
        # Handle both dictionary and object types for listener parameter
        listener_id = extract_attr(listener, "id") or extract_attr(listener, "listener_id")
        LOG.info("Deleting listener %s with enhanced state reconciliation", listener_id)

        # STEP 1: CRITICAL - Identify dependent resources before deletion
        dependent_resources = {}
        reconciliation_summary = {}
        
        try:
            dependent_resources = self.state_reconciler.get_dependent_resources(listener)
            
            if dependent_resources:
                total_dependents = (
                    len(dependent_resources.get('pools', [])) +
                    len(dependent_resources.get('members', [])) +
                    len(dependent_resources.get('health_monitors', []))
                )
                
                LOG.warning(
                    "CASCADE DELETE WARNING: Deleting listener %s will cascade delete "
                    "%d dependent resources in LoxiLB: %s",
                    listener_id, total_dependents, dependent_resources
                )
        except Exception as e:
            LOG.warning("Failed to analyze dependencies for listener %s: %s", listener_id, e)
            # Continue with deletion even if dependency analysis fails

        try:
            # STEP 2: Validate pre-deletion state
            try:
                consistency_check = self.state_reconciler.validate_resource_consistency(
                    'listener', listener_id
                )
                if not consistency_check['consistent']:
                    LOG.warning("Listener %s has inconsistent state before deletion: %s", 
                              listener_id, consistency_check['issues'])
            except Exception as e:
                LOG.warning("Failed to validate pre-deletion state for listener %s: %s", 
                          listener_id, e)

            # STEP 3: Get LoxiLB service mapping
            LOG.info("Looking up mapping for listener %s in delete method", listener_id)
            
            # Debug: Check the contents of the mapping cache
            cache_entries = len(self.resource_mapper.id_mapping_cache.get("octavia_to_loxilb", {}))
            LOG.info("Current mapping cache has %d entries", cache_entries)
            
            # Get mapping for this listener
            loxilb_service_key = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, listener_id
            )

            if not loxilb_service_key:
                LOG.warning("No mapping found for listener %s in delete method. This may indicate a mapping storage issue.", listener_id)
                
                # Check if there's any metadata for this listener
                metadata = utils.get_id_mapping_metadata(self.resource_mapper.id_mapping_cache, listener_id)
                if metadata:
                    LOG.info("Found metadata for listener %s but no mapping key: %s", listener_id, metadata)
                    # Clean up orphaned metadata
                    resource_metadata = self.resource_mapper.id_mapping_cache.get("resource_metadata", {})
                    if listener_id in resource_metadata:
                        del resource_metadata[listener_id]
                        LOG.info("Removed orphaned metadata for listener %s", listener_id)
                        
                        # Force save mappings to ensure consistency
                        storage_path = self.resource_mapper.id_mapping_cache.get("_storage_path")
                        if storage_path:
                            success = utils.save_id_mappings_to_storage(self.resource_mapper.id_mapping_cache)
                            if success:
                                LOG.debug("Successfully saved ID mappings after metadata cleanup")
                            else:
                                LOG.error("Failed to save ID mappings after metadata cleanup")
                
                # Even though we couldn't delete the actual resource, mark it as deleted
                # since there's no mapping to find it anyway
                return {
                    "status": {
                        "id": listener_id,
                        "provisioning_status": lib_consts.DELETED,
                        "operating_status": lib_consts.OFFLINE
                    }
                }
            
            # Continue with deletion since we found a mapping
            # STEP 4: Parse service key to get deletion parameters
            try:
                service_info = utils.parse_loxilb_service_key(loxilb_service_key)
                external_ip = service_info["external_ip"]
                port = service_info["port"]
                protocol = service_info["protocol"]
            except ValueError as e:
                LOG.error("Invalid service key format for listener %s: %s", listener_id, e)
                # Try alternative deletion method using listener data
                external_ip = self._get_vip_address(self.get_loadbalancer(listener))
                port = extract_attr(listener, "protocol_port")
                protocol_str = extract_attr(listener, "protocol", "HTTP")
                protocol = utils.map_octavia_protocol_to_loxilb(protocol_str)

            # STEP 5: Delete the LoxiLB service
            try:
                self.api_client.delete_loadbalancer_rule(external_ip, port, protocol)
                LOG.info("Successfully deleted LoxiLB service for listener %s", listener_id)
            except exceptions.LoxiLBResourceNotFoundException:
                LOG.info("LoxiLB service for listener %s was already deleted", listener_id)
            except Exception as e:
                LOG.warning("Failed to delete LoxiLB service for listener %s: %s", listener_id, e)
                # Continue with cleanup - don't fail the operation

            # STEP 6: CRITICAL - Reconcile cascade effects
            if dependent_resources:
                try:
                    reconciliation_summary = self.state_reconciler.reconcile_cascade_delete(
                        listener_id, dependent_resources
                    )
                    LOG.info("Cascade delete reconciliation completed: %s", reconciliation_summary)
                except Exception as e:
                    LOG.error("Failed to reconcile cascade delete for listener %s: %s", 
                             listener_id, e)
                    # Continue - don't fail the entire operation

            # STEP 7: Remove listener ID mapping
            LOG.info("Removing ID mapping for listener %s with loxilb_service_key %s", 
                    listener_id, loxilb_service_key)
            
            # Check if mapping exists before removal
            pre_check = utils.get_loxilb_key_from_octavia_id(self.resource_mapper.id_mapping_cache, listener_id)
            LOG.info("Pre-removal mapping check for %s: %s", listener_id, pre_check)
            
            utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, listener_id)
            
            # Verify mapping was removed
            post_check = utils.get_loxilb_key_from_octavia_id(self.resource_mapper.id_mapping_cache, listener_id)
            LOG.info("Post-removal mapping check for %s: %s", listener_id, post_check or "<removed>")
            
            # Force save mappings to ensure consistency after removal
            storage_path = self.resource_mapper.id_mapping_cache.get("_storage_path")
            if storage_path:
                success = utils.save_id_mappings_to_storage(self.resource_mapper.id_mapping_cache)
                if success:
                    LOG.debug("Successfully saved ID mappings after listener deletion")
                else:
                    LOG.error("Failed to save ID mappings after listener deletion")

            LOG.info("Successfully deleted listener %s with reconciliation", listener_id)
            
            result = {
                "status": {
                    "id": listener_id,
                    "provisioning_status": lib_consts.DELETED,
                    "operating_status": lib_consts.OFFLINE
                }
            }
            
            # Add reconciliation info for monitoring and debugging
            if reconciliation_summary:
                result['cascade_reconciliation'] = reconciliation_summary
                
            return result

        except Exception as e:
            LOG.error("Enhanced listener deletion failed for %s: %s", listener_id, e)
            
            # Even if deletion fails, attempt reconciliation to prevent orphaned state
            if dependent_resources:
                try:
                    reconciliation_summary = self.state_reconciler.reconcile_cascade_delete(
                        listener_id, dependent_resources
                    )
                    LOG.info("Emergency reconciliation completed after deletion failure")
                except Exception as reconcile_error:
                    LOG.error("Failed emergency reconciliation: %s", reconcile_error)
            
            # Octavia expects delete to be idempotent, so we don't re-raise
            # But we still remove the mapping to prevent orphaned entries
            utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, listener_id)
            return {
                "status": {
                    "id": listener_id,
                    "provisioning_status": lib_consts.ERROR,
                    "operating_status": lib_consts.OFFLINE
                }
            }

        except Exception as e:
            LOG.error("Failed to delete listener %s: %s", listener_id, e)
            # Octavia expects delete to be idempotent, so we don't re-raise
            # But we still remove the mapping to prevent orphaned entries
            utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, listener_id)
            return {
                "status": {
                    "id": listener_id,
                    "provisioning_status": lib_consts.ERROR,
                    "operating_status": lib_consts.OFFLINE
                }
            }

    def get(self, listener_id):
        """Get listener information.

        Retrieves listener information from LoxiLB and maps it back to Octavia format.

        Args:
            listener_id: UUID of the listener

        Returns:
            dict: Listener information in Octavia format

        Raises:
            LoxiLBResourceNotFoundException: If listener is not found
        """
        LOG.debug("Getting listener %s", listener_id)

        try:
            # Step 1: Get LoxiLB service mapping
            loxilb_service_key = utils.get_loxilb_key_from_octavia_id(
                self.resource_mapper.id_mapping_cache, listener_id
            )

            if not loxilb_service_key:
                # Try to recover mapping by scanning LoxiLB services
                LOG.info("No mapping found for listener %s, attempting recovery", listener_id)
                recovered_count = utils.recover_id_mappings_from_loxilb(
                    self.resource_mapper.id_mapping_cache,
                    self.api_client,
                    self.resource_mapper
                )
                
                if recovered_count > 0:
                    loxilb_service_key = utils.get_loxilb_key_from_octavia_id(
                        self.resource_mapper.id_mapping_cache, listener_id
                    )

                if not loxilb_service_key:
                    raise exceptions.LoxiLBResourceNotFoundException(
                        resource_type="listener",
                        resource_id=listener_id,
                        endpoint="LoxiLB"
                    )

            # Step 2: Get service information from LoxiLB
            service_info = utils.parse_loxilb_service_key(loxilb_service_key)
            loxilb_services = self.api_client.list_loadbalancers()

            # Find the specific service
            matching_service = None
            for service in loxilb_services:
                service_args = service.get("serviceArguments", {})
                if (service_args.get("externalIP") == service_info["external_ip"] and
                    service_args.get("port") == service_info["port"] and
                    service_args.get("protocol") == service_info["protocol"]):
                    matching_service = service
                    break

            if not matching_service:
                raise exceptions.LoxiLBResourceNotFoundException(
                    resource_type="listener",
                    resource_id=listener_id,
                    endpoint="LoxiLB"
                )

            # Step 3: Convert to Octavia format with metadata enhancement
            # Get stored metadata for additional fields
            metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache, listener_id
            )
            
            # Convert LoxiLB service to Octavia listener format
            service_args = matching_service.get("serviceArguments", {})
            
            listener_data = {
                "id": listener_id,
                "name": metadata.get("listener_name") or service_args.get("name", f"listener-{listener_id[:8]}"),
                "description": metadata.get("listener_description", ""),
                "protocol": utils.map_loxilb_protocol_to_octavia(service_args.get("protocol", "tcp")),
                "protocol_port": service_args.get("port", 80),
                "connection_limit": metadata.get("connection_limit", -1),
                "admin_state_up": metadata.get("admin_state_up", True),
                "operating_status": lib_consts.ONLINE,
                "provisioning_status": lib_consts.ACTIVE,
                "created_at": metadata.get("created_at"),  # From stored metadata
                "updated_at": metadata.get("updated_at"),  # From stored metadata (when available)
                "project_id": None,  # Not available - would need OpenStack context
                "default_pool_id": metadata.get("pool_id"),  # From stored metadata
                "loadbalancer_id": metadata.get("loadbalancer_id"),  # From stored metadata
                "default_tls_container_ref": metadata.get("tls_container_ref"),  # From stored metadata
            }

            return listener_data

        except Exception as e:
            LOG.error("Failed to get listener %s: %s", listener_id, e)
            raise

    def get_all(self):
        """Get all listeners managed by this driver.

        Returns:
            list: List of listener dictionaries in Octavia format
        """
        LOG.debug("Getting all listeners")

        try:
            # Get all LoxiLB services
            loxilb_services = self.api_client.list_loadbalancers()
            listeners = []

            # Convert each service to listener format if we have a mapping
            for octavia_id, loxilb_key in self.resource_mapper.id_mapping_cache["octavia_to_loxilb"].items():
                metadata = utils.get_id_mapping_metadata(
                    self.resource_mapper.id_mapping_cache, octavia_id
                )
                
                # Only process listener mappings
                if metadata.get("resource_type") == "listener":
                    try:
                        listener_data = self.get(octavia_id)
                        listeners.append(listener_data)
                    except exceptions.LoxiLBResourceNotFoundException:
                        LOG.warning("Listener %s mapping exists but service not found in LoxiLB", octavia_id)
                        # Clean up orphaned mapping
                        utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, octavia_id)

            return listeners

        except Exception as e:
            LOG.error("Failed to get all listeners: %s", e)
            return []

    def _update_listener_metadata(self, listener_id, updates):
        """Update listener metadata with timestamp tracking.
        
        Args:
            listener_id: Listener UUID
            updates: Dictionary of updates to apply to metadata
        """
        # Get existing metadata
        metadata = utils.get_id_mapping_metadata(
            self.resource_mapper.id_mapping_cache, listener_id
        )
        
        if metadata:
            # Update metadata with new values and timestamp
            updated_metadata = {**metadata, **updates, "updated_at": time.time()}
            
            # Store updated metadata
            utils.store_id_mapping(
                self.resource_mapper.id_mapping_cache,
                listener_id,
                metadata.get("loxilb_key"),
                "listener",
                updated_metadata
            )

    # Helper methods

    def _attempt_service_key_recovery(self, listener_id):
        """Attempt to recover a service key for a listener when the mapping is missing.
        
        This method tries various approaches to reconstruct the LoxiLB service key
        when the ID mapping is missing, such as:
        1. Looking for patterns in existing mappings
        2. Querying LoxiLB API for services that might match
        3. Using any available metadata to reconstruct the key
        
        Args:
            listener_id (str): ID of the listener to recover service key for
            
        Returns:
            str or None: Recovered service key if successful, None otherwise
        """
        LOG.info("Attempting to recover service key for listener %s", listener_id)
        recovered_key = None
        
        # Method 1: Check if there's metadata with partial information
        metadata = self.resource_mapper.id_mapping_cache.get("resource_metadata", {}).get(listener_id)
        if metadata:
            LOG.debug("Found metadata for listener %s: %s", listener_id, metadata)
            # Try to reconstruct from metadata if it contains relevant fields
            if all(k in metadata for k in ["external_ip", "protocol_port", "protocol"]):
                try:
                    external_ip = metadata["external_ip"]
                    port = metadata["protocol_port"]
                    protocol = utils.map_octavia_protocol_to_loxilb(metadata["protocol"])
                    recovered_key = f"{external_ip}:{port}/{protocol}"
                    LOG.info("Recovered service key from metadata: %s", recovered_key)
                    return recovered_key
                except Exception as e:
                    LOG.warning("Failed to reconstruct service key from metadata: %s", e)
        
        # Method 2: Query LoxiLB API for services that might match this listener
        try:
            services = self.api_client.list_services()
            # Filter services that might be related to this listener
            # This is a best-effort approach and might not be accurate
            for service in services:
                service_key = service.get("key")
                if service_key and listener_id in service.get("name", ""):
                    LOG.info("Found potential matching service by name: %s", service_key)
                    recovered_key = service_key
                    break
        except Exception as e:
            LOG.warning("Failed to query LoxiLB API for services: %s", e)
        
        return recovered_key
        
    def _reconcile_cascade_delete(self, listener_id):
        """Reconcile cascade delete effects.

        Args:
            listener_id (str): ID of the listener that was deleted

        Returns:
            None
        """
        # Implementation details omitted for brevity
        # This would handle cleaning up any resources that were cascade deleted
        pass
        
    def _validate_listener_config(self, listener):
        """Validate listener configuration.
        
        Args:
            listener: Listener object to validate
            
        Raises:
            LoxiLBValidationException: If validation fails
        """
        errors = []

        # Required fields
        if isinstance(listener, dict):
            if not listener.get("id") and not listener.get("listener_id"):
                errors.append("Listener ID is required")
            if not listener.get("protocol"):
                errors.append("Listener protocol is required")
            if not listener.get("protocol_port"):
                errors.append("Listener protocol_port is required")
        else:
            if not getattr(listener, "id", getattr(listener, "listener_id", None)):
                errors.append("Listener ID is required")
            if not getattr(listener, "protocol", None):
                errors.append("Listener protocol is required")
            if not getattr(listener, "protocol_port", None):
                errors.append("Listener protocol_port is required")

        # Validate protocol
        protocol = extract_attr(listener, "protocol", "").upper()
            
        if protocol not in ["HTTP", "HTTPS", "TCP", "UDP", "TERMINATED_HTTPS", "PROXY", "SCTP"]:
            errors.append(f"Unsupported protocol: {protocol}")

        # Validate port
        port = extract_attr(listener, "protocol_port", None)
            
        if not port or not isinstance(port, int) or port < 1 or port > 65535:
            errors.append(f"Invalid port: {port}")

        # Validate TLS configuration
        protocol = extract_attr(listener, "protocol", "").upper()
        default_tls_container_ref = extract_attr(listener, "default_tls_container_ref", None)
            
        if protocol in ["HTTPS", "TERMINATED_HTTPS"]:
            if not default_tls_container_ref:
                errors.append("TLS container reference required for HTTPS listeners")

        if errors:
            raise exceptions.LoxiLBValidationException(
                resource_type="listener",
                validation_errors=errors
            )

    def _get_vip_address(self, loadbalancer):
        """Extract VIP address from load balancer object.
        
        Args:
            loadbalancer: Load balancer object or dictionary
            
        Returns:
            str: VIP IP address
            
        Raises:
            LoxiLBValidationException: If VIP address not found
        """
        if not loadbalancer:
            LOG.error("No loadbalancer provided to _get_vip_address")
            raise exceptions.LoxiLBValidationException(
                resource_type="listener",
                validation_errors=["No load balancer associated with listener"]
            )

        # Log loadbalancer ID for tracking
        lb_id = None
        lb_id = extract_attr(loadbalancer, "id", None)
        
        LOG.info("Attempting to extract VIP address from loadbalancer: %s", lb_id)
        
        # Check if we only have a loadbalancer ID and no other information
        if isinstance(loadbalancer, dict) and len(loadbalancer) == 1 and "id" in loadbalancer:
            LOG.error("Only loadbalancer ID is available (%s), but no VIP information. "
                     "The driver needs access to the complete loadbalancer object.", lb_id)
            LOG.error("This is likely because the listener was created with only a loadbalancer_id "
                     "reference, but the driver needs the full loadbalancer object with VIP information.")
            LOG.error("To fix this issue, the provider driver should fetch the complete loadbalancer "
                     "object from the Octavia database before passing it to the listener driver.")
            raise exceptions.LoxiLBValidationException(
                resource_type="listener",
                validation_errors=[f"Incomplete loadbalancer information. Only ID ({lb_id}) is available, "
                                  f"but VIP address is required."]
            )
        
        # Try different ways to get VIP address (different API versions)
        vip_address = None               
        
        # Method 1: vip.ip_address
        vip = extract_attr(loadbalancer, "vip", None)
            
        if vip:
            vip_address = extract_attr(vip, "ip_address", None)
                
        # Method 2: vip_address directly
        if not vip_address:
            vip_address = extract_attr(loadbalancer, "vip_address", None)
                
        # Method 3: vip_subnet_id resolution (would require neutron client)
        if not vip_address:
            LOG.info("Checking for vip_subnet_id as last resort")
            vip_subnet_id = extract_attr(loadbalancer, "vip_subnet_id", None)
                
            if vip_subnet_id:
                LOG.warning("VIP address not provided, subnet ID found but neutron resolution not implemented")

        if not vip_address:
            LOG.error("Failed to find VIP address for loadbalancer: %s", lb_id)
            raise exceptions.LoxiLBValidationException(
                resource_type="listener",
                validation_errors=["Load balancer VIP address not found"]
            )

        LOG.info("Successfully extracted VIP address: %s from loadbalancer: %s", vip_address, lb_id)
        return vip_address

    def _apply_listener_config(self, loxilb_lb_config, listener):
        """Apply listener-specific configuration to LoxiLB service.
        
        Args:
            loxilb_lb_config: LoxiLB load balancer configuration to modify
            listener: Octavia listener object
        """
        service_args = loxilb_lb_config.get("serviceArguments", {})
        
        # Set listener-specific name
        listener_name = extract_attr(listener, "name") or f"listener-{extract_attr(listener, 'id', 'unknown')[:8]}"            
        service_args["name"] = listener_name
        
        # Handle connection limits
        connection_limit = extract_attr(listener, "connection_limit", None)
            
        if connection_limit and connection_limit > 0:
            # LoxiLB doesn't have direct connection limit, but we can set it in service arguments
            service_args["connectionLimit"] = connection_limit
            
        # Handle TLS/SSL configuration
        protocol = extract_attr(listener, "protocol", "").upper()
        default_tls_container_ref = extract_attr(listener, "default_tls_container_ref", None)
            
        if protocol in ["HTTPS", "TERMINATED_HTTPS"]:
            if default_tls_container_ref:
                service_args["tlsContainerRef"] = default_tls_container_ref
            # This is already handled above
                
        # Handle proxy protocol
        if protocol == "PROXY":
            service_args["proxyProtocol"] = True

    def _should_create_on_missing_mapping(self, listener, updates):
        """Determine if we should create a new service when mapping is missing.
        
        Args:
            listener: Listener object
            updates: Update dictionary
            
        Returns:
            bool: True if should create, False otherwise
        """
        # If admin_state_up is being set to True, create the service
        if updates.get("admin_state_up") is True:
            return True
            
        # If admin state is currently up, recreate
        if listener.get("admin_state_up", True):
            return True
            
        return False

    def _requires_service_recreation(self, listener_updates):
        """Check if updates require LoxiLB service recreation.
        
        Args:
            listener_updates: Dictionary of field updates
            
        Returns:
            bool: True if recreation required
        """
        # Most listener changes require recreation in LoxiLB
        recreation_fields = [
            "protocol",
            "protocol_port", 
            "default_tls_container_ref",
            "sni_container_refs",
            "connection_limit",
            "default_pool_id"
        ]
        
        return any(field in listener_updates for field in recreation_fields)
