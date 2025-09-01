# Copyright 2025 LoxiLB
# Licensed under the Apache License, Version 2.0

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from octavia.common import constants as octavia_constants
from octavia_loxilb_driver.controller.controller_worker import LoxiLBControllerWorker

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Endpoints(object):
    """RPC endpoints for LoxiLB controller worker."""

    # Set the namespace for RPC - must match the namespace used in provider_driver.py
    target = messaging.Target(namespace=octavia_constants.RPC_NAMESPACE_CONTROLLER_AGENT, version='1.0')

    def __init__(self):
        """Initialize the endpoints."""
        self.worker = LoxiLBControllerWorker()

    # Load Balancer endpoints
    def create_load_balancer(self, context, **kwargs):
        """Create a load balancer.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to create load balancer")
        load_balancer_id = kwargs.get('load_balancer_id')
        vip_subnet_id = kwargs.get('vip_subnet_id')
        flavor = kwargs.get('flavor')
        
        try:
            self.worker.create_load_balancer(load_balancer_id, vip_subnet_id, flavor)
            LOG.info("Successfully created load balancer %s", load_balancer_id)
        except Exception as e:
            LOG.exception("Failed to create load balancer %s: %s", 
                         load_balancer_id, str(e))
            raise

    def delete_load_balancer(self, context, **kwargs):
        """Delete a load balancer.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to delete load balancer")
        load_balancer_id = kwargs.get('loadbalancer_id')
        cascade = kwargs.get('cascade', False)
        
        try:
            self.worker.delete_load_balancer(load_balancer_id, cascade)
            LOG.info("Successfully deleted load balancer %s", load_balancer_id)
        except Exception as e:
            LOG.exception("Failed to delete load balancer %s: %s", 
                         load_balancer_id, str(e))
            raise

    def update_load_balancer(self, context, **kwargs):
        """Update a load balancer.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to update load balancer")
        load_balancer_id = kwargs.get('loadbalancer_id')
        load_balancer_updates = kwargs.get('loadbalancer_updates', {})
        
        try:
            self.worker.update_load_balancer(load_balancer_id, load_balancer_updates)
            LOG.info("Successfully updated load balancer %s", load_balancer_id)
        except Exception as e:
            LOG.exception("Failed to update load balancer %s: %s", 
                         load_balancer_id, str(e))
            raise

    # Listener endpoints
    def create_listener(self, context, **kwargs):
        """Create a listener.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to create listener")
        listener_id = kwargs.get('listener_id')
        
        try:
            self.worker.create_listener(listener_id)
            LOG.info("Successfully created listener %s", listener_id)
        except Exception as e:
            LOG.exception("Failed to create listener %s: %s", listener_id, str(e))
            raise

    def delete_listener(self, context, **kwargs):
        """Delete a listener.
        
        :param context: RPC context
        :param kwargs: Additional arguments including listener_id and optionally loadbalancer_id
        :returns: None
        """
        LOG.info("Received RPC call to delete listener")
        listener_id = kwargs.get('listener_id')
        loadbalancer_id = kwargs.get('loadbalancer_id')
        
        if not listener_id:
            LOG.error("Cannot delete listener: No listener_id provided in RPC call")
            raise ValueError("listener_id is required for delete_listener RPC call")
            
        LOG.info("Processing delete request for listener %s (loadbalancer_id: %s)", 
                 listener_id, loadbalancer_id or 'not provided')
        
        try:
            self.worker.delete_listener(listener_id)
            LOG.info("Successfully deleted listener %s", listener_id)
        except Exception as e:
            LOG.exception("Failed to delete listener %s: %s", listener_id, str(e))
            raise

    def update_listener(self, context, **kwargs):
        """Update a listener.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to update listener")
        listener_id = kwargs.get('listener_id')
        listener_updates = kwargs.get('listener_updates', {})
        
        try:
            self.worker.update_listener(listener_id, listener_updates)
            LOG.info("Successfully updated listener %s", listener_id)
        except Exception as e:
            LOG.exception("Failed to update listener %s: %s", listener_id, str(e))
            raise

    # Pool endpoints
    def create_pool(self, context, **kwargs):
        """Create a pool.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to create pool")
        pool_id = kwargs.get('pool_id')
        
        try:
            self.worker.create_pool(pool_id)
            LOG.info("Successfully created pool %s", pool_id)
        except Exception as e:
            LOG.exception("Failed to create pool %s: %s", pool_id, str(e))
            raise

    def delete_pool(self, context, **kwargs):
        """Delete a pool.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to delete pool")
        pool_id = kwargs.get('pool_id')
        
        try:
            self.worker.delete_pool(pool_id)
            LOG.info("Successfully deleted pool %s", pool_id)
        except Exception as e:
            LOG.exception("Failed to delete pool %s: %s", pool_id, str(e))
            raise

    def update_pool(self, context, **kwargs):
        """Update a pool.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to update pool")
        pool_id = kwargs.get('pool_id')
        pool_updates = kwargs.get('pool_updates', {})
        
        try:
            self.worker.update_pool(pool_id, pool_updates)
            LOG.info("Successfully updated pool %s", pool_id)
        except Exception as e:
            LOG.exception("Failed to update pool %s: %s", pool_id, str(e))
            raise

    # Member endpoints
    def create_member(self, context, **kwargs):
        """Create a member.
        
        :param context: RPC context
        :param kwargs: Additional arguments including subnet_id and loadbalancer_id
        :returns: None
        """
        LOG.info("Received RPC call to create member")
        member_id = kwargs.get('member_id')
        subnet_id = kwargs.get('subnet_id')
        pool_id = kwargs.get('pool_id')
        
        LOG.info("Creating member %s in subnet %s for pool %s", 
                 member_id, subnet_id, pool_id)
        
        try:
            # Pass the additional parameters to the worker
            self.worker.create_member(member_id, subnet_id=subnet_id, pool_id=pool_id)
            LOG.info("Successfully created member %s", member_id)
        except Exception as e:
            LOG.exception("Failed to create member %s: %s", member_id, str(e))
            raise

    def delete_member(self, context, **kwargs):
        """Delete a member.
        
        :param context: RPC context
        :param kwargs: Additional arguments including subnet_id and loadbalancer_id
        :returns: None
        """
        LOG.info("Received RPC call to delete member")
        member_id = kwargs.get('member_id')
        subnet_id = kwargs.get('subnet_id')
        loadbalancer_id = kwargs.get('loadbalancer_id')
        
        LOG.info("Deleting member %s from subnet %s for loadbalancer %s", 
                 member_id, subnet_id, loadbalancer_id)
        
        try:
            # Pass the additional parameters to the worker
            self.worker.delete_member(member_id, subnet_id=subnet_id, loadbalancer_id=loadbalancer_id)
            LOG.info("Successfully deleted member %s", member_id)
        except Exception as e:
            LOG.exception("Failed to delete member %s: %s", member_id, str(e))
            raise

    def update_member(self, context, **kwargs):
        """Update a member.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to update member")
        member_id = kwargs.get('member_id')
        member_updates = kwargs.get('member_updates', {})
        
        try:
            self.worker.update_member(member_id, member_updates)
            LOG.info("Successfully updated member %s", member_id)
        except Exception as e:
            LOG.exception("Failed to update member %s: %s", member_id, str(e))
            raise

    def batch_update_members(self, context, **kwargs):
        """Batch update members.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to batch update members")
        old_member_ids = kwargs.get('old_member_ids', [])
        new_member_ids = kwargs.get('new_member_ids', [])
        updated_members = kwargs.get('updated_members', [])
        
        try:
            self.worker.batch_update_members(old_member_ids, new_member_ids, updated_members)
            LOG.info("Successfully batch updated members")
        except Exception as e:
            LOG.exception("Failed to batch update members: %s", str(e))
            raise

    # Health Monitor endpoints
    def create_health_monitor(self, context, **kwargs):
        """Create a health monitor.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to create health monitor")
        health_monitor_id = kwargs.get('healthmonitor_id')
        
        try:
            self.worker.create_health_monitor(health_monitor_id)
            LOG.info("Successfully created health monitor %s", health_monitor_id)
        except Exception as e:
            LOG.exception("Failed to create health monitor %s: %s", 
                         health_monitor_id, str(e))
            raise

    def delete_health_monitor(self, context, **kwargs):
        """Delete a health monitor.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to delete health monitor")
        health_monitor_id = kwargs.get('healthmonitor_id')
        
        try:
            self.worker.delete_health_monitor(health_monitor_id)
            LOG.info("Successfully deleted health monitor %s", health_monitor_id)
        except Exception as e:
            LOG.exception("Failed to delete health monitor %s: %s", 
                         health_monitor_id, str(e))
            raise

    def update_health_monitor(self, context, **kwargs):
        """Update a health monitor.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to update health monitor")
        health_monitor_id = kwargs.get('healthmonitor_id')
        health_monitor_updates = kwargs.get('healthmonitor_updates', {})
        
        try:
            self.worker.update_health_monitor(health_monitor_id, health_monitor_updates)
            LOG.info("Successfully updated health monitor %s", health_monitor_id)
        except Exception as e:
            LOG.exception("Failed to update health monitor %s: %s", 
                         health_monitor_id, str(e))
            raise

    # L7 Policy endpoints (add if needed)
    def create_l7policy(self, context, **kwargs):
        """Create an L7 policy.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to create l7policy")
        l7policy_id = kwargs.get('l7policy_id')
        
        try:
            # Implement when L7 policy support is added
            # self.worker.create_l7policy(l7policy_id)
            LOG.info("L7 policy creation not yet implemented")
            raise NotImplementedError("L7 policy creation not yet implemented")
        except Exception as e:
            LOG.exception("Failed to create l7policy %s: %s", l7policy_id, str(e))
            raise

    def delete_l7policy(self, context, **kwargs):
        """Delete an L7 policy.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to delete l7policy")
        l7policy_id = kwargs.get('l7policy_id')
        
        try:
            # Implement when L7 policy support is added
            # self.worker.delete_l7policy(l7policy_id)
            LOG.info("L7 policy deletion not yet implemented")
            raise NotImplementedError("L7 policy deletion not yet implemented")
        except Exception as e:
            LOG.exception("Failed to delete l7policy %s: %s", l7policy_id, str(e))
            raise

    def update_l7policy(self, context, **kwargs):
        """Update an L7 policy.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to update l7policy")
        l7policy_id = kwargs.get('l7policy_id')
        l7policy_updates = kwargs.get('l7policy_updates', {})
        
        try:
            # Implement when L7 policy support is added
            # self.worker.update_l7policy(l7policy_id, l7policy_updates)
            LOG.info("L7 policy update not yet implemented")
            raise NotImplementedError("L7 policy update not yet implemented")
        except Exception as e:
            LOG.exception("Failed to update l7policy %s: %s", l7policy_id, str(e))
            raise

    # L7 Rule endpoints (add if needed)
    def create_l7rule(self, context, **kwargs):
        """Create an L7 rule.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to create l7rule")
        l7rule_id = kwargs.get('l7rule_id')
        
        try:
            # Implement when L7 rule support is added
            # self.worker.create_l7rule(l7rule_id)
            LOG.info("L7 rule creation not yet implemented")
            raise NotImplementedError("L7 rule creation not yet implemented")
        except Exception as e:
            LOG.exception("Failed to create l7rule %s: %s", l7rule_id, str(e))
            raise

    def delete_l7rule(self, context, **kwargs):
        """Delete an L7 rule.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to delete l7rule")
        l7rule_id = kwargs.get('l7rule_id')
        
        try:
            # Implement when L7 rule support is added
            # self.worker.delete_l7rule(l7rule_id)
            LOG.info("L7 rule deletion not yet implemented")
            raise NotImplementedError("L7 rule deletion not yet implemented")
        except Exception as e:
            LOG.exception("Failed to delete l7rule %s: %s", l7rule_id, str(e))
            raise

    def update_l7rule(self, context, **kwargs):
        """Update an L7 rule.
        
        :param context: RPC context
        :param kwargs: Additional arguments
        :returns: None
        """
        LOG.info("Received RPC call to update l7rule")
        l7rule_id = kwargs.get('l7rule_id')
        l7rule_updates = kwargs.get('l7rule_updates', {})
        
        try:
            # Implement when L7 rule support is added
            # self.worker.update_l7rule(l7rule_id, l7rule_updates)
            LOG.info("L7 rule update not yet implemented")
            raise NotImplementedError("L7 rule update not yet implemented")
        except Exception as e:
            LOG.exception("Failed to update l7rule %s: %s", l7rule_id, str(e))
            raise