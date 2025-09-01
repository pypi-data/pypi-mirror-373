# octavia_loxilb_driver/driver/provider_driver.py
"""Enhanced LoxiLB provider driver for Octavia with architectural fixes."""

from typing import Any, Dict, List
import time

import octavia_lib.api.drivers.exceptions as driver_exceptions
from octavia_lib.api.drivers import provider_base as driver_lib
from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging

from octavia.common import constants as octavia_constants
from octavia.common import rpc

from octavia_loxilb_driver.api.loxilb_client import LoxiLBAPIClient

from octavia_loxilb_driver.common import config, constants, exceptions, utils
from octavia_loxilb_driver.driver import (healthmonitor_driver,
                                          listener_driver, loadbalancer_driver,
                                          member_driver, pool_driver)
from octavia_loxilb_driver.resource_mapping.mapper import ResourceMapper
from octavia_loxilb_driver.controller.worker.flows import flow_utils as loxilb_flow_utils
from taskflow import engines

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

# General-purpose attribute extraction function
def extract_attr(obj, key, default=None):
    """Safely extract attribute from dict or object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

class OperationalMetrics:
    """Tracks operational metrics for the LoxiLB driver."""
    
    def __init__(self):
        self.start_time = time.time()
        self.operation_count = 0
        self.cascade_delete_count = 0
        self.state_inconsistency_count = 0
        self.endpoint_api_usage_count = 0
        self.service_recreation_count = 0
        self.error_count = 0
        
    def record_operation(self, operation_type, success=True):
        """Record an operation."""
        self.operation_count += 1
        if not success:
            self.error_count += 1
        LOG.debug("Recorded %s operation (success=%s)", operation_type, success)
    
    def record_cascade_delete(self, affected_resources):
        """Record a cascade delete operation."""
        self.cascade_delete_count += 1
        LOG.warning("Cascade delete recorded affecting %d resources", affected_resources)
    
    def record_state_inconsistency(self, resource_type, resource_id):
        """Record a state inconsistency detection."""
        self.state_inconsistency_count += 1
        LOG.error("State inconsistency recorded for %s %s", resource_type, resource_id)
    
    def record_endpoint_api_usage(self):
        """Record successful endpoint API usage."""
        self.endpoint_api_usage_count += 1
        LOG.debug("Endpoint API usage recorded")
    
    def record_service_recreation(self):
        """Record service recreation fallback."""
        self.service_recreation_count += 1
        LOG.info("Service recreation recorded")
    
    def get_metrics(self):
        """Get current metrics."""
        uptime = time.time() - self.start_time
        return {
            'uptime_seconds': uptime,
            'total_operations': self.operation_count,
            'cascade_deletes': self.cascade_delete_count,
            'state_inconsistencies': self.state_inconsistency_count,
            'endpoint_api_usage': self.endpoint_api_usage_count,
            'service_recreations': self.service_recreation_count,
            'errors': self.error_count,
            'success_rate': (
                (self.operation_count - self.error_count) / max(self.operation_count, 1)
            ),
            'cascade_delete_rate': (
                self.cascade_delete_count / max(self.operation_count, 1)
            ),
            'endpoint_api_efficiency': (
                self.endpoint_api_usage_count / max(
                    self.endpoint_api_usage_count + self.service_recreation_count, 1
                )
            )
        }


class LoxiLBProviderDriver(driver_lib.ProviderDriver):
    """Enhanced LoxiLB provider driver with architectural fixes and monitoring."""

    def __init__(self):
        """Initialize enhanced LoxiLB provider driver."""
        super().__init__()
        
        # Initialize status callback (will be set by Octavia when driver is loaded)
        # RPC is now used for all status updates
        
        # Initialize metrics tracking
        self.metrics = OperationalMetrics()

        # Register configuration
        config.register_opts(CONF)

        # Validate configuration
        config_errors = config.validate_config(CONF)
        if config_errors:
            error_msg = "LoxiLB driver configuration errors: " + "; ".join(
                config_errors
            )
            LOG.error(error_msg)
            raise exceptions.LoxiLBConfigurationException(
                "driver_initialization", error_msg
            )

        # Setup logging
        config.setup_logging(CONF)

        # Initialize components
        self.config = CONF.loxilb
        self.api_client = LoxiLBAPIClient(self.config)
        self.resource_mapper = ResourceMapper(self.config)
        
        # Initialize RPC client
        self.target = messaging.Target(
            namespace=octavia_constants.RPC_NAMESPACE_CONTROLLER_AGENT,
            topic=self.config.rpc_topic, 
            version='1.0', 
            fanout=False
        )
        self.client = rpc.get_client(self.target)
        
        LOG.info("LoxiLB RPC client initialized with namespace=%s, topic=%s", 
                 octavia_constants.RPC_NAMESPACE_CONTROLLER_AGENT, 
                 self.config.rpc_topic)

        # Initialize sub-drivers
        self.loadbalancer_driver = loadbalancer_driver.LoadBalancerDriver(
            self.api_client, self.resource_mapper, self.config
        )
        self.listener_driver = listener_driver.ListenerDriver(
            self.api_client, self.resource_mapper, self.config
        )
        self.pool_driver = pool_driver.PoolDriver(
            self.api_client, self.resource_mapper, self.config
        )
        self.member_driver = member_driver.MemberDriver(
            self.api_client, self.resource_mapper, self.config
        )
        self.healthmonitor_driver = healthmonitor_driver.HealthMonitorDriver(
            self.api_client, self.resource_mapper, self.config
        )
        
    def set_status_callback(self, status_callback):
        """Set the callback function for status updates.
        
        This method is kept for compatibility with the Octavia driver interface,
        but it does nothing since we're using RPC for all status updates.
        
        :param status_callback: Callback function that will be used to update the status
        """
        LOG.debug("loxilb:Status callback function is ignored as RPC is used for all status updates")
        # No-op as we're using RPC for all status updates
    
    def update_loadbalancer_status(self, status):
        """Update load balancer status in Octavia.
        
        This method is kept for compatibility with existing code that might call it,
        but it does nothing since we're using RPC for all status updates.
        
        :param status: Dictionary containing status updates for resources
        """
        LOG.debug("Status updates are now handled via RPC, ignoring direct status update: %s", status)
        # No-op as we're using RPC for all status updates

        # Operational metrics tracker
        self.metrics = OperationalMetrics()

        # Test connectivity to LoxiLB cluster
        self._test_connectivity()

        LOG.info(
            "LoxiLB provider driver initialized successfully with "
            f"{len(self.config.api_endpoints)} endpoints"
        )

    def _test_connectivity(self):
        """Test connectivity to LoxiLB cluster during initialization."""
        try:
            if not self.api_client.health_check():
                LOG.warning("LoxiLB cluster health check failed during initialization")
        except Exception as e:
            LOG.error(f"Failed to connect to LoxiLB cluster during initialization: {e}")
            raise exceptions.LoxiLBConnectionException(
                endpoint=", ".join(self.config.api_endpoints), original_exception=e
            )

    # Provider Information Methods
    def get_supported_flavor_metadata(self) -> Dict[str, Any]:
        """Get supported flavor metadata for LoxiLB provider."""
        return {
            "loadbalancer_topology": {
                "description": "Load balancer topology",
                "type": "string",
                "choices": ["SINGLE", "ACTIVE_STANDBY"],
                "default": "SINGLE",
            },
            "compute_flavor": {
                "description": "Compute flavor for load balancer instances",
                "type": "string",
                "default": "small",
            },
            "enable_anti_affinity": {
                "description": "Enable anti-affinity for HA deployments",
                "type": "boolean",
                "default": False,
            },
            "performance_tier": {
                "description": "Performance tier for load balancer",
                "type": "string",
                "choices": ["standard", "high", "maximum"],
                "default": "standard",
            },
        }

    def get_supported_availability_zone_metadata(self) -> Dict[str, Any]:
        """Get supported availability zone metadata."""
        return {
            "availability_zone": {
                "description": "Availability zone for load balancer deployment",
                "type": "string",
            },
            "enable_cross_zone_load_balancing": {
                "description": "Enable cross-zone load balancing",
                "type": "boolean",
                "default": True,
            },
        }

    # Load Balancer Management Methods
    def loadbalancer_create(self, loadbalancer):
        """Create a load balancer using LoxiLB TaskFlow and sync resource mapping via RPC."""
        try:
            lb_id = extract_attr(loadbalancer, "loadbalancer_id", str(loadbalancer))
            LOG.info("loxilb:Creating load balancer %s (TaskFlow, best practice)", lb_id)

            # Only extract the VIP subnet ID and pass all provisioning to TaskFlow
            vip_subnet_id = extract_attr(loadbalancer, "vip_subnet_id")
            if not vip_subnet_id:
                raise Exception("VIP subnet ID is missing from loadbalancer object")
            else:
                LOG.info(f"loxilb:Passing VIP subnet ID {vip_subnet_id} for load balancer {lb_id} to TaskFlow")            

            flow = loxilb_flow_utils.get_create_loxilb_load_balancer_flow()
            store = {
                "lb_id": lb_id,
                "vip_subnet_id": vip_subnet_id,
                "flavor_name": "loxilb",
                "image_tag": "loxilb",
            }
            engine = engines.load(flow, store=store)
            engine.run()
            LOG.info("loxilb:Successfully provisioned load balancer %s via TaskFlow", lb_id)

            # Sync resource mapping cache with controller/worker via RPC
            LOG.info("loxilb:Syncing resource mapping cache for load balancer %s via RPC", lb_id)
            flavor = extract_attr(loadbalancer, "flavor")
            if hasattr(flavor, '__class__') and flavor.__class__.__name__ == 'Unset':
                flavor = None

            payload = {"load_balancer_id": lb_id}
            if flavor:
                payload['flavor'] = flavor
            else:
                payload['flavor'] = "loxilb"
            if vip_subnet_id:
                payload['vip_subnet_id'] = vip_subnet_id

            self.client.cast({}, "create_load_balancer", **payload)
            LOG.info("loxilb:RPC request sent to sync resource mapping cache for load balancer %s", lb_id)
        except Exception as e:
            LOG.exception("loxilb:Error creating load balancer via TaskFlow: %s", str(e))
            raise driver_exceptions.DriverError(
                user_fault_string="Load balancer creation failed",
                operator_fault_string=str(e)
            )

    def loadbalancer_failover(self, loadbalancer_id: str) -> None:
        """Failover a load balancer.

        Args:
            loadbalancer_id: Load balancer ID to failover

        Raises:
            DriverError: If load balancer failover fails
        """
        try:
            LOG.info(f"loxilb:Failing over load balancer: {loadbalancer_id}")
            self.loadbalancer_driver.failover(loadbalancer_id)
            LOG.info(f"loxilb:Load balancer failover completed: {loadbalancer_id}")
            self.metrics.record_operation("loadbalancer_failover", success=True)

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error during failover: {e}")
            self.metrics.record_operation("loadbalancer_failover", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error during failover: {e}")
            self.metrics.record_operation("loadbalancer_failover", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Load balancer failover failed",
                operator_fault_string=str(e),
            )

    def loadbalancer_delete(self, loadbalancer, cascade=False):
        """Delete a load balancer using LoxiLB TaskFlow and sync resource mapping via RPC."""
        try:
            lb_id = extract_attr(loadbalancer, "loadbalancer_id", str(loadbalancer))
            vip_subnet_id = extract_attr(loadbalancer, "vip_network_id", '')
            vip_port_id = extract_attr(loadbalancer, "vip_port_id", '')
            LOG.info(f"loxilb:Deleting load balancer {lb_id} (TaskFlow)")
            flow = loxilb_flow_utils.get_delete_loxilb_load_balancer_flow()
            store = {
                "lb_id": lb_id,
                "vip_subnet_id": vip_subnet_id,
                "vip_port_id": vip_port_id,
            }
            engine = engines.load(flow, store=store)
            engine.run()          
            
            LOG.info(f"loxilb:Syncing resource mapping cache for load balancer {lb_id} deletion via RPC")
            payload = {"loadbalancer_id": lb_id}
            self.client.cast({}, "delete_load_balancer", **payload)
            LOG.info(f"loxilb:RPC request sent to sync resource mapping cache for load balancer deletion {lb_id}")
            self.metrics.record_operation("loadbalancer_delete", success=True)
        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error deleting load balancer: {e}")
            self.metrics.record_operation("loadbalancer_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error deleting load balancer via TaskFlow: {e}")
            self.metrics.record_operation("loadbalancer_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Load balancer deletion failed",
                operator_fault_string=str(e),
            )

    def loadbalancer_update(
        self, old_loadbalancer: Dict, new_loadbalancer: Dict
    ) -> None:
        """Update a load balancer.

        Args:
            old_loadbalancer: Current load balancer configuration
            new_loadbalancer: New load balancer configuration

        Raises:
            DriverError: If load balancer update fails
        """
        try:
            # Extract load balancer ID
            lb_id = extract_attr(new_loadbalancer, 'loadbalancer_id') or str(new_loadbalancer)

            LOG.info("loxilb:Updating load balancer %s", lb_id)
            
            LOG.info("loxilb:Using RPC mechanism for updating load balancer %s", lb_id)
            # Adapt the provider data model to the queue schema
            if hasattr(new_loadbalancer, 'to_dict'):
                lb_dict = new_loadbalancer.to_dict()
            else:
                lb_dict = dict(new_loadbalancer)
                
            if 'admin_state_up' in lb_dict:
                lb_dict['enabled'] = lb_dict.pop('admin_state_up')
                
            # Handle VIP QoS policy if present
            vip_qos_policy_id = lb_dict.pop('vip_qos_policy_id', None)
            if vip_qos_policy_id:
                vip_dict = {"qos_policy_id": vip_qos_policy_id}
                lb_dict["vip"] = vip_dict
                
            # Send RPC cast to controller worker
            payload = {octavia_constants.LOAD_BALANCER_ID: lb_id,
                      octavia_constants.LOAD_BALANCER_UPDATES: lb_dict}
            self.client.cast({}, 'update_load_balancer', **payload)
            LOG.info("loxilb:Successfully sent RPC update request for load balancer %s", lb_id)
        except Exception as e:
            self.metrics.record_operation("loadbalancer_update", success=False)
            LOG.exception("loxilb:Error updating load balancer: %s", str(e))
            raise driver_exceptions.DriverError(
                user_fault_string="Load balancer update failed",
                operator_fault_string=str(e),
            )            

    # Listener Management Methods
    def listener_create(self, listener) -> None:
        """Create a listener.

        Args:
            listener: Listener configuration dictionary or object

        Raises:
            DriverError: If listener creation fails
        """
        try:
            listener_id = extract_attr(listener, 'listener_id') or extract_attr(listener, 'id') or str(listener)
            LOG.info(f"loxilb:Creating listener: {listener_id}")
            loadbalancer = extract_attr(listener, 'loadbalancer')
            if loadbalancer:
                # Check VIP info
                has_vip = extract_attr(loadbalancer, 'vip') is not None
                has_vip_address = extract_attr(loadbalancer, 'vip_address') is not None
                if not (has_vip or has_vip_address):
                    LOG.warning(f"loxilb:Loadbalancer object is missing VIP information. This may cause issues when creating the listener.")
                    if isinstance(loadbalancer, dict):
                        LOG.warning(f"loxilb:Available loadbalancer keys: {list(loadbalancer.keys())}")
            elif extract_attr(listener, 'loadbalancer_id'):
                LOG.warning(f"loxilb:Only loadbalancer_id is available ({extract_attr(listener, 'loadbalancer_id')}), but no complete loadbalancer object with VIP information.")
                LOG.warning(f"loxilb:This may cause issues when creating the listener.")
                
            LOG.info(f"loxilb:Creating listener: {listener_id}")
            
            # Instead of directly calling the listener driver, use RPC to offload to controller worker
            # which can access the Octavia DB to get the complete loadbalancer object
            if getattr(listener, 'loadbalancer_id', None):
                loadbalancer_id = getattr(listener, 'loadbalancer_id')
                LOG.info(f"loxilb:Using RPC to create listener {listener_id} for loadbalancer {loadbalancer_id}")
                
                # Prepare payload for RPC call
                payload = {
                    'listener_id': listener_id,
                    'loadbalancer_id': loadbalancer_id
                }
                
                # Make RPC call to controller worker
                self.client.cast({}, 'create_listener', **payload)
                LOG.info(f"loxilb:RPC request sent to create listener {listener_id}")
            else:
                # If we somehow have the complete loadbalancer object, use it directly
                # This is a fallback path and should rarely be used
                if loadbalancer:
                    LOG.info(f"loxilb:Using direct path to create listener with available loadbalancer object")
                    self.listener_driver.create(listener, loadbalancer)
                    LOG.info(f"loxilb:Listener created successfully via direct path: {listener_id}")
                else:
                    # We don't have enough information to create the listener
                    raise exceptions.LoxiLBValidationException(
                        resource_type="listener",
                        resource_id=listener_id,
                        reason="Missing loadbalancer information required for listener creation"
                    )
            
            self.metrics.record_operation("listener_create", success=True)

        except exceptions.LoxiLBValidationException as e:
            if "Incomplete loadbalancer information" in str(e) or "Load balancer VIP address not found" in str(e):
                LOG.error(f"LoxiLB driver error: Missing VIP information in loadbalancer object")
                LOG.error(f"This is likely because the listener was created with only a loadbalancer_id "
                         f"reference, but the driver needs the full loadbalancer object with VIP information.")
                LOG.error(f"To fix this issue, ensure the complete loadbalancer object with VIP information "
                         f"is passed to the provider driver when creating a listener.")
            
            LOG.error(f"LoxiLB driver validation error creating listener: {e}")
            self.metrics.record_operation("listener_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error creating listener: {e}")
            self.metrics.record_operation("listener_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error creating listener: {e}")
            self.metrics.record_operation("listener_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Listener creation failed",
                operator_fault_string=str(e),
            )

    def listener_delete(self, listener) -> None:
        """Delete a listener.

        Args:
            listener: Listener configuration dictionary or object

        Raises:
            DriverError: If listener deletion fails
        """
        try:
            listener_id = extract_attr(listener, 'listener_id') or extract_attr(listener, 'id') or str(listener)
            loadbalancer_id = extract_attr(listener, 'loadbalancer_id')
            if not loadbalancer_id:
                lb = extract_attr(listener, 'loadbalancer')
                if lb:
                    loadbalancer_id = extract_attr(lb, 'id')
                
            LOG.info(f"loxilb:Deleting listener: {listener_id}")
            
            # Use RPC to offload deletion to controller worker where mapping file exists
            # This matches the pattern used in listener_create
            if listener_id:
                LOG.info(f"loxilb:Using RPC to delete listener {listener_id}")
                
                # Prepare payload for RPC call
                payload = {
                    'listener_id': listener_id
                }
                
                if loadbalancer_id:
                    payload['loadbalancer_id'] = loadbalancer_id
                    LOG.info(f"loxilb:Deleting listener {listener_id} for loadbalancer {loadbalancer_id}")
                
                # Make RPC call to controller worker
                self.client.cast({}, 'delete_listener', **payload)
                LOG.info(f"loxilb:RPC request sent to delete listener {listener_id}")
            else:
                # Fallback to direct deletion if we can't use RPC
                # This should rarely happen
                LOG.warning(f"loxilb:Using direct path to delete listener (no ID available for RPC)")
                self.listener_driver.delete(listener)
                
            LOG.info(f"loxilb:Listener deletion request processed: {listener_id}")
            self.metrics.record_operation("listener_delete", success=True)

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error deleting listener: {e}")
            self.metrics.record_operation("listener_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error deleting listener: {e}")
            self.metrics.record_operation("listener_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Listener deletion failed",
                operator_fault_string=str(e),
            )

    def listener_update(self, old_listener, new_listener) -> None:
        """Update a listener.

        Args:
            old_listener: Current listener configuration (dict or object)
            new_listener: New listener configuration (dict or object)

        Raises:
            DriverError: If listener update fails
        """
        try:
            listener_id = extract_attr(new_listener, 'listener_id') or str(new_listener)
                
            LOG.info(f"loxilb:Updating listener: {listener_id}")
            self.listener_driver.update(old_listener, new_listener)
            LOG.info(f"loxilb:Listener updated successfully: {listener_id}")
            self.metrics.record_operation("listener_update", success=True)

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error updating listener: {e}")
            self.metrics.record_operation("listener_update", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error updating listener: {e}")
            self.metrics.record_operation("listener_update", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Listener update failed", operator_fault_string=str(e)
            )

    # Pool Management Methods
    def pool_create(self, pool) -> None:
        """Create a new pool via RPC to controller worker.

        Args:
            pool: Pool object or dictionary

        Raises:
            DriverError: If pool creation fails
        """
        try:
            # Extract pool_id and loadbalancer_id
            pool_id = extract_attr(pool, 'pool_id') or extract_attr(pool, 'id') or str(pool)
            loadbalancer_id = extract_attr(pool, 'loadbalancer_id')

            LOG.info(f"loxilb:Creating pool via RPC: {pool_id} for loadbalancer {loadbalancer_id}")
            payload = {
                'pool_id': pool_id,
                'loadbalancer_id': loadbalancer_id
            }
            self.client.cast({}, 'create_pool', **payload)
            LOG.info(f"loxilb:RPC request sent to create pool {pool_id}")
            self.metrics.record_operation("pool_create", success=True)

        except Exception as e:
            LOG.error(f"Unexpected error creating pool: {e}")
            self.metrics.record_operation("pool_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Pool creation failed", operator_fault_string=str(e)
            )

    def pool_delete(self, pool) -> None:
        """Delete a pool via RPC to controller worker.

        Args:
            pool: Pool object or dictionary

        Raises:
            DriverError: If pool deletion fails
        """
        try:
            pool_id = extract_attr(pool, 'pool_id') or extract_attr(pool, 'id') or str(pool)
            loadbalancer_id = extract_attr(pool, 'loadbalancer_id')

            LOG.info(f"loxilb:Deleting pool via RPC: {pool_id} for loadbalancer {loadbalancer_id}")
            payload = {
                'pool_id': pool_id,
                'loadbalancer_id': loadbalancer_id
            }
            self.client.cast({}, 'delete_pool', **payload)
            LOG.info(f"loxilb:RPC request sent to delete pool {pool_id}")
            self.metrics.record_operation("pool_delete", success=True)

        except Exception as e:
            LOG.error(f"Unexpected error deleting pool: {e}")
            self.metrics.record_operation("pool_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Pool deletion failed", operator_fault_string=str(e)
            )

    def pool_update(self, old_pool, new_pool) -> None:
        """Update a pool via RPC to controller worker.

        Args:
            old_pool: Current pool object or dictionary
            new_pool: New pool object or dictionary

        Raises:
            DriverError: If pool update fails
        """
        try:
            pool_id = extract_attr(new_pool, 'pool_id') or extract_attr(new_pool, 'id') or str(new_pool)
            loadbalancer_id = extract_attr(new_pool, 'loadbalancer_id')

            LOG.info(f"loxilb:Updating pool via RPC: {pool_id} for loadbalancer {loadbalancer_id}")
            payload = {
                'pool_id': pool_id,
                'loadbalancer_id': loadbalancer_id,
                'old_pool': old_pool,
                'new_pool': new_pool
            }
            self.client.cast({}, 'update_pool', **payload)
            LOG.info(f"loxilb:RPC request sent to update pool {pool_id}")
            self.metrics.record_operation("pool_update", success=True)

        except Exception as e:
            LOG.error(f"Unexpected error updating pool: {e}")
            self.metrics.record_operation("pool_update", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Pool update failed", operator_fault_string=str(e)
            )

    # Member Management Methods
    def member_create(self, member) -> None:
        """Create a member via RPC to controller worker.

        Args:
            member: Member object or dictionary

        Raises:
            DriverError: If member creation fails
        """
        try:
            member_id = extract_attr(member, 'member_id') or extract_attr(member, 'id')
            pool_id = extract_attr(member, 'pool_id')
            subnet_id = extract_attr(member, 'subnet_id')
            
            LOG.info(f"loxilb:Creating member via RPC: {member_id} for pool {pool_id} in subnet {subnet_id}")
            
            # Include subnet_id and loadbalancer_id in the payload
            # This allows the controller worker to attach the LoxiLB VM to the member's subnet
            payload = {
                'member_id': member_id,
                'pool_id': pool_id,
                'subnet_id': subnet_id
            }
            
            self.client.cast({}, 'create_member', **payload)
            LOG.info(f"loxilb:RPC request sent to create member {member_id} in subnet {subnet_id}")
            self.metrics.record_operation("member_create", success=True)

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error creating member: {e}")
            self.metrics.record_operation("member_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error creating member: {e}")
            self.metrics.record_operation("member_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Member creation failed", operator_fault_string=str(e)
            )

    def member_delete(self, member) -> None:
        """Delete a member via RPC to controller worker.

        Args:
            member: Member object or dictionary

        Raises:
            DriverError: If member deletion fails
        """
        try:
            member_id = extract_attr(member, 'member_id') or extract_attr(member, 'id')
            pool_id = extract_attr(member, 'pool_id')
            subnet_id = extract_attr(member, 'subnet_id')
            loadbalancer_id = extract_attr(member, 'loadbalancer_id')
            
            LOG.info(f"loxilb:Deleting member via RPC: {member_id} from pool {pool_id} in subnet {subnet_id}")
            
            # Include subnet_id and loadbalancer_id in the payload
            # This allows the controller worker to check if this is the last member in the subnet
            # and potentially detach the LoxiLB VM from that subnet
            payload = {
                'member_id': member_id,
                'pool_id': pool_id,
                'subnet_id': subnet_id,
                'loadbalancer_id': loadbalancer_id
            }
            
            self.client.cast({}, 'delete_member', **payload)
            LOG.info(f"loxilb:RPC request sent to delete member {member_id} from subnet {subnet_id}")
            self.metrics.record_operation("member_delete", success=True)

        except Exception as e:
            LOG.error(f"Unexpected error deleting member: {e}")
            self.metrics.record_operation("member_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Member deletion failed", operator_fault_string=str(e)
            )

    def member_update(self, old_member, new_member) -> None:
        """Update a member via RPC to controller worker.

        Args:
            old_member: Current member configuration (dict or object)
            new_member: New member configuration (dict or object)

        Raises:
            DriverError: If member update fails
        """
        try:
            member_id = extract_attr(new_member, 'member_id') or extract_attr(new_member, 'id')
            pool_id = extract_attr(new_member, 'pool_id')
            LOG.info(f"loxilb:Updating member via RPC: {member_id} in pool {pool_id}")
            payload = {
                'member_id': member_id,
                'pool_id': pool_id,
                'old_member': old_member,
                'new_member': new_member
            }
            self.client.cast({}, 'update_member', **payload)
            LOG.info(f"loxilb:RPC request sent to update member {member_id}")
            self.metrics.record_operation("member_update", success=True)

        except Exception as e:
            LOG.error(f"Unexpected error updating member: {e}")
            self.metrics.record_operation("member_update", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Member update failed", operator_fault_string=str(e)
            )

    def member_batch_update(
        self, old_members, new_members
    ) -> None:
        """Batch update members via RPC to controller worker.

        Args:
            old_members: List of current member objects or dictionaries
            new_members: List of new member objects or dictionaries

        Raises:
            DriverError: If batch member update fails
        """
        try:
            LOG.info(f"loxilb:Batch updating {len(new_members)} members via RPC")
            payload = {
                'old_members': old_members,
                'new_members': new_members
            }
            self.client.cast({}, 'batch_update_members', **payload)
            LOG.info("loxilb:RPC request sent for batch member update")
            self.metrics.record_operation("member_batch_update", success=True)

        except Exception as e:
            LOG.error(f"Unexpected error during batch member update: {e}")
            self.metrics.record_operation("member_batch_update", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Batch member update failed",
                operator_fault_string=str(e),
            )

    # Health Monitor Management Methods
    def health_monitor_create(self, healthmonitor) -> None:
        """Create a health monitor.

        Args:
            healthmonitor: Health monitor object or dictionary

        Raises:
            DriverError: If health monitor creation fails
        """
        try:
            hm_id = extract_attr(healthmonitor, 'healthmonitor_id') or extract_attr(healthmonitor, 'id') or str(healthmonitor)
            LOG.info(f"loxilb:Creating health monitor via RPC: {hm_id}")
            payload = {'healthmonitor_id': hm_id}
            self.client.cast({}, 'create_health_monitor', **payload)
            LOG.info(f"loxilb:RPC request sent to create health monitor {hm_id}")
            self.metrics.record_operation("health_monitor_create", success=True)
        except Exception as e:
            LOG.error(f"Unexpected error creating health monitor: {e}")
            self.metrics.record_operation("health_monitor_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Health monitor creation failed",
                operator_fault_string=str(e),
            )

    def health_monitor_delete(self, healthmonitor) -> None:
        """Delete a health monitor.

        Args:
            healthmonitor: Health monitor object or dictionary

        Raises:
            DriverError: If health monitor deletion fails
        """
        try:
            hm_id = extract_attr(healthmonitor, 'healthmonitor_id') or extract_attr(healthmonitor, 'id') or str(healthmonitor)
            LOG.info(f"loxilb:Deleting health monitor via RPC: {hm_id}")
            payload = {'healthmonitor_id': hm_id}
            self.client.cast({}, 'delete_health_monitor', **payload)
            LOG.info(f"loxilb:RPC request sent to delete health monitor {hm_id}")
            self.metrics.record_operation("health_monitor_delete", success=True)
        except Exception as e:
            LOG.error(f"Unexpected error deleting health monitor: {e}")
            self.metrics.record_operation("health_monitor_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Health monitor deletion failed",
                operator_fault_string=str(e),
            )

    def health_monitor_update(
        self, old_healthmonitor, new_healthmonitor
    ) -> None:
        """Update a health monitor.

        Args:
            old_healthmonitor: Current health monitor object or dictionary
            new_healthmonitor: New health monitor object or dictionary

        Raises:
            DriverError: If health monitor update fails
        """
        try:
            hm_id = extract_attr(new_healthmonitor, 'healthmonitor_id') or extract_attr(new_healthmonitor, 'id') or str(new_healthmonitor)
            LOG.info(f"loxilb:Updating health monitor via RPC: {hm_id}")
            payload = {'healthmonitor_id': hm_id, 'old_healthmonitor': old_healthmonitor, 'new_healthmonitor': new_healthmonitor}
            self.client.cast({}, 'update_health_monitor', **payload)
            LOG.info(f"loxilb:RPC request sent to update health monitor {hm_id}")
            self.metrics.record_operation("health_monitor_update", success=True)
        except Exception as e:
            LOG.error(f"Unexpected error updating health monitor: {e}")
            self.metrics.record_operation("health_monitor_update", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="Health monitor update failed",
                operator_fault_string=str(e),
            )

    # Statistics and Monitoring Methods
    def validate_flavor(self, flavor_metadata: Dict[str, Any]) -> None:
        """Validate flavor metadata.

        Args:
            flavor_metadata: Flavor metadata to validate

        Raises:
            UnsupportedOptionError: If flavor metadata is not supported
        """
        supported_metadata = self.get_supported_flavor_metadata()

        for key, value in flavor_metadata.items():
            if key not in supported_metadata:
                raise driver_exceptions.UnsupportedOptionError(
                    user_fault_string=f"Unsupported flavor option: {key}",
                    operator_fault_string=(
                        f"Flavor option {key} is not supported by LoxiLB driver"
                    ),
                )

            metadata = supported_metadata[key]
            if "choices" in metadata and value not in metadata["choices"]:
                raise driver_exceptions.UnsupportedOptionError(
                    user_fault_string=f"Invalid value for {key}: {value}",
                    operator_fault_string=(
                        f"Value {value} not in allowed choices {metadata['choices']}"
                    ),
                )

    # Statistics Methods
    def get_loadbalancer_stats(self, loadbalancer_id: str) -> Dict[str, Any]:
        """Get load balancer statistics.

        Args:
            loadbalancer_id: Load balancer ID

        Returns:
            Dictionary containing load balancer statistics

        Raises:
            DriverError: If retrieving statistics fails
        """
        try:
            LOG.debug(f"Getting statistics for load balancer: {loadbalancer_id}")
            stats = self.loadbalancer_driver.get_stats(loadbalancer_id)
            return stats

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error getting load balancer stats: {e}")
            raise driver_exceptions.DriverError(
                user_fault_string="Failed to retrieve load balancer statistics",
                operator_fault_string=str(e),
            )
        except Exception as e:
            LOG.error(f"Unexpected error getting load balancer stats: {e}")
            raise driver_exceptions.DriverError(
                user_fault_string="Failed to retrieve load balancer statistics",
                operator_fault_string=str(e),
            )

    # Driver Management Methods
    def validate_availability_zone(
        self, availability_zone_metadata: Dict[str, Any]
    ) -> None:
        """Validate availability zone metadata.

        Args:
            availability_zone_metadata: Availability zone metadata to validate

        Raises:
            UnsupportedOptionError: If availability zone metadata is not supported
        """
        # LoxiLB driver supports basic availability zone configuration
        supported_keys = ["availability_zone", "enable_cross_zone_load_balancing"]

        for key in availability_zone_metadata:
            if key not in supported_keys:
                raise driver_exceptions.UnsupportedOptionError(
                    user_fault_string=f"Unsupported availability zone option: {key}",
                    operator_fault_string=(
                        f"Availability zone option {key} is not supported"
                    ),
                )

    def get_resource_versions(self) -> Dict[str, str]:
        """Get supported resource versions.

        Returns:
            Dictionary mapping resource types to supported versions
        """
        return {
            "loadbalancer": "1.0",
            "listener": "1.0",
            "pool": "1.0",
            "member": "1.0",
            "healthmonitor": "1.0",
            "l7policy": "1.0",
            "l7rule": "1.0",
        }

    def health_check(self) -> bool:
        """Perform driver health check.

        Returns:
            True if driver is healthy, False otherwise
        """
        try:
            return self.api_client.health_check()
        except Exception as e:
            LOG.error(f"Driver health check failed: {e}")
            return False

    def get_driver_status(self) -> Dict[str, Any]:
        """Get driver status information.

        Returns:
            Dictionary containing driver status information
        """
        try:
            cluster_status = self.api_client.get_cluster_status()
            driver_stats = utils.get_driver_stats()

            return {
                "driver_name": constants.DRIVER_NAME,
                "driver_version": constants.DRIVER_VERSION,
                "provider_name": constants.PROVIDER_NAME,
                "healthy": self.health_check(),
                "cluster_status": cluster_status,
                "statistics": driver_stats,
                "endpoints": self.config.api_endpoints,
                "capabilities": self.api_client.get_capabilities(),
                "operational_metrics": self.metrics.get_metrics(),
            }
        except Exception as e:
            LOG.error(f"Failed to get driver status: {e}")
            return {
                "driver_name": constants.DRIVER_NAME,
                "driver_version": constants.DRIVER_VERSION,
                "healthy": False,
                "error": str(e),
            }

    # Cleanup Methods
    def cleanup(self):
        """Cleanup driver resources."""
        try:
            if hasattr(self, "api_client"):
                self.api_client.close()
            LOG.info("LoxiLB provider driver cleanup completed")
        except Exception as e:
            LOG.error(f"Error during driver cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception as e:
            LOG.error("Cleanup during destruction failed: %s", str(e))
    
    # L7 Policy Management Methods
    def l7policy_create(self, l7policy):
        """Create an L7 policy.

        Args:
            l7policy: L7 policy configuration dictionary or object

        Raises:
            DriverError: If L7 policy creation fails
        """
        try:
            # Extract L7 policy ID
            l7policy_id = extract_attr(l7policy, 'id') or str(l7policy)
                
            LOG.info(f"loxilb:Creating L7 policy: {l7policy_id}")
            
            # Send RPC cast to controller worker
            payload = {octavia_constants.L7POLICY_ID: l7policy_id}
            self.client.cast({}, 'create_l7policy', **payload)
            LOG.info("loxilb:Successfully sent RPC request for L7 policy %s", l7policy_id)
            
            # Call the loadbalancer driver implementation
            self.loadbalancer_driver.l7policy_create(l7policy)
            
            LOG.info(f"loxilb:L7 policy created successfully: {l7policy_id}")
            self.metrics.record_operation("l7policy_create", success=True)

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error creating L7 policy: {e}")
            self.metrics.record_operation("l7policy_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error creating L7 policy: {e}")
            self.metrics.record_operation("l7policy_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="L7 policy creation failed",
                operator_fault_string=str(e),
            )

    def l7policy_delete(self, l7policy):
        """Delete an L7 policy.

        Args:
            l7policy: L7 policy configuration dictionary or object

        Raises:
            DriverError: If L7 policy deletion fails
        """
        try:
            # Extract L7 policy ID
            l7policy_id = extract_attr(l7policy, 'id') or str(l7policy)
                
            LOG.info(f"loxilb:Deleting L7 policy: {l7policy_id}")
            
            # Send RPC cast to controller worker
            payload = {octavia_constants.L7POLICY_ID: l7policy_id}
            self.client.cast({}, 'delete_l7policy', **payload)
            LOG.info("loxilb:Successfully sent RPC request for deleting L7 policy %s", l7policy_id)
            
            # Call the loadbalancer driver implementation
            self.loadbalancer_driver.l7policy_delete(l7policy)
            
            LOG.info(f"loxilb:L7 policy deleted successfully: {l7policy_id}")
            self.metrics.record_operation("l7policy_delete", success=True)

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error deleting L7 policy: {e}")
            self.metrics.record_operation("l7policy_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error deleting L7 policy: {e}")
            self.metrics.record_operation("l7policy_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="L7 policy deletion failed",
                operator_fault_string=str(e),
            )

    def l7policy_update(self, old_l7policy, new_l7policy):
        """Update an L7 policy.

        Args:
            old_l7policy: Current L7 policy configuration (dict or object)
            new_l7policy: New L7 policy configuration (dict or object)

        Raises:
            DriverError: If L7 policy update fails
        """
        try:
            # Extract L7 policy ID
            l7policy_id = extract_attr(new_l7policy, 'id') or str(new_l7policy)
                
            LOG.info(f"loxilb:Updating L7 policy: {l7policy_id}")
            
            # Adapt the provider data model to the queue schema
            if hasattr(new_l7policy, 'to_dict'):
                l7policy_dict = new_l7policy.to_dict()
            else:
                l7policy_dict = dict(new_l7policy)
                
            # Send RPC cast to controller worker
            payload = {octavia_constants.L7POLICY_ID: l7policy_id,
                      octavia_constants.L7POLICY_UPDATES: l7policy_dict}
            self.client.cast({}, 'update_l7policy', **payload)
            LOG.info("loxilb:Successfully sent RPC request for updating L7 policy %s", l7policy_id)
            
            # Call the loadbalancer driver implementation
            self.loadbalancer_driver.l7policy_update(old_l7policy, new_l7policy)
            
            LOG.info(f"loxilb:L7 policy updated successfully: {l7policy_id}")
            self.metrics.record_operation("l7policy_update", success=True)

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error updating L7 policy: {e}")
            self.metrics.record_operation("l7policy_update", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error updating L7 policy: {e}")
            self.metrics.record_operation("l7policy_update", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="L7 policy update failed",
                operator_fault_string=str(e),
            )
            
    # L7 Rule Management Methods
    def l7rule_create(self, l7rule):
        """Create an L7 rule.

        Args:
            l7rule: L7 rule configuration dictionary or object

        Raises:
            DriverError: If L7 rule creation fails
        """
        try:
            # Extract L7 rule ID
            l7rule_id = extract_attr(l7rule, 'id') or str(l7rule)
                
            LOG.info(f"loxilb:Creating L7 rule: {l7rule_id}")
            
            # Send RPC cast to controller worker
            payload = {octavia_constants.L7RULE_ID: l7rule_id}
            self.client.cast({}, 'create_l7rule', **payload)
            LOG.info("loxilb:Successfully sent RPC request for L7 rule %s", l7rule_id)
            
            # Call the loadbalancer driver implementation
            self.loadbalancer_driver.l7rule_create(l7rule)
            
            LOG.info(f"loxilb:L7 rule created successfully: {l7rule_id}")
            self.metrics.record_operation("l7rule_create", success=True)

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error creating L7 rule: {e}")
            self.metrics.record_operation("l7rule_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error creating L7 rule: {e}")
            self.metrics.record_operation("l7rule_create", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="L7 rule creation failed",
                operator_fault_string=str(e),
            )

    def l7rule_delete(self, l7rule):
        """Delete an L7 rule.

        Args:
            l7rule: L7 rule configuration dictionary or object

        Raises:
            DriverError: If L7 rule deletion fails
        """
        try:
            # Extract L7 rule ID
            l7rule_id = extract_attr(l7rule, 'id') or str(l7rule)
                
            LOG.info(f"loxilb:Deleting L7 rule: {l7rule_id}")
            
            # Send RPC cast to controller worker
            payload = {octavia_constants.L7RULE_ID: l7rule_id}
            self.client.cast({}, 'delete_l7rule', **payload)
            LOG.info("loxilb:Successfully sent RPC request for deleting L7 rule %s", l7rule_id)
            
            # Call the loadbalancer driver implementation
            self.loadbalancer_driver.l7rule_delete(l7rule)
            
            LOG.info(f"loxilb:L7 rule deleted successfully: {l7rule_id}")
            self.metrics.record_operation("l7rule_delete", success=True)

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error deleting L7 rule: {e}")
            self.metrics.record_operation("l7rule_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error deleting L7 rule: {e}")
            self.metrics.record_operation("l7rule_delete", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="L7 rule deletion failed",
                operator_fault_string=str(e),
            )

    def l7rule_update(self, old_l7rule, new_l7rule):
        """Update an L7 rule.

        Args:
            old_l7rule: Current L7 rule configuration (dict or object)
            new_l7rule: New L7 rule configuration (dict or object)

        Raises:
            DriverError: If L7 rule update fails
        """
        try:
            # Extract L7 rule ID
            l7rule_id = extract_attr(new_l7rule, 'id') or str(new_l7rule)
                
            LOG.info(f"loxilb:Updating L7 rule: {l7rule_id}")
            
            # Adapt the provider data model to the queue schema
            if hasattr(new_l7rule, 'to_dict'):
                l7rule_dict = new_l7rule.to_dict()
            else:
                l7rule_dict = dict(new_l7rule)
                
            # Send RPC cast to controller worker
            payload = {octavia_constants.L7RULE_ID: l7rule_id,
                      octavia_constants.L7RULE_UPDATES: l7rule_dict}
            self.client.cast({}, 'update_l7rule', **payload)
            LOG.info("loxilb:Successfully sent RPC request for updating L7 rule %s", l7rule_id)
            
            # Call the loadbalancer driver implementation
            self.loadbalancer_driver.l7rule_update(old_l7rule, new_l7rule)
            
            LOG.info(f"loxilb:L7 rule updated successfully: {l7rule_id}")
            self.metrics.record_operation("l7rule_update", success=True)

        except exceptions.LoxiLBDriverException as e:
            LOG.error(f"LoxiLB driver error updating L7 rule: {e}")
            self.metrics.record_operation("l7rule_update", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string=e.fault_string, operator_fault_string=str(e)
            )
        except Exception as e:
            LOG.error(f"Unexpected error updating L7 rule: {e}")
            self.metrics.record_operation("l7rule_update", success=False)
            raise driver_exceptions.DriverError(
                user_fault_string="L7 rule update failed",
                operator_fault_string=str(e),
            )
