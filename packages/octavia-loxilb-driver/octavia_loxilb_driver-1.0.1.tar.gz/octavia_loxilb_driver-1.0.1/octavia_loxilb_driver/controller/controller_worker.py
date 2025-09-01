# Copyright 2025 LoxiLB
# Licensed under the Apache License, Version 2.0

import tenacity
import time

from sqlalchemy.orm import exc as db_exceptions
from oslo_config import cfg
from oslo_log import log as logging
from taskflow.listeners import logging as tf_logging

from octavia.common import base_taskflow
from octavia.common import constants
from octavia.db import api as db_apis
from octavia.db import repositories as repo

from octavia_loxilb_driver.controller.worker.flows import loadbalancer_flows
from octavia_loxilb_driver.controller.worker.flows import listener_flows
from octavia_loxilb_driver.controller.worker.flows import pool_flows
from octavia_loxilb_driver.controller.worker.flows import member_flows
from octavia_loxilb_driver.controller.worker.flows import healthmonitor_flows
from octavia_loxilb_driver.controller.worker.flows import l7policy_flows
from octavia_loxilb_driver.controller.worker.flows import l7rule_flows
from octavia_loxilb_driver.common import constants as loxilb_constants
from octavia_loxilb_driver.common import exceptions
from octavia_loxilb_driver.common import loxilb_network_config
from octavia_loxilb_driver.common import network_utils
from octavia_loxilb_driver.common import openstack_sdk_utils

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

# Retry configuration
RETRY_ATTEMPTS = 3
RETRY_INITIAL_DELAY = 1
RETRY_BACKOFF = 2
RETRY_MAX = 30


class LoxiLBControllerWorker(base_taskflow.BaseTaskFlowEngine):
    """Enhanced LoxiLB Controller Worker."""

    def __init__(self):
        # Initialize repositories
        self._lb_repo = repo.LoadBalancerRepository()
        self._listener_repo = repo.ListenerRepository()
        self._pool_repo = repo.PoolRepository()
        self._member_repo = repo.MemberRepository()
        self._health_mon_repo = repo.HealthMonitorRepository()
        self._l7policy_repo = repo.L7PolicyRepository()
        self._l7rule_repo = repo.L7RuleRepository()
        
        # Initialize flows
        self._lb_flows = loadbalancer_flows.LoadBalancerFlows()
        self._listener_flows = listener_flows.ListenerFlows()
        self._pool_flows = pool_flows.PoolFlows()
        self._member_flows = member_flows.MemberFlows()
        self._health_monitor_flows = healthmonitor_flows.HealthMonitorFlows()
        self._l7policy_flows = l7policy_flows.L7PolicyFlows()
        self._l7rule_flows = l7rule_flows.L7RuleFlows()
        
        super().__init__()

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(db_exceptions.NoResultFound),
        wait=tenacity.wait_incrementing(
            RETRY_INITIAL_DELAY, RETRY_BACKOFF, RETRY_MAX),
        stop=tenacity.stop_after_attempt(RETRY_ATTEMPTS))
    def create_load_balancer(self, load_balancer_id, vip_subnet_id, flavor=None):
        """Creates a load balancer.

        :param load_balancer_id: ID of the load balancer to create
        :param flavor: Optional flavor data
        :returns: None
        :raises NoResultFound: Unable to find the object
        """
        LOG.info("Controller worker processing create request for load balancer %s", load_balancer_id)
        lb = self._lb_repo.get(db_apis.get_session(), id=load_balancer_id)
        if not lb:
            LOG.warning('Failed to fetch load balancer %s from DB. Retrying for up to '
                       '60 seconds.', load_balancer_id)
            raise db_exceptions.NoResultFound

        topology = CONF.loxilb.default_topology or 'SINGLE'
        
        try:
            create_lb_tf = self.taskflow_load(
                self._lb_flows.get_create_load_balancer_flow(
                    topology=topology, 
                    listeners=lb.listeners, 
                    pools=lb.pools
                ),
                store={
                    constants.LOADBALANCER: lb,
                    constants.FLAVOR: flavor,
                    'topology': topology,
                    constants.VIP_SUBNET_ID: vip_subnet_id,
                }
            )

            with tf_logging.DynamicLoggingListener(create_lb_tf, log=LOG):
                create_lb_tf.run()

        except Exception as e:
            LOG.exception("Failed to create load balancer %s", load_balancer_id)
            # Update status to ERROR
            self._lb_repo.update(
                db_apis.get_session(),
                load_balancer_id,
                provisioning_status=constants.ERROR,
                operating_status=constants.ERROR
            )
            raise

    def delete_load_balancer(self, load_balancer_id, cascade=False):
        """Deletes a load balancer.
        :param load_balancer_id: ID of the load balancer to delete
        :param cascade: If True, delete all child objects
        :returns: None
        """
        lb = self._lb_repo.get(db_apis.get_session(), id=load_balancer_id)
        
        try:
            delete_lb_tf = self.taskflow_load(
                self._lb_flows.get_delete_load_balancer_flow(cascade=cascade),
                store={
                    constants.LOADBALANCER: lb,
                    'cascade': cascade
                }
            )

            with tf_logging.DynamicLoggingListener(delete_lb_tf, log=LOG):
                delete_lb_tf.run()

        except Exception as e:
            LOG.exception("Failed to delete load balancer %s", load_balancer_id)
            # Update status to ERROR
            self._lb_repo.update(
                db_apis.get_session(),
                load_balancer_id,
                provisioning_status=constants.ERROR,
                operating_status=constants.ERROR
            )
            raise

    def update_load_balancer(self, load_balancer_id, load_balancer_updates):
        """Updates a load balancer.

        :param load_balancer_id: ID of the load balancer to update
        :param load_balancer_updates: Dict containing updated attributes
        :returns: None
        """
        try:
            lb = self._get_db_obj_until_pending_update(
                self._lb_repo, load_balancer_id)
        except tenacity.RetryError as e:
            LOG.warning('Load balancer did not go into %s in 60 seconds. '
                       'This either due to an in-progress Octavia upgrade '
                       'or an overloaded and failing database. Assuming '
                       'an upgrade is in progress and continuing.',
                       constants.PENDING_UPDATE)
            lb = e.last_attempt.result()

        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            update_lb_tf = self.taskflow_load(
                self._lb_flows.get_update_load_balancer_flow(topology),
                store={
                    constants.LOADBALANCER: lb,
                    constants.UPDATE_DICT: load_balancer_updates
                }
            )

            with tf_logging.DynamicLoggingListener(update_lb_tf, log=LOG):
                update_lb_tf.run()

        except Exception as e:
            LOG.exception("Failed to update load balancer %s", load_balancer_id)
            self._lb_repo.update(
                db_apis.get_session(),
                load_balancer_id,
                provisioning_status=constants.ERROR
            )
            raise

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(db_exceptions.NoResultFound),
        wait=tenacity.wait_incrementing(
            RETRY_INITIAL_DELAY, RETRY_BACKOFF, RETRY_MAX),
        stop=tenacity.stop_after_attempt(RETRY_ATTEMPTS))
    def create_listener(self, listener_id):
        """Creates a listener.

        :param listener_id: ID of the listener to create
        :returns: None
        :raises NoResultFound: Unable to find the object
        """
        listener = self._listener_repo.get(db_apis.get_session(), id=listener_id)
        if not listener:
            LOG.warning('Failed to fetch listener %s from DB. Retrying for up to '
                       '60 seconds.', listener_id)
            raise db_exceptions.NoResultFound

        load_balancer = listener.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            create_listener_tf = self.taskflow_load(
                self._listener_flows.get_create_listener_flow(topology),
                store={
                    constants.LOADBALANCER: load_balancer,
                    constants.LISTENER: listener
                }
            )

            with tf_logging.DynamicLoggingListener(create_listener_tf, log=LOG):
                create_listener_tf.run()

        except Exception as e:
            LOG.exception("Failed to create listener %s", listener_id)
            self._listener_repo.update(
                db_apis.get_session(),
                listener_id,
                provisioning_status=constants.ERROR,
                operating_status=constants.ERROR
            )
            raise

    def delete_listener(self, listener_id):
        """Deletes a listener.

        :param listener_id: ID of the listener to delete
        :returns: None
        """
        LOG.info("Controller worker processing delete request for listener %s", listener_id)
        
        try:
            # Try to get the listener from the database
            session = db_apis.get_session()
            try:
                listener = self._listener_repo.get(session, id=listener_id)
                load_balancer = listener.load_balancer
                LOG.info("Found listener %s for loadbalancer %s", listener_id, load_balancer.id)
            except db_exceptions.NoResultFound:
                LOG.warning("Listener %s not found in database - may have been already deleted", listener_id)
                # If the listener doesn't exist in the database, we still need to clean up LoxiLB resources
                # This is a recovery path for orphaned LoxiLB resources
                from octavia_loxilb_driver.driver import listener_driver
                from octavia_loxilb_driver.api import api_client
                from octavia_loxilb_driver.resource_mapping import mapper
                from octavia_loxilb_driver.common import config
                
                # Initialize components needed for cleanup
                config.register_opts(CONF)
                loxilb_config = CONF.loxilb
                api_client_instance = api_client.LoxiLBAPIClient(loxilb_config)
                resource_mapper = mapper.ResourceMapper(loxilb_config)
                
                # Create a listener driver instance for cleanup
                cleanup_driver = listener_driver.ListenerDriver(
                    api_client_instance, resource_mapper, loxilb_config
                )
                
                # Attempt cleanup with just the ID
                LOG.info("Attempting to clean up any orphaned LoxiLB resources for listener %s", listener_id)
                cleanup_driver.delete({"id": listener_id, "listener_id": listener_id})
                return
            
            # If we get here, we found the listener in the database
            topology = CONF.loxilb.default_topology or 'SINGLE'
            
            delete_listener_tf = self.taskflow_load(
                self._listener_flows.get_delete_listener_flow(topology),
                store={
                    constants.LOADBALANCER: load_balancer,
                    constants.LISTENER: listener
                }
            )

            with tf_logging.DynamicLoggingListener(delete_listener_tf, log=LOG):
                delete_listener_tf.run()
                LOG.info("Successfully deleted listener %s via taskflow", listener_id)

        except Exception as e:
            LOG.exception("Failed to delete listener %s: %s", listener_id, str(e))
            try:
                self._listener_repo.update(
                    db_apis.get_session(),
                    listener_id,
                    provisioning_status=constants.ERROR
                )
            except Exception as update_ex:
                LOG.warning("Could not update listener status to ERROR: %s", str(update_ex))
            raise

    def update_listener(self, listener_id, listener_updates):
        """Updates a listener.

        :param listener_id: ID of the listener to update
        :param listener_updates: Dict containing updated attributes
        :returns: None
        """
        try:
            listener = self._get_db_obj_until_pending_update(
                self._listener_repo, listener_id)
        except tenacity.RetryError as e:
            LOG.warning('Listener did not go into %s in 60 seconds.',
                       constants.PENDING_UPDATE)
            listener = e.last_attempt.result()

        load_balancer = listener.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            update_listener_tf = self.taskflow_load(
                self._listener_flows.get_update_listener_flow(topology),
                store={
                    constants.LISTENER: listener,
                    constants.LOADBALANCER: load_balancer,
                    constants.UPDATE_DICT: listener_updates
                }
            )

            with tf_logging.DynamicLoggingListener(update_listener_tf, log=LOG):
                update_listener_tf.run()

        except Exception as e:
            LOG.exception("Failed to update listener %s", listener_id)
            self._listener_repo.update(
                db_apis.get_session(),
                listener_id,
                provisioning_status=constants.ERROR
            )
            raise

    # Pool operations
    #
    # These methods follow the Octavia provider driver stateless pattern:
    # - No direct access to resource mapping cache.
    # - All resource relationships and metadata are managed by the controller/worker.
    # - The pool_driver only receives explicit resource objects via method arguments.
    # - The flow store injects pool, listeners, and load balancer objects for correct orchestration.
    #
    # This ensures statelessness, maintainability, and error-free orchestration for pool operations.
    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(db_exceptions.NoResultFound),
        wait=tenacity.wait_incrementing(
            RETRY_INITIAL_DELAY, RETRY_BACKOFF, RETRY_MAX),
        stop=tenacity.stop_after_attempt(RETRY_ATTEMPTS))
    def create_pool(self, pool_id):
        """Creates a pool.

        :param pool_id: ID of the pool to create
        :returns: None
        :raises NoResultFound: Unable to find the object
        """
        pool = self._pool_repo.get(db_apis.get_session(), id=pool_id)
        if not pool:
            LOG.warning('Failed to fetch pool %s from DB. Retrying for up to '
                       '60 seconds.', pool_id)
            raise db_exceptions.NoResultFound

        listeners = pool.listeners
        listener = listeners[0] if listeners else None
        load_balancer = pool.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            create_pool_tf = self.taskflow_load(
                self._pool_flows.get_create_pool_flow(topology),
                store={
                    constants.POOL: pool,
                    constants.LISTENERS: listeners,
                    constants.LISTENER: listener,
                    constants.LOADBALANCER: load_balancer
                }
            )

            with tf_logging.DynamicLoggingListener(create_pool_tf, log=LOG):
                create_pool_tf.run()

        except Exception as e:
            LOG.exception("Failed to create pool %s", pool_id)
            self._pool_repo.update(
                db_apis.get_session(),
                pool_id,
                provisioning_status=constants.ERROR,
                operating_status=constants.ERROR
            )
            raise

    def delete_pool(self, pool_id):
        """Deletes a pool.

        :param pool_id: ID of the pool to delete
        :returns: None
        """
        pool = self._pool_repo.get(db_apis.get_session(), id=pool_id)
        load_balancer = pool.load_balancer
        listeners = pool.listeners
        listener = listeners[0] if listeners else None
        members = pool.members
        health_monitor = pool.health_monitor
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            delete_pool_tf = self.taskflow_load(
                self._pool_flows.get_delete_pool_flow(),
                store={
                    constants.POOL: pool,
                    constants.LISTENERS: listeners,
                    constants.LISTENER: listener,
                    constants.LOADBALANCER: load_balancer,
                    constants.HEALTH_MON: health_monitor
                }
            )

            with tf_logging.DynamicLoggingListener(delete_pool_tf, log=LOG):
                delete_pool_tf.run()

        except Exception as e:
            LOG.exception("Failed to delete pool %s", pool_id)
            self._pool_repo.update(
                db_apis.get_session(),
                pool_id,
                provisioning_status=constants.ERROR
            )
            raise

    def update_pool(self, pool_id, pool_updates):
        """Updates a pool.

        :param pool_id: ID of the pool to update
        :param pool_updates: Dict containing updated attributes
        :returns: None
        """
        try:
            pool = self._get_db_obj_until_pending_update(
                self._pool_repo, pool_id)
        except tenacity.RetryError as e:
            LOG.warning('Pool did not go into %s in 60 seconds.',
                       constants.PENDING_UPDATE)
            pool = e.last_attempt.result()

        listeners = pool.listeners
        listener = listeners[0] if listeners else None
        load_balancer = pool.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            update_pool_tf = self.taskflow_load(
                self._pool_flows.get_update_pool_flow(topology),
                store={
                    constants.POOL: pool,
                    constants.LISTENERS: listeners,
                    constants.LISTENER: listener,
                    constants.LOADBALANCER: load_balancer,
                    constants.UPDATE_DICT: pool_updates
                }
            )

            with tf_logging.DynamicLoggingListener(update_pool_tf, log=LOG):
                update_pool_tf.run()

        except Exception as e:
            LOG.exception("Failed to update pool %s", pool_id)
            self._pool_repo.update(
                db_apis.get_session(),
                pool_id,
                provisioning_status=constants.ERROR
            )
            raise

    # Member operations
    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(db_exceptions.NoResultFound),
        wait=tenacity.wait_incrementing(
            RETRY_INITIAL_DELAY, RETRY_BACKOFF, RETRY_MAX),
        stop=tenacity.stop_after_attempt(RETRY_ATTEMPTS))
    def create_member(self, member_id, subnet_id=None, pool_id=None, loadbalancer_id=None):
        """Creates a pool member.

        :param member_id: ID of the member to create
        :param subnet_id: ID of the subnet where the member is located
        :param pool_id: ID of the pool
        :param loadbalancer_id: ID of the load balancer (optional, will be resolved from pool if not provided)
        :returns: None
        :raises NoResultFound: Unable to find the object
        """
        member = self._member_repo.get(db_apis.get_session(), id=member_id)
        if not member:
            LOG.warning('Failed to fetch member %s from DB. Retrying for up to 60 seconds.', member_id)
            raise db_exceptions.NoResultFound

        # Resolve pool and loadbalancer from member or pool_id
        pool = member.pool if hasattr(member, 'pool') and member.pool else None
        if not pool and pool_id:
            pool = self._pool_repo.get(db_apis.get_session(), id=pool_id)
        if not pool:
            LOG.error(f"Could not resolve pool for member {member_id} (pool_id={pool_id})")
            raise db_exceptions.NoResultFound

        listeners = pool.listeners
        load_balancer = pool.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        # Resolve loadbalancer_id if not provided
        if not loadbalancer_id and load_balancer:
            loadbalancer_id = getattr(load_balancer, 'id', None)

        # If we're using management network and subnet_id is provided, ensure LoxiLB VM is attached
        # to the member's subnet for connectivity
        if CONF.loxilb.use_mgmt_network and subnet_id and loadbalancer_id:
            LOG.info(f"Ensuring LoxiLB VM for loadbalancer {loadbalancer_id} is attached to subnet {subnet_id}")
            try:
                # Get OpenStack connection
                conn = openstack_sdk_utils.get_openstack_connection()

                # Find the LoxiLB VM for this load balancer
                server = openstack_sdk_utils.get_loxilb_server_by_lb_id(conn, loadbalancer_id)

                if server:
                    # Get the network_id from the subnet_id
                    subnet = conn.network.get_subnet(subnet_id)
                    if not subnet:
                        LOG.error(f"Could not find subnet {subnet_id}")
                        raise Exception(f"Subnet {subnet_id} not found")
                    
                    network_id = subnet.network_id
                    LOG.info(f"Resolved network_id {network_id} from subnet_id {subnet_id}")
                    
                    # Check if the VM is already attached to this network
                    is_attached = False
                    for interface in conn.compute.server_interfaces(server.id):
                        if interface.net_id == network_id:
                            LOG.info(f"LoxiLB VM is already attached to network {network_id} (subnet {subnet_id})")
                            is_attached = True
                            break

                    # If not attached, attach it
                    if not is_attached:
                        LOG.info(f"Creating port on subnet {subnet_id} for LoxiLB VM {server.id}")
                        
                        # Create a port with specific subnet to ensure IP assignment
                        port_name = f"loxilb-member-port-{loadbalancer_id}-{subnet_id[:8]}"
                        port = conn.network.create_port(
                            name=port_name,
                            network_id=network_id,
                            fixed_ips=[{"subnet_id": subnet_id}],
                            device_owner="compute:nova"
                        )
                        LOG.info(f"Created port {port.id} with IP {port.fixed_ips[0]['ip_address']} on subnet {subnet_id}")
                        
                        # Attach the port to the server
                        LOG.info(f"Attaching port {port.id} to LoxiLB VM {server.id}")
                        interface = openstack_sdk_utils.attach_port_to_server(conn, server.id, port.id)

                        # Verify the attachment was successful
                        if openstack_sdk_utils.verify_interface_attached(conn, server.id, network_id):
                            LOG.info(f"Verified LoxiLB VM successfully attached to network {network_id} (subnet {subnet_id})")
                            
                            # Configure network interface using LoxiLB API (secure, no SSH required)
                            # Get the management IP of the LoxiLB server for API access
                            mgmt_ip = openstack_sdk_utils.get_server_ip(server)
                            if mgmt_ip:
                                LOG.info(f"Configuring network interface on LoxiLB VM {server.id} via API at {mgmt_ip}")
                                
                                # Get subnet information for IP configuration
                                subnet = conn.network.get_subnet(subnet_id)
                                if subnet:
                                    # Configure interface using LoxiLB API with MAC address mapping
                                    success = loxilb_network_config.configure_loxilb_interface(
                                        loxilb_ip=mgmt_ip,
                                        openstack_port=port,
                                        subnet_info=subnet,
                                        api_port=11111
                                    )
                                    
                                    if success:
                                        LOG.info(f"Successfully configured interface via LoxiLB API on {mgmt_ip}")
                                        # Wait a moment for the configuration to take effect
                                        time.sleep(5)
                                    else:
                                        LOG.warning(f"Failed to configure interface via LoxiLB API on {mgmt_ip}, but continuing")
                                else:
                                    LOG.error(f"Could not get subnet information for {subnet_id}")
                            else:
                                LOG.warning(f"Could not determine management IP for LoxiLB VM {server.id}")
                            
                            # First verify basic network connectivity
                            if network_utils.verify_interface_operational(conn, server.id, subnet_id):
                                LOG.info(f"Verified basic network connectivity on subnet {subnet_id} is operational")

                                # Then verify LoxiLB API is accessible through this interface
                                # Use the default LoxiLB API port (11111) or configure as needed
                                if network_utils.verify_loxilb_interface_operational(conn, server.id, subnet_id, loadbalancer_id, api_port=11111):
                                    LOG.info(f"Verified LoxiLB API is accessible through subnet {subnet_id}")
                                else:
                                    LOG.warning(f"LoxiLB API is not accessible through subnet {subnet_id}, but continuing with member creation")
                            else:
                                LOG.warning(f"Network connectivity on subnet {subnet_id} could not be verified, but continuing with member creation")
                        else:
                            LOG.warning(f"Could not verify LoxiLB VM attachment to subnet {subnet_id}, but continuing")
                else:
                    LOG.warning(f"Could not find LoxiLB VM for loadbalancer {loadbalancer_id}")
            except Exception as e:
                LOG.error(f"Failed to attach LoxiLB VM to subnet {subnet_id}: {e}")
                # Continue with member creation even if attachment fails

        try:
            create_member_tf = self.taskflow_load(
                self._member_flows.get_create_member_flow(topology),
                store={
                    constants.MEMBER: member,
                    constants.LISTENERS: listeners,
                    constants.LOADBALANCER: load_balancer,
                    constants.POOL: pool
                }
            )

            with tf_logging.DynamicLoggingListener(create_member_tf, log=LOG):
                create_member_tf.run()

        except Exception as e:
            LOG.exception("Failed to create member %s", member_id)
            self._member_repo.update(
                db_apis.get_session(),
                member_id,
                provisioning_status=constants.ERROR,
                operating_status=constants.ERROR
            )
            raise

    def delete_member(self, member_id, subnet_id=None, loadbalancer_id=None):
        """Deletes a pool member.

        :param member_id: ID of the member to delete
        :param subnet_id: ID of the subnet where the member is located
        :param loadbalancer_id: ID of the load balancer
        :returns: None
        """
        member = self._member_repo.get(db_apis.get_session(), id=member_id)
        pool = member.pool
        listeners = pool.listeners
        load_balancer = pool.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'
        
        # If we're using management network and subnet_id is provided, check if this is the last member
        # in this subnet and potentially detach the LoxiLB VM from the subnet
        if CONF.loxilb.use_mgmt_network and subnet_id and loadbalancer_id:
            LOG.info(f"Checking if member {member_id} is the last one in subnet {subnet_id}")
            try:
                # Check if there are other members in the same subnet
                session = db_apis.get_session()
                other_members = self._member_repo.get_all_by_pool(
                    session, pool_id=pool.id, subnet_id=subnet_id
                )
                
                # Filter out the member we're deleting
                other_members = [m for m in other_members if m.id != member_id]
                
                # If this is the last member in the subnet, consider detaching the interface
                if not other_members:
                    LOG.info(f"Member {member_id} is the last one in subnet {subnet_id}, checking for other pools")
                    
                    # Check if there are members in other pools using the same subnet
                    other_pool_members = self._member_repo.get_all(
                        session, subnet_id=subnet_id
                    )
                    other_pool_members = [m for m in other_pool_members if m.id != member_id]
                    
                    if not other_pool_members:
                        LOG.info(f"No other members in subnet {subnet_id}, considering detaching interface")
                        
                        # Get OpenStack connection
                        conn = openstack_sdk_utils.get_openstack_connection()
                        
                        # Find the LoxiLB VM for this load balancer
                        server = openstack_sdk_utils.get_loxilb_server_by_lb_id(conn, loadbalancer_id)
                        
                        if server:
                            # Find the interface for this subnet
                            for interface in conn.compute.server_interfaces(server.id):
                                if interface.net_id == subnet_id:
                                    # Don't detach if it's the management network
                                    if subnet_id != CONF.loxilb.mgmt_network_id:
                                        LOG.info(f"Detaching LoxiLB VM from subnet {subnet_id}")
                                        try:
                                            # Use the enhanced detach function with retry logic
                                            openstack_sdk_utils.detach_interface_from_server(conn, server.id, interface.id)
                                            
                                            # Verify the interface was actually detached
                                            if openstack_sdk_utils.verify_interface_detached(conn, server.id, interface.id):
                                                LOG.info(f"Verified interface {interface.id} was successfully detached")
                                                
                                                # Configure network interface using LoxiLB API (secure, no SSH required)
                                                # Get the management IP of the LoxiLB server for API access
                                                mgmt_ip = openstack_sdk_utils.get_server_ip(server)
                                                if mgmt_ip:
                                                    LOG.info(f"Configuring network interface on LoxiLB VM {server.id} via API at {mgmt_ip}")
                                                    
                                                    # Get subnet information for IP configuration
                                                    subnet = conn.network.get_subnet(subnet_id)
                                                    if subnet:
                                                        # Configure interface using LoxiLB API with MAC address mapping
                                                        success = loxilb_network_config.configure_loxilb_interface(
                                                            loxilb_ip=mgmt_ip,
                                                            openstack_port=port,
                                                            subnet_info=subnet,
                                                            api_port=11111
                                                        )
                                                        
                                                        if success:
                                                            LOG.info(f"Successfully configured interface via LoxiLB API on {mgmt_ip}")
                                                            # Wait a moment for the configuration to take effect
                                                            time.sleep(5)
                                                        else:
                                                            LOG.warning(f"Failed to configure interface via LoxiLB API on {mgmt_ip}, but continuing")
                                                    else:
                                                        LOG.error(f"Could not get subnet information for {subnet_id}")
                                                else:
                                                    LOG.warning(f"Could not determine management IP for LoxiLB VM {server.id}")
                                            else:
                                                LOG.warning(f"Could not verify interface {interface.id} was detached")
                                        except exceptions.NetworkOperationException as e:
                                            LOG.error(f"Failed to detach interface after retries: {e}")
                                            # Continue with member deletion even if detachment fails
                                    else:
                                        LOG.info(f"Not detaching management network interface")
                                    break
                        else:
                            LOG.warning(f"Could not find LoxiLB VM for loadbalancer {loadbalancer_id}")
            except Exception as e:
                LOG.error(f"Failed to check/detach LoxiLB VM from subnet {subnet_id}: {e}")
                # Continue with member deletion even if detachment fails

        try:
            delete_member_tf = self.taskflow_load(
                self._member_flows.get_delete_member_flow(topology),
                store={
                    constants.MEMBER: member,
                    constants.LISTENERS: listeners,
                    constants.LOADBALANCER: load_balancer,
                    constants.POOL: pool
                }
            )

            with tf_logging.DynamicLoggingListener(delete_member_tf, log=LOG):
                delete_member_tf.run()

        except Exception as e:
            LOG.exception("Failed to delete member %s", member_id)
            self._member_repo.update(
                db_apis.get_session(),
                member_id,
                provisioning_status=constants.ERROR
            )
            raise

    def update_member(self, member_id, member_updates):
        """Updates a pool member.

        :param member_id: ID of the member to update
        :param member_updates: Dict containing updated attributes
        :returns: None
        """
        try:
            member = self._get_db_obj_until_pending_update(
                self._member_repo, member_id)
        except tenacity.RetryError as e:
            LOG.warning('Member did not go into %s in 60 seconds.',
                       constants.PENDING_UPDATE)
            member = e.last_attempt.result()

        pool = member.pool
        listeners = pool.listeners
        load_balancer = pool.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            update_member_tf = self.taskflow_load(
                self._member_flows.get_update_member_flow(topology),
                store={
                    constants.MEMBER: member,
                    constants.LISTENERS: listeners,
                    constants.LOADBALANCER: load_balancer,
                    constants.POOL: pool,
                    constants.UPDATE_DICT: member_updates
                }
            )

            with tf_logging.DynamicLoggingListener(update_member_tf, log=LOG):
                update_member_tf.run()

        except Exception as e:
            LOG.exception("Failed to update member %s", member_id)
            self._member_repo.update(
                db_apis.get_session(),
                member_id,
                provisioning_status=constants.ERROR
            )
            raise

    def batch_update_members(self, old_member_ids, new_member_ids, updated_members):
        """Batch update pool members.

        :param old_member_ids: List of member IDs to delete
        :param new_member_ids: List of member IDs to create
        :param updated_members: List of member update dicts
        :returns: None
        """
        # Get member objects
        old_members = [self._member_repo.get(db_apis.get_session(), id=mid)
                       for mid in old_member_ids]
        new_members = [self._member_repo.get(db_apis.get_session(), id=mid)
                       for mid in new_member_ids]

        if old_members:
            pool = old_members[0].pool
        elif new_members:
            pool = new_members[0].pool
        else:
            # Updated members case
            updated_member_ids = [m.get('id') for m in updated_members]
            updated_member_models = [
                self._member_repo.get(db_apis.get_session(), id=mid)
                for mid in updated_member_ids
            ]
            pool = updated_member_models[0].pool

        listeners = pool.listeners
        load_balancer = pool.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            batch_update_members_tf = self.taskflow_load(
                self._member_flows.get_batch_update_members_flow(
                    old_members, new_members, updated_members, topology
                ),
                store={
                    constants.LISTENERS: listeners,
                    constants.LOADBALANCER: load_balancer,
                    constants.POOL: pool
                }
            )

            with tf_logging.DynamicLoggingListener(batch_update_members_tf, log=LOG):
                batch_update_members_tf.run()

        except Exception as e:
            LOG.exception("Failed to batch update members")
            # Update pool status to ERROR
            self._pool_repo.update(
                db_apis.get_session(),
                pool.id,
                provisioning_status=constants.ERROR
            )
            raise

    # Health Monitor operations
    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(db_exceptions.NoResultFound),
        wait=tenacity.wait_incrementing(
            RETRY_INITIAL_DELAY, RETRY_BACKOFF, RETRY_MAX),
        stop=tenacity.stop_after_attempt(RETRY_ATTEMPTS))
    def create_health_monitor(self, health_monitor_id):
        """Creates a health monitor.

        :param health_monitor_id: ID of the health monitor to create
        :returns: None
        :raises NoResultFound: Unable to find the object
        """
        health_mon = self._health_mon_repo.get(
            db_apis.get_session(), id=health_monitor_id)
        if not health_mon:
            LOG.warning('Failed to fetch health monitor %s from DB. Retrying for up to '
                       '60 seconds.', health_monitor_id)
            raise db_exceptions.NoResultFound

        pool = health_mon.pool
        listeners = pool.listeners
        pool.health_monitor = health_mon
        load_balancer = pool.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            create_hm_tf = self.taskflow_load(
                self._health_monitor_flows.get_create_health_monitor_flow(topology),
                store={
                    constants.HEALTH_MON: health_mon,
                    constants.POOL: pool,
                    constants.LISTENERS: listeners,
                    constants.LOADBALANCER: load_balancer
                }
            )

            with tf_logging.DynamicLoggingListener(create_hm_tf, log=LOG):
                create_hm_tf.run()

        except Exception as e:
            LOG.exception("Failed to create health monitor %s", health_monitor_id)
            self._health_mon_repo.update(
                db_apis.get_session(),
                health_monitor_id,
                provisioning_status=constants.ERROR,
                operating_status=constants.ERROR
            )
            raise

    def delete_health_monitor(self, health_monitor_id):
        """Deletes a health monitor.

        :param health_monitor_id: ID of the health monitor to delete
        :returns: None
        """
        health_mon = self._health_mon_repo.get(
            db_apis.get_session(), id=health_monitor_id)
        pool = health_mon.pool
        listeners = pool.listeners
        load_balancer = pool.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            delete_hm_tf = self.taskflow_load(
                self._health_monitor_flows.get_delete_health_monitor_flow(topology),
                store={
                    constants.HEALTH_MON: health_mon,
                    constants.POOL: pool,
                    constants.LISTENERS: listeners,
                    constants.LOADBALANCER: load_balancer
                }
            )

            with tf_logging.DynamicLoggingListener(delete_hm_tf, log=LOG):
                delete_hm_tf.run()

        except Exception as e:
            LOG.exception("Failed to delete health monitor %s", health_monitor_id)
            self._health_mon_repo.update(
                db_apis.get_session(),
                health_monitor_id,
                provisioning_status=constants.ERROR
            )
            raise

    def update_health_monitor(self, health_monitor_id, health_monitor_updates):
        """Updates a health monitor.

        :param health_monitor_id: ID of the health monitor to update
        :param health_monitor_updates: Dict containing updated attributes
        :returns: None
        """
        try:
            health_mon = self._get_db_obj_until_pending_update(
                self._health_mon_repo, health_monitor_id)
        except tenacity.RetryError as e:
            LOG.warning('Health monitor did not go into %s in 60 seconds.',
                       constants.PENDING_UPDATE)
            health_mon = e.last_attempt.result()

        pool = health_mon.pool
        listeners = pool.listeners
        pool.health_monitor = health_mon
        load_balancer = pool.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            update_hm_tf = self.taskflow_load(
                self._health_monitor_flows.get_update_health_monitor_flow(topology),
                store={
                    constants.HEALTH_MON: health_mon,
                    constants.POOL: pool,
                    constants.LISTENERS: listeners,
                    constants.LOADBALANCER: load_balancer,
                    constants.UPDATE_DICT: health_monitor_updates
                }
            )

            with tf_logging.DynamicLoggingListener(update_hm_tf, log=LOG):
                update_hm_tf.run()

        except Exception as e:
            LOG.exception("Failed to update health monitor %s", health_monitor_id)
            self._health_mon_repo.update(
                db_apis.get_session(),
                health_monitor_id,
                provisioning_status=constants.ERROR
            )
            raise

    # L7 Policy operations
    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(db_exceptions.NoResultFound),
        wait=tenacity.wait_incrementing(
            RETRY_INITIAL_DELAY, RETRY_BACKOFF, RETRY_MAX),
        stop=tenacity.stop_after_attempt(RETRY_ATTEMPTS))
    def create_l7policy(self, l7policy_id):
        """Creates an L7 policy.

        :param l7policy_id: ID of the L7 policy to create
        :returns: None
        :raises NoResultFound: Unable to find the object
        """
        l7policy = self._l7policy_repo.get(db_apis.get_session(), id=l7policy_id)
        if not l7policy:
            LOG.warning('Failed to fetch L7 policy %s from DB. Retrying for up to '
                       '60 seconds.', l7policy_id)
            raise db_exceptions.NoResultFound

        listener = l7policy.listener
        load_balancer = listener.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            create_l7policy_tf = self.taskflow_load(
                self._l7policy_flows.get_create_l7policy_flow(topology),
                store={
                    constants.L7POLICY: l7policy,
                    constants.LISTENER: listener,
                    constants.LOADBALANCER: load_balancer
                }
            )

            with tf_logging.DynamicLoggingListener(create_l7policy_tf, log=LOG):
                create_l7policy_tf.run()

        except Exception as e:
            LOG.exception("Failed to create L7 policy %s", l7policy_id)
            self._l7policy_repo.update(
                db_apis.get_session(),
                l7policy_id,
                provisioning_status=constants.ERROR,
                operating_status=constants.ERROR
            )
            raise

    def delete_l7policy(self, l7policy_id):
        """Deletes an L7 policy.

        :param l7policy_id: ID of the L7 policy to delete
        :returns: None
        """
        l7policy = self._l7policy_repo.get(db_apis.get_session(), id=l7policy_id)
        listener = l7policy.listener
        load_balancer = listener.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            delete_l7policy_tf = self.taskflow_load(
                self._l7policy_flows.get_delete_l7policy_flow(cascade=True),
                store={
                    constants.L7POLICY: l7policy,
                    constants.LISTENER: listener,
                    constants.LOADBALANCER: load_balancer
                }
            )

            with tf_logging.DynamicLoggingListener(delete_l7policy_tf, log=LOG):
                delete_l7policy_tf.run()

        except Exception as e:
            LOG.exception("Failed to delete L7 policy %s", l7policy_id)
            self._l7policy_repo.update(
                db_apis.get_session(),
                l7policy_id,
                provisioning_status=constants.ERROR
            )
            raise

    def update_l7policy(self, l7policy_id, l7policy_updates):
        """Updates an L7 policy.

        :param l7policy_id: ID of the L7 policy to update
        :param l7policy_updates: Dict containing updated attributes
        :returns: None
        """
        try:
            l7policy = self._get_db_obj_until_pending_update(
                self._l7policy_repo, l7policy_id)
        except tenacity.RetryError as e:
            LOG.warning('L7 policy did not go into %s in 60 seconds.',
                       constants.PENDING_UPDATE)
            l7policy = e.last_attempt.result()

        listener = l7policy.listener
        load_balancer = listener.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            update_l7policy_tf = self.taskflow_load(
                self._l7policy_flows.get_update_l7policy_flow(),
                store={
                    constants.L7POLICY: l7policy,
                    constants.LISTENER: listener,
                    constants.LOADBALANCER: load_balancer,
                    constants.UPDATE_DICT: l7policy_updates
                }
            )

            with tf_logging.DynamicLoggingListener(update_l7policy_tf, log=LOG):
                update_l7policy_tf.run()

        except Exception as e:
            LOG.exception("Failed to update L7 policy %s", l7policy_id)
            self._l7policy_repo.update(
                db_apis.get_session(),
                l7policy_id,
                provisioning_status=constants.ERROR
            )
            raise

    # L7 Rule operations
    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(db_exceptions.NoResultFound),
        wait=tenacity.wait_incrementing(
            RETRY_INITIAL_DELAY, RETRY_BACKOFF, RETRY_MAX),
        stop=tenacity.stop_after_attempt(RETRY_ATTEMPTS))
    def create_l7rule(self, l7rule_id):
        """Creates an L7 rule.

        :param l7rule_id: ID of the L7 rule to create
        :returns: None
        :raises NoResultFound: Unable to find the object
        """
        l7rule = self._l7rule_repo.get(db_apis.get_session(), id=l7rule_id)
        if not l7rule:
            LOG.warning('Failed to fetch L7 rule %s from DB. Retrying for up to '
                       '60 seconds.', l7rule_id)
            raise db_exceptions.NoResultFound

        l7policy = l7rule.l7policy
        listener = l7policy.listener
        load_balancer = listener.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            create_l7rule_tf = self.taskflow_load(
                self._l7rule_flows.get_create_l7rule_flow(topology),
                store={
                    constants.L7RULE: l7rule,
                    constants.L7POLICY: l7policy,
                    constants.LISTENER: listener,
                    constants.LOADBALANCER: load_balancer
                }
            )

            with tf_logging.DynamicLoggingListener(create_l7rule_tf, log=LOG):
                create_l7rule_tf.run()

        except Exception as e:
            LOG.exception("Failed to create L7 rule %s", l7rule_id)
            self._l7rule_repo.update(
                db_apis.get_session(),
                l7rule_id,
                provisioning_status=constants.ERROR,
                operating_status=constants.ERROR
            )
            raise

    def delete_l7rule(self, l7rule_id):
        """Deletes an L7 rule.

        :param l7rule_id: ID of the L7 rule to delete
        :returns: None
        """
        l7rule = self._l7rule_repo.get(db_apis.get_session(), id=l7rule_id)
        l7policy = l7rule.l7policy
        listener = l7policy.listener
        load_balancer = listener.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            delete_l7rule_tf = self.taskflow_load(
                self._l7rule_flows.get_delete_l7rule_flow(),
                store={
                    constants.L7RULE: l7rule,
                    constants.L7POLICY: l7policy,
                    constants.LISTENER: listener,
                    constants.LOADBALANCER: load_balancer
                }
            )

            with tf_logging.DynamicLoggingListener(delete_l7rule_tf, log=LOG):
                delete_l7rule_tf.run()

        except Exception as e:
            LOG.exception("Failed to delete L7 rule %s", l7rule_id)
            self._l7rule_repo.update(
                db_apis.get_session(),
                l7rule_id,
                provisioning_status=constants.ERROR
            )
            raise

    def update_l7rule(self, l7rule_id, l7rule_updates):
        """Updates an L7 rule.

        :param l7rule_id: ID of the L7 rule to update
        :param l7rule_updates: Dict containing updated attributes
        :returns: None
        """
        try:
            l7rule = self._get_db_obj_until_pending_update(
                self._l7rule_repo, l7rule_id)
        except tenacity.RetryError as e:
            LOG.warning('L7 rule did not go into %s in 60 seconds.',
                       constants.PENDING_UPDATE)
            l7rule = e.last_attempt.result()

        l7policy = l7rule.l7policy
        listener = l7policy.listener
        load_balancer = listener.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            update_l7rule_tf = self.taskflow_load(
                self._l7rule_flows.get_update_l7rule_flow(),
                store={
                    constants.L7RULE: l7rule,
                    constants.L7POLICY: l7policy,
                    constants.LISTENER: listener,
                    constants.LOADBALANCER: load_balancer,
                    constants.UPDATE_DICT: l7rule_updates
                }
            )

            with tf_logging.DynamicLoggingListener(update_l7rule_tf, log=LOG):
                update_l7rule_tf.run()

        except Exception as e:
            LOG.exception("Failed to update L7 rule %s", l7rule_id)
            self._l7rule_repo.update(
                db_apis.get_session(),
                l7rule_id,
                provisioning_status=constants.ERROR
            )
            raise

    def update_health_monitor(self, health_monitor_id, health_monitor_updates):
        """Updates a health monitor.

        :param health_monitor_id: ID of the health monitor to update
        :param health_monitor_updates: Dict containing updated attributes
        :returns: None
        """
        try:
            health_mon = self._get_db_obj_until_pending_update(
                self._health_mon_repo, health_monitor_id)
        except tenacity.RetryError as e:
            LOG.warning('Health monitor did not go into %s in 60 seconds.',
                       constants.PENDING_UPDATE)
            health_mon = e.last_attempt.result()

        pool = health_mon.pool
        listeners = pool.listeners
        pool.health_monitor = health_mon
        load_balancer = pool.load_balancer
        topology = CONF.loxilb.default_topology or 'SINGLE'

        try:
            update_hm_tf = self.taskflow_load(
                self._health_monitor_flows.get_update_health_monitor_flow(topology),
                store={
                    constants.HEALTH_MON: health_mon,
                    constants.POOL: pool,
                    constants.LISTENERS: listeners,
                    constants.LOADBALANCER: load_balancer,
                    constants.UPDATE_DICT: health_monitor_updates
                }
            )

            with tf_logging.DynamicLoggingListener(update_hm_tf, log=LOG):
                update_hm_tf.run()

        except Exception as e:
            LOG.exception("Failed to update health monitor %s", health_monitor_id)
            self._health_mon_repo.update(
                db_apis.get_session(),
                health_monitor_id,
                provisioning_status=constants.ERROR
            )
            raise

    def _get_db_obj_until_pending_update(self, repo, obj_id):
        """Helper method to get database object until it's in pending update state."""
        return repo.get(db_apis.get_session(), id=obj_id)