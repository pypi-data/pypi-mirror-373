# octavia_loxilb_driver/driver/loadbalancer_driver.py
import time

from octavia_lib.api.drivers import exceptions as driver_exceptions
from octavia_lib.common import constants as lib_consts
from oslo_log import log as logging

from octavia_loxilb_driver.common import exceptions, utils

LOG = logging.getLogger(__name__)

# General-purpose attribute extraction function
def extract_attr(obj, key, default=None):
    """Safely extract attribute from dict or object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def get_listener_id(listener):
    """Extract ID from listener object or dict.
    
    Args:
        listener: Listener object or dict
        
    Returns:
        str: Listener ID
    """
    listener_id = extract_attr(listener, "id")
    if not listener_id:
        listener_id = extract_attr(listener, "listener_id")
    return listener_id


class LoadBalancerDriver:
    """Load Balancer Management Driver for LoxiLB."""
    
    @staticmethod
    def get_vip_address(loadbalancer):
        """Extract VIP address from loadbalancer object or dict.
        
        Args:
            loadbalancer: Loadbalancer object or dict
            
        Returns:
            str: VIP address or None if not found
        """
        vip = None
        
        if isinstance(loadbalancer, dict):
            vip = extract_attr(loadbalancer.get("vip", {}), "ip_address")
            if not vip:
                vip = extract_attr(loadbalancer, "vip_address")
        else:
            vip = extract_attr(extract_attr(loadbalancer, "vip"), "ip_address")
            if not vip:
                vip = extract_attr(loadbalancer, "vip_address")
                
        return vip

    def __init__(self, api_client, resource_mapper, config):
        self.api_client = api_client
        self.resource_mapper = resource_mapper
        self.config = config

    def create(self, loadbalancer):
        """Create a load balancer.

        This method is called when a load balancer is created. In LoxiLB,
        a load balancer is defined by a service rule (VIP:port) which is
        equivalent to an Octavia listener. Therefore, we iterate through the
        listeners associated with the load balancer and create a LoxiLB
        service for each.

        :param loadbalancer: The load balancer object from Octavia.
        """
        # Handle both dictionary and object types for loadbalancer
        lb_id = None
        listeners = []
        
        if isinstance(loadbalancer, dict):
            lb_id = extract_attr(loadbalancer, "loadbalancer_id")
            listeners = extract_attr(loadbalancer, "listeners", [])
        else:
            lb_id = extract_attr(loadbalancer, "loadbalancer_id", str(loadbalancer))
            listeners = extract_attr(loadbalancer, "listeners", [])
            
        LOG.info("loxilb:Creating load balancer %s", lb_id)

        if not listeners:
            LOG.info(
                "loxilb:Load balancer %s has no listeners, nothing to create in LoxiLB.",
                lb_id,
            )
            # Update status to ACTIVE even if there are no listeners
            # Always log the status update attempt
            LOG.info(
                "loxilb:Load balancer %s has no listeners, nothing to create in LoxiLB.",
                lb_id,
            )
            
            # Status updates are now handled by the controller worker via RPC
            LOG.info(
                "loxilb:Status updates for load balancer %s are handled by the controller worker",
                lb_id,
            )
            return

        for listener in listeners:
            loxilb_service_key = None
            try:
                LOG.debug(
                    "loxilb:Processing listener %s for load balancer %s",
                    get_listener_id(listener),
                    lb_id,
                )
                
                # Step 1: Map Octavia resources to LoxiLB format
                lb_data = self.resource_mapper.loadbalancer_to_loxilb(
                    loadbalancer, listener
                )

                # Step 2: Extract LoxiLB service identifier
                service_args = lb_data["serviceArguments"]
                external_ip = service_args["externalIP"]
                port = service_args["port"]
                protocol = service_args["protocol"]
                
                loxilb_service_key = utils.get_loxilb_service_key(
                    external_ip, port, protocol
                )
                
                # Step 3: Check if service already exists (idempotency)
                existing_service = None
                try:
                    # Pass lb_id to use management network IP for API communication
                    existing_service = self.api_client.get_loadbalancer(loxilb_service_key, lb_id=lb_id)
                    if existing_service:
                        LOG.info(
                            "LoxiLB service %s already exists, updating instead of creating",
                            loxilb_service_key
                        )
                        # Pass lb_id to use management network IP for API communication
                        self.api_client.update_loadbalancer(loxilb_service_key, lb_data)
                    else:
                        # Step 4: Create new service in LoxiLB
                        # lb_id is extracted from the name in create_loadbalancer method
                        self.api_client.create_loadbalancer(lb_data)
                        
                except exceptions.LoxiLBResourceNotFoundException:
                    # Service doesn't exist, create it
                    # lb_id is extracted from the name in create_loadbalancer method
                    self.api_client.create_loadbalancer(lb_data)
                
                # Step 5: Store ID mapping for future operations
                # This mapping is crucial for tracking resources
                utils.store_id_mapping(
                    self.resource_mapper.id_mapping_cache,
                    lb_id,  # Octavia load balancer ID
                    loxilb_service_key,  # LoxiLB service identifier
                    "loadbalancer",
                    {
                        "external_ip": external_ip,
                        "port": port,
                        "protocol": protocol,
                        "listener_id": get_listener_id(listener),
                        "created_at": time.time(),
                        "created_by": "loadbalancer_driver"
                    }
                )

                LOG.info(
                    "loxilb:loxilb:Successfully created LoxiLB service %s for listener %s (LB %s)",
                    loxilb_service_key, get_listener_id(listener), lb_id
                )

            except exceptions.LoxiLBMappingException as e:
                LOG.error(
                    "loxilb:Failed to map listener %s to LoxiLB format: %s",
                    get_listener_id(listener),
                    e,
                )
                # Clean up any partial mapping on failure
                if loxilb_service_key:
                    try:
                        utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, lb_id)
                    except Exception:
                        pass  # Best effort cleanup
                        
                raise driver_exceptions.DriverError(
                    user_fault_string=f"Failed to process listener {listener.get('id')}: {e.fault_string}",
                    operator_fault_string=str(e),
                )
            except Exception as e:
                LOG.error(
                    "An unexpected error occurred while creating rule for listener %s: %s",
                    get_listener_id(listener),
                    e,
                )
                # Clean up any partial mapping on failure
                if loxilb_service_key:
                    try:
                        utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, lb_id)
                        # Also try to clean up the LoxiLB service if it was created
                        # Pass lb_id to use management network IP for API communication
                        self.api_client.delete_loadbalancer(loxilb_service_key, lb_id=lb_id)
                    except Exception:
                        pass  # Best effort cleanup
                        
                # This will mark the LB as ERROR
                raise driver_exceptions.DriverError(
                    user_fault_string=f"Failed to create load balancer {lb_id}",
                    operator_fault_string=str(e),
                )

        LOG.info("loxilb:Load balancer %s created successfully", lb_id)
        
        # Note: Status updates are now handled by the controller worker via RPC
        LOG.info("loxilb:Status updates for load balancer %s are handled by the controller worker", lb_id)

    def update(self, loadbalancer, loadbalancer_updates):
        """Update a load balancer.

        Handles updates to the load balancer. This method demonstrates how
        ID mapping enables finding and updating existing LoxiLB services
        when only the Octavia load balancer ID is provided.

        :param loadbalancer: The load balancer object before the update.
        :param loadbalancer_updates: A dict with the changed attributes.
        """
        # Handle both dictionary and object types for loadbalancer
        lb_id = None
        
        lb_id = extract_attr(loadbalancer, "loadbalancer_id", str(loadbalancer))
            
        LOG.info("loxilb:Updating load balancer %s", lb_id)

        # Step 1: Use ID mapping to find existing LoxiLB service
        loxilb_service_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, lb_id
        )
        
        if not loxilb_service_key:
            LOG.warning(
                "No ID mapping found for load balancer %s during update, "
                "attempting to recover mapping", lb_id
            )
            
            # Try to recover mapping by searching LoxiLB services
            try:
                # Use get method which has recovery logic
                existing_lb = self.get(lb_id)
                loxilb_service_key = utils.get_loxilb_key_from_octavia_id(
                    self.resource_mapper.id_mapping_cache, lb_id
                )
            except exceptions.LoxiLBResourceNotFoundException:
                # Load balancer doesn't exist, treat as create operation
                LOG.info(
                    "loxilb:loxilb:Load balancer %s not found in LoxiLB, treating update as create",
                    lb_id
                )
                self.create(loadbalancer)
                return

        # Step 2: Handle specific update scenarios
        if "admin_state_up" in loadbalancer_updates:
            is_up = loadbalancer_updates["admin_state_up"]
            if is_up:
                LOG.info(
                    "loxilb:loxilb:Load balancer %s is being enabled. Applying create logic.",
                    lb_id,
                )
                self.create(loadbalancer)
            else:
                LOG.info(
                    "loxilb:loxilb:Load balancer %s is being disabled. Applying delete logic.",
                    lb_id,
                )
                self.delete(loadbalancer)
        else:
            # Step 3: Handle updates that require LoxiLB service modification
            # (e.g., timeout changes, algorithm changes, etc.)
            
            # Get current service configuration
            try:
                # Pass lb_id to use management network IP for API communication
                current_service = self.api_client.get_loadbalancer(loxilb_service_key, lb_id=lb_id)
            except exceptions.LoxiLBResourceNotFoundException:
                LOG.error(
                    "LoxiLB service %s not found during update for LB %s",
                    loxilb_service_key, lb_id
                )
                # Clean up stale mapping
                utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, lb_id)
                # Treat as create operation
                self.create(loadbalancer)
                return
            
            # Check if any listeners were added/removed/modified
            updated_listeners = []
            updated_listeners = extract_attr(loadbalancer, "listeners", [])
                
            if updated_listeners:
                # Re-map the entire load balancer configuration
                for listener in updated_listeners:
                    try:
                        updated_config = self.resource_mapper.loadbalancer_to_loxilb(
                            loadbalancer, listener
                        )
                        
                        # Update the service in LoxiLB
                        # Pass lb_id to use management network IP for API communication
                        self.api_client.update_loadbalancer(loxilb_service_key, updated_config)
                        
                        # Update mapping metadata with update information
                        mapping_metadata = utils.get_id_mapping_metadata(
                            self.resource_mapper.id_mapping_cache, lb_id
                        )
                        if mapping_metadata:
                            mapping_metadata.update({
                                "last_updated": time.time(),
                                "update_count": mapping_metadata.get("update_count", 0) + 1,
                                "updated_by": "loadbalancer_driver"
                            })
                        
                        LOG.info(
                            "Successfully updated LoxiLB service %s for load balancer %s",
                            loxilb_service_key, lb_id
                        )
                        
                    except Exception as e:
                        LOG.error(
                            "Failed to update LoxiLB service %s for listener %s: %s",
                            loxilb_service_key, get_listener_id(listener), e
                        )
                        raise driver_exceptions.DriverError(
                            user_fault_string=f"Failed to update load balancer {lb_id}",
                            operator_fault_string=str(e)
                        )
            else:
                LOG.info(
                    "loxilb:loxilb:No relevant updates for LoxiLB on load balancer %s. Ignoring.",
                    lb_id,
                )

    def delete(self, loadbalancer):
        """Delete a load balancer.

        This method is called when a load balancer is deleted. In LoxiLB,
        a load balancer is defined by a service rule (VIP:port) which is
        equivalent to an Octavia listener. We use the ID mapping cache to
        find the corresponding LoxiLB services and delete them.

        :param loadbalancer: The load balancer object from Octavia.
        """
        # Handle both dictionary and object types for loadbalancer
        lb_id = None        
        lb_id = extract_attr(loadbalancer, "id") or extract_attr(loadbalancer, "loadbalancer_id")
        if not lb_id:
            LOG.error("Could not extract load balancer ID from object: %s", loadbalancer)
            return
        LOG.info("loxilb:Deleting load balancer %s", lb_id)

        # Method 1: Use ID mapping cache to find LoxiLB service
        loxilb_service_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, lb_id
        )
        
        if loxilb_service_key:
            try:
                LOG.debug("loxilb:Found LoxiLB service mapping: %s -> %s",
                    lb_id, loxilb_service_key)                
                # Delete from LoxiLB using the mapped service key
                # Pass lb_id to use management network IP for API communication
                self.api_client.delete_loadbalancer(loxilb_service_key, lb_id=lb_id)                
                LOG.info("loxilb:Successfully deleted LoxiLB service %s for load balancer %s",
                    loxilb_service_key, lb_id)
                
            except exceptions.LoxiLBResourceNotFoundException:
                LOG.warning("LoxiLB service %s not found, may have been deleted already",
                    loxilb_service_key)
            except Exception as e:
                LOG.error("Failed to delete LoxiLB service %s: %s",
                    loxilb_service_key, e)
                # Don't re-raise, as Octavia expects delete to be idempotent
            finally:
                # Always remove the mapping, even if delete failed
                utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, lb_id)
                
        else:
            # Method 2: Fallback - try to find and delete by listener information
            LOG.warning(
                "No ID mapping found for load balancer %s, attempting fallback deletion",
                lb_id
            )
            
            # Check for listeners in the loadbalancer object
            listeners = []
            listeners = extract_attr(loadbalancer, "listeners", [])
                
            if not listeners:
                LOG.info(
                    "loxilb:loxilb:Load balancer %s has no listeners, nothing to delete in LoxiLB.",
                    lb_id,
                )
                return

            # Get VIP information
            vip = self.get_vip_address(loadbalancer)
                
            if not vip:
                LOG.warning(
                    "Load balancer %s has no VIP, cannot delete rules.",
                    lb_id,
                )
                return

            # Try to delete by reconstructing the service key from listener info
            listeners_to_process = []
            listeners_to_process = extract_attr(loadbalancer, "listeners", [])
                
            for listener in listeners_to_process:
                try:
                    LOG.debug(
                        "Processing listener %s for load balancer %s deletion",
                        get_listener_id(listener),
                        lb_id,
                    )

                    port = listener.get("protocol_port")
                    protocol = utils.map_octavia_protocol_to_loxilb(
                        listener.get("protocol", "")
                    )

                    if not port or not protocol:
                        LOG.error(
                            "Listener %s is missing port or protocol, cannot delete.",
                            get_listener_id(listener),
                        )
                        continue

                    # Construct the LoxiLB service key
                    fallback_service_key = utils.get_loxilb_service_key(vip, port, protocol)
                    
                    try:
                        # Check if service exists and delete it
                        # Pass lb_id to use management network IP for API communication
                        self.api_client.delete_loadbalancer(fallback_service_key, lb_id=lb_id)
                        LOG.info(
                            "Successfully deleted LoxiLB service %s (fallback method)",
                            fallback_service_key
                        )
                        utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, lb_id)
                    except exceptions.LoxiLBResourceNotFoundException:
                        LOG.debug(
                            "LoxiLB service %s not found (may not exist)",
                            fallback_service_key
                        )

                except Exception as e:
                    LOG.error(
                        "An unexpected error occurred while deleting rule for listener %s: %s",
                        get_listener_id(listener),
                        e,
                    )
                    # Do not re-raise, as Octavia expects delete to be idempotent.

        # Note: Status updates are now handled by the controller worker via RPC
        LOG.info("loxilb:Status updates for load balancer %s are handled by the controller worker", lb_id)

    def get(self, loadbalancer_id):
        """Get load balancer details from LoxiLB.
        
        This method demonstrates how ID mapping enables efficient lookups
        of LoxiLB services using Octavia load balancer IDs.
        
        :param loadbalancer_id: The Octavia load balancer ID
        :return: Octavia-formatted load balancer dictionary
        """
        LOG.debug("Getting load balancer %s", loadbalancer_id)
        
        # Step 1: Use ID mapping to find LoxiLB service key
        loxilb_service_key = utils.get_loxilb_key_from_octavia_id(
            self.resource_mapper.id_mapping_cache, loadbalancer_id
        )
        
        if not loxilb_service_key:
            # Step 2: Fallback - search all services and try deterministic ID matching
            LOG.warning(
                "No ID mapping found for load balancer %s, searching LoxiLB services",
                loadbalancer_id
            )
            
            # Pass lb_id to use management network IP for API communication
            loxilb_services = self.api_client.list_loadbalancers(lb_id=loadbalancer_id)
            for service in loxilb_services:
                service_args = service.get("serviceArguments", {})
                
                # Generate deterministic ID to see if this service matches
                candidate_id = utils.generate_deterministic_id(
                    "loadbalancer",
                    external_ip=service_args.get("externalIP"),
                    port=service_args.get("port"),
                    protocol=service_args.get("protocol")
                )
                
                if candidate_id == loadbalancer_id:
                    loxilb_service_key = utils.get_loxilb_service_key(
                        service_args["externalIP"],
                        service_args["port"],
                        service_args["protocol"]
                    )
                    
                    # Re-establish the mapping for future operations
                    utils.store_id_mapping(
                        self.resource_mapper.id_mapping_cache,
                        loadbalancer_id,
                        loxilb_service_key,
                        "loadbalancer",
                        {"recovered_in_get": True}
                    )
                    break
        
        if not loxilb_service_key:
            raise exceptions.LoxiLBResourceNotFoundException(
                f"Load balancer {loadbalancer_id} not found in LoxiLB"
            )
        
        # Step 3: Get service details from LoxiLB
        try:
            # Pass lb_id to use management network IP for API communication
            loxilb_service = self.api_client.get_loadbalancer(loxilb_service_key, lb_id=loadbalancer_id)
        except exceptions.LoxiLBResourceNotFoundException:
            # Service was deleted from LoxiLB but mapping still exists
            utils.remove_id_mapping(self.resource_mapper.id_mapping_cache, loadbalancer_id)
            raise exceptions.LoxiLBResourceNotFoundException(
                f"Load balancer {loadbalancer_id} not found in LoxiLB"
            )
        
        # Step 4: Convert LoxiLB service back to Octavia format
        octavia_lb = self.resource_mapper.loxilb_to_octavia_loadbalancer(loxilb_service)
        
        # Ensure the ID matches what was requested (important for deterministic mapping)
        octavia_lb["id"] = loadbalancer_id
        
        return octavia_lb
    
    def get_all(self):
        """Get all load balancers from LoxiLB.
        
        This method shows how ID mapping helps maintain consistency when
        listing all resources, and how to recover mappings for discovered services.
        
        :return: List of Octavia-formatted load balancer dictionaries
        """
        LOG.debug("Getting all load balancers from LoxiLB")
        
        try:
            # Step 1: Get all services from LoxiLB
            # Note: We don't pass a specific lb_id here since we want all load balancers
            # This will use the static endpoint configured in the LoxiLB API client
            loxilb_services = self.api_client.list_loadbalancers()
            
            octavia_lbs = []
            recovered_mappings = 0
            
            for service in loxilb_services:
                try:
                    # Step 2: Convert to Octavia format (uses deterministic ID generation)
                    octavia_lb = self.resource_mapper.loxilb_to_octavia_loadbalancer(service)
                    lb_id = octavia_lb["id"]
                    
                    # Step 3: Ensure mapping exists for future operations
                    service_args = service.get("serviceArguments", {})
                    loxilb_service_key = utils.get_loxilb_service_key(
                        service_args["externalIP"],
                        service_args["port"],
                        service_args["protocol"]
                    )
                    
                    # Check if mapping already exists
                    existing_key = utils.get_loxilb_key_from_octavia_id(
                        self.resource_mapper.id_mapping_cache, lb_id
                    )
                    
                    if not existing_key:
                        # Create mapping for discovered service
                        utils.store_id_mapping(
                            self.resource_mapper.id_mapping_cache,
                            lb_id,
                            loxilb_service_key,
                            "loadbalancer",
                            {
                                "discovered_in_list": True,
                                "discovery_time": time.time()
                            }
                        )
                        recovered_mappings += 1
                    
                    octavia_lbs.append(octavia_lb)
                    
                except Exception as e:
                    LOG.warning(f"Failed to convert LoxiLB service to Octavia format: {e}")
                    continue
            
            if recovered_mappings > 0:
                LOG.info(f"Recovered {recovered_mappings} ID mappings during list operation")
            
            LOG.debug(f"Found {len(octavia_lbs)} load balancers in LoxiLB")
            return octavia_lbs
            
        except Exception as e:
            LOG.error(f"Failed to list load balancers from LoxiLB: {e}")
            # Update status to ERROR
            self.status_callback({
                "loadbalancers": [{
                    "id": "all",
                    "provisioning_status": lib_consts.ERROR,
                    "operating_status": lib_consts.OFFLINE
                }]
            })
            raise exceptions.LoxiLBOperationException(
                operation="list_loadbalancers",
                resource_type="loadbalancer",
                resource_id="all",
                reason=str(e)
            )
            
    # L7 Policy methods
    def l7policy_create(self, l7policy):
        """Create an L7 policy.

        :param l7policy: The L7 policy object from Octavia.
        """
        # Extract necessary information
        l7policy_id = extract_attr(l7policy, 'id')
        listener_id = extract_attr(l7policy, 'listener_id')
        
        LOG.info("loxilb:Creating L7 policy %s for listener %s", l7policy_id, listener_id)
        
        # The actual L7 policy creation is handled by the controller worker via RPC
        # This method is just a pass-through to maintain the driver interface
        LOG.info("loxilb:L7 policy %s creation is handled by the controller worker", l7policy_id)
        
    def l7policy_delete(self, l7policy):
        """Delete an L7 policy.

        :param l7policy: The L7 policy object from Octavia.
        """
        # Extract necessary information
        l7policy_id = extract_attr(l7policy, 'id')
        listener_id = extract_attr(l7policy, 'listener_id')
        
        LOG.info("loxilb:Deleting L7 policy %s for listener %s", l7policy_id, listener_id)
        
        # The actual L7 policy deletion is handled by the controller worker via RPC
        # This method is just a pass-through to maintain the driver interface
        LOG.info("loxilb:L7 policy %s deletion is handled by the controller worker", l7policy_id)
        
    def l7policy_update(self, old_l7policy, new_l7policy):
        """Update an L7 policy.

        :param old_l7policy: The L7 policy object from Octavia before the update.
        :param new_l7policy: The L7 policy object from Octavia with the update.
        """
        # Extract necessary information
        l7policy_id = extract_attr(old_l7policy, 'id')
        listener_id = extract_attr(old_l7policy, 'listener_id')
        
        LOG.info("loxilb:Updating L7 policy %s for listener %s", l7policy_id, listener_id)
        
        # The actual L7 policy update is handled by the controller worker via RPC
        # This method is just a pass-through to maintain the driver interface
        LOG.info("loxilb:L7 policy %s update is handled by the controller worker", l7policy_id)
    
    # L7 Rule methods
    def l7rule_create(self, l7rule):
        """Create an L7 rule.

        :param l7rule: The L7 rule object from Octavia.
        """
        # Extract necessary information
        l7rule_id = extract_attr(l7rule, 'id')
        l7policy_id = extract_attr(l7rule, 'l7policy_id')
        
        LOG.info("loxilb:Creating L7 rule %s for L7 policy %s", l7rule_id, l7policy_id)
        
        # The actual L7 rule creation is handled by the controller worker via RPC
        # This method is just a pass-through to maintain the driver interface
        LOG.info("loxilb:L7 rule %s creation is handled by the controller worker", l7rule_id)
        
    def l7rule_delete(self, l7rule):
        """Delete an L7 rule.

        :param l7rule: The L7 rule object from Octavia.
        """
        # Extract necessary information
        l7rule_id = extract_attr(l7rule, 'id')
        l7policy_id = extract_attr(l7rule, 'l7policy_id')
        
        LOG.info("loxilb:Deleting L7 rule %s for L7 policy %s", l7rule_id, l7policy_id)
        
        # The actual L7 rule deletion is handled by the controller worker via RPC
        # This method is just a pass-through to maintain the driver interface
        LOG.info("loxilb:L7 rule %s deletion is handled by the controller worker", l7rule_id)
        
    def l7rule_update(self, old_l7rule, new_l7rule):
        """Update an L7 rule.

        :param old_l7rule: The L7 rule object from Octavia before the update.
        :param new_l7rule: The L7 rule object from Octavia with the update.
        """
        # Extract necessary information
        l7rule_id = extract_attr(old_l7rule, 'id')
        l7policy_id = extract_attr(old_l7rule, 'l7policy_id')
        
        LOG.info("loxilb:Updating L7 rule %s for L7 policy %s", l7rule_id, l7policy_id)
        
        # The actual L7 rule update is handled by the controller worker via RPC
        # This method is just a pass-through to maintain the driver interface
        LOG.info("loxilb:L7 rule %s update is handled by the controller worker", l7rule_id)
