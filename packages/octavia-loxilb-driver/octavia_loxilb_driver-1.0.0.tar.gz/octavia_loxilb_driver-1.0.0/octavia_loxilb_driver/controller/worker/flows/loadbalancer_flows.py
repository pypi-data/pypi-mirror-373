# Copyright 2025 LoxiLB
# Licensed under the Apache License, Version 2.0

from oslo_config import cfg
from oslo_log import log as logging
from taskflow.patterns import linear_flow
from taskflow.patterns import unordered_flow

from octavia.common import constants
from octavia.common import exceptions
# Use our custom notification tasks instead of the default Octavia ones
from octavia_loxilb_driver.controller.worker.tasks import database_tasks
from octavia_loxilb_driver.controller.worker.tasks import loxilb_tasks
from octavia_loxilb_driver.controller.worker.tasks import notification_tasks
from octavia_loxilb_driver.controller.worker.flows import listener_flows
from octavia_loxilb_driver.controller.worker.flows import pool_flows

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class LoadBalancerFlows(object):
    """Load balancer flows for LoxiLB driver."""

    def __init__(self):
        self._listener_flows = listener_flows.ListenerFlows()
        self._pool_flows = pool_flows.PoolFlows()

    def get_create_load_balancer_flow(self, topology='SINGLE', listeners=None, pools=None):
        """Create a load balancer flow.
        
        :param topology: Load balancer topology
        :param listeners: List of listeners to create with the load balancer
        :param pools: List of pools to create with the load balancer
        :returns: The flow for creating a load balancer
        """
        f_name = 'loxilb-create-loadbalancer-flow'
        create_lb_flow = linear_flow.Flow(f_name)
        
        # Update load balancer status to PENDING_CREATE
        create_lb_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-pending-create',
            provisioning_status=constants.PENDING_CREATE
        ))
        
        # Create load balancer in LoxiLB
        create_lb_flow.add(loxilb_tasks.CreateLoadBalancerInLoxiLB(
            name='create-loadbalancer-in-loxilb',
            requires=[constants.LOADBALANCER, constants.VIP_SUBNET_ID] 
        ))
        
        # Create VIP in LoxiLB
        create_lb_flow.add(loxilb_tasks.CreateVIPInLoxiLB(
            name='create-vip-in-loxilb',
            requires=constants.LOADBALANCER
        ))
        
        # Create pools if specified
        if pools:
            for pool in pools:
                create_lb_flow.add(self._pool_flows.get_create_pool_flow(
                    topology=topology
                ))
        
        # Create listeners if specified
        if listeners:
            for listener in listeners:
                create_lb_flow.add(self._listener_flows.get_create_listener_flow(
                    topology=topology
                ))
        
        # Update load balancer status to ACTIVE
        create_lb_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            create_lb_flow.add(
                notification_tasks.CoreSendCreateNotification(
                    requires=constants.LOADBALANCER
                )
            )
        
        return create_lb_flow

    def get_delete_load_balancer_flow(self, cascade=False):
        """Delete a load balancer flow.
        
        :param cascade: Whether to cascade delete child resources
        :returns: The flow for deleting a load balancer
        """
        f_name = 'loxilb-delete-loadbalancer-flow'
        delete_lb_flow = linear_flow.Flow(f_name)
        
        # Update load balancer status to PENDING_DELETE
        delete_lb_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-pending-delete',
            provisioning_status=constants.PENDING_DELETE
        ))
        
        # If cascade delete, add flows to delete all child objects
        if cascade:
            # Add cascade delete flows for listeners, pools, etc.
            delete_lb_flow.add(self._get_cascade_delete_children_flow())
        
        # Delete load balancer from LoxiLB
        delete_lb_flow.add(loxilb_tasks.DeleteLoadBalancerInLoxiLB(
            name='delete-loadbalancer-in-loxilb',
            requires=constants.LOADBALANCER
        ))
        
        # Mark load balancer as deleted in DB
        delete_lb_flow.add(database_tasks.MarkLoadBalancerDeletedInDB(
            name='mark-lb-deleted',
            requires=constants.LOADBALANCER
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            delete_lb_flow.add(
                notification_tasks.CoreSendDeleteNotification(
                    requires=constants.LOADBALANCER
                )
            )
        
        delete_lb_flow.add(database_tasks.MarkLoadBalancerDeletedInDB())

        return delete_lb_flow

    def _get_cascade_delete_children_flow(self):
        """Creates a flow to delete all child objects of a load balancer.
        
        :returns: The flow for deleting all child objects
        """
        cascade_flow = linear_flow.Flow('loxilb-cascade-delete-children-flow')
        
        # Delete in reverse order of dependencies:
        # 1. First delete members (they depend on pools)
        # 2. Then delete listeners (they may reference pools)
        # 3. Finally delete pools
        
        # Delete all members
        cascade_flow.add(loxilb_tasks.DeleteAllMembersInLoxiLB(
            name='delete-all-members',
            requires=constants.LOADBALANCER
        ))
        
        # Delete all listeners
        cascade_flow.add(loxilb_tasks.DeleteAllListenersInLoxiLB(
            name='delete-all-listeners',
            requires=constants.LOADBALANCER
        ))
        
        # Delete all pools
        cascade_flow.add(loxilb_tasks.DeleteAllPoolsInLoxiLB(
            name='delete-all-pools',
            requires=constants.LOADBALANCER
        ))
        
        # Mark all child objects as deleted in DB
        cascade_flow.add(database_tasks.MarkChildObjectsDeletedInDB(
            name='mark-child-objects-deleted',
            requires=constants.LOADBALANCER
        ))
        
        return cascade_flow

    def get_update_load_balancer_flow(self):
        """Update a load balancer flow.
        
        :returns: The flow for updating a load balancer
        """
        f_name = 'loxilb-update-loadbalancer-flow'
        update_lb_flow = linear_flow.Flow(f_name)
        
        # Update load balancer status to PENDING_UPDATE
        update_lb_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-pending-update',
            provisioning_status=constants.PENDING_UPDATE
        ))
        
        # Update load balancer in LoxiLB
        update_lb_flow.add(loxilb_tasks.UpdateLoadBalancerInLoxiLB(
            name='update-loadbalancer-in-loxilb',
            requires=[constants.LOADBALANCER, constants.UPDATE_DICT]
        ))
        
        # Update load balancer status to ACTIVE
        update_lb_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active',
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            update_lb_flow.add(
                notification_tasks.CoreSendUpdateNotification(
                    requires=constants.LOADBALANCER
                )
            )
        
        return update_lb_flow
        
    def get_failover_load_balancer_flow(self):
        """Failover a load balancer flow.
        
        :returns: The flow for failing over a load balancer
        """
        f_name = 'loxilb-failover-loadbalancer-flow'
        failover_lb_flow = linear_flow.Flow(f_name)
        
        # Update load balancer status to PENDING_UPDATE
        failover_lb_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-pending-failover',
            provisioning_status=constants.PENDING_UPDATE
        ))
        
        # Failover load balancer in LoxiLB
        failover_lb_flow.add(loxilb_tasks.FailoverLoadBalancerInLoxiLB(
            name='failover-loadbalancer-in-loxilb',
            requires=constants.LOADBALANCER
        ))
        
        # Update load balancer status to ACTIVE
        failover_lb_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-after-failover',
            provisioning_status=constants.ACTIVE
        ))
        
        return failover_lb_flow