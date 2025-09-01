# Copyright 2025 LoxiLB
# Licensed under the Apache License, Version 2.0

from oslo_config import cfg
from oslo_log import log as logging
from taskflow.patterns import linear_flow
from taskflow.patterns import unordered_flow

from octavia.common import constants
from octavia.controller.worker.v1.tasks import lifecycle_tasks
# Use our custom notification tasks instead of the default Octavia ones
from octavia_loxilb_driver.controller.worker.tasks import notification_tasks

from octavia_loxilb_driver.controller.worker.flows import healthmonitor_flows
from octavia_loxilb_driver.controller.worker.flows import member_flows
from octavia_loxilb_driver.controller.worker.tasks import loxilb_tasks
from octavia_loxilb_driver.controller.worker.tasks import database_tasks

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class PoolFlows(object):
    """Pool flows for LoxiLB driver."""
    
    def __init__(self):
        self._health_monitor_flows = healthmonitor_flows.HealthMonitorFlows()
        self._member_flows = member_flows.MemberFlows()

    def get_create_pool_flow(self, topology='SINGLE'):
        """Create a pool flow.
        
        :param topology: Load balancer topology
        :returns: The flow for creating a pool
        """
        f_name = 'loxilb-create-pool-flow'
        create_pool_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        create_pool_flow.add(lifecycle_tasks.PoolToErrorOnRevertTask(
            name='pool-to-error-on-revert',
            requires=[constants.POOL]
        ))

        # Update status to pending create
        create_pool_flow.add(database_tasks.UpdatePoolInDB(
            name='update-pool-pending-create',
            provisioning_status=constants.PENDING_CREATE
        ))

        # Create pool in LoxiLB (pass listener if available)
        create_pool_flow.add(loxilb_tasks.CreatePoolInLoxiLB(
            name='create-pool-in-loxilb',
            requires=[constants.LOADBALANCER, constants.POOL, constants.LISTENER]
        ))

        # Update status to active
        create_pool_flow.add(database_tasks.UpdatePoolInDB(
            name='update-pool-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))
        
        # Update load balancer status
        create_pool_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-pool-create',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            create_pool_flow.add(
                notification_tasks.SendCreateNotification(
                    name='send-pool-create-notification',
                    requires=constants.POOL
                )
            )

        return create_pool_flow

    def get_delete_pool_flow(self, cascade=False):
        """Delete a pool flow.
        
        :param cascade: Whether to cascade delete child resources
        :returns: The flow for deleting a pool
        """
        f_name = 'loxilb-delete-pool-flow'
        delete_pool_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        delete_pool_flow.add(lifecycle_tasks.PoolToErrorOnRevertTask(
            name='pool-to-error-on-revert',
            requires=[constants.POOL]
        ))

        # Update status to pending delete
        delete_pool_flow.add(database_tasks.UpdatePoolInDB(
            name='update-pool-pending-delete',
            provisioning_status=constants.PENDING_DELETE
        ))
        
        # If cascade delete, add flows to delete all child objects
        if cascade:
            delete_pool_flow.add(self._get_cascade_delete_children_flow())

        # Delete pool from LoxiLB (pass listener if available)
        delete_pool_flow.add(loxilb_tasks.DeletePoolInLoxiLB(
            name='delete-pool-in-loxilb',
            requires=[constants.LOADBALANCER, constants.POOL, constants.LISTENER]
        ))

        # Mark as deleted
        delete_pool_flow.add(database_tasks.MarkPoolDeletedInDB(
            name='mark-pool-deleted',
            requires=constants.POOL
        ))
        
        # Update load balancer status
        delete_pool_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-pool-delete',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            delete_pool_flow.add(
                notification_tasks.SendDeleteNotification(
                    name='send-pool-delete-notification',
                    requires=constants.POOL
                )
            )

        return delete_pool_flow
    
    def _get_cascade_delete_children_flow(self):
        """Creates a flow to delete all child objects of a pool.
        
        :returns: The flow for deleting all child objects
        """
        cascade_flow = linear_flow.Flow('loxilb-cascade-delete-pool-children-flow')
        
        # Delete all members
        cascade_flow.add(loxilb_tasks.DeleteAllMembersInLoxiLB(
            name='delete-all-members',
            requires=constants.POOL
        ))
        
        # Delete health monitor if present
        cascade_flow.add(loxilb_tasks.DeleteHealthMonitorInLoxiLB(
            name='delete-health-monitor',
            requires=constants.POOL
        ))
        
        # Mark all child objects as deleted in DB
        cascade_flow.add(database_tasks.MarkPoolChildrenDeletedInDB(
            name='mark-pool-children-deleted',
            requires=constants.POOL
        ))
        
        return cascade_flow

    def get_update_pool_flow(self, topology='SINGLE'):
        """Update a pool flow.
        
        :returns: The flow for updating a pool
        """
        f_name = 'loxilb-update-pool-flow'
        update_pool_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        update_pool_flow.add(lifecycle_tasks.PoolToErrorOnRevertTask(
            name='pool-to-error-on-revert',
            requires=[constants.POOL]
        ))

        # Update status to pending update
        update_pool_flow.add(database_tasks.UpdatePoolInDB(
            name='update-pool-pending-update',
            provisioning_status=constants.PENDING_UPDATE
        ))

        # Update pool in LoxiLB (pass listener if available)
        update_pool_flow.add(loxilb_tasks.UpdatePoolInLoxiLB(
            name='update-pool-in-loxilb',
            requires=[constants.LOADBALANCER, constants.POOL, constants.UPDATE_DICT, constants.LISTENER]
        ))

        # Update status to active
        update_pool_flow.add(database_tasks.UpdatePoolInDB(
            name='update-pool-active',
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        update_pool_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-pool-update',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            update_pool_flow.add(
                notification_tasks.SendUpdateNotification(
                    name='send-pool-update-notification',
                    requires=constants.POOL
                )
            )

        return update_pool_flow
    
    def get_fully_populated_create_pool_flow(self, topology='SINGLE', pool=None):
        """Create a fully populated pool flow.
        
        :param topology: Load balancer topology
        :param pool: Pool object to create
        :returns: The flow for creating a fully populated pool
        """
        f_name = 'loxilb-fully-populated-create-pool-flow'
        if pool:
            f_name += '-' + pool.id
            
        create_pool_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        create_pool_flow.add(lifecycle_tasks.PoolToErrorOnRevertTask(
            name=f_name + '-to-error-on-revert',
            requires=[constants.POOL],
            inject={constants.POOL: pool} if pool else {}
        ))

        # Update status to pending create
        create_pool_flow.add(database_tasks.UpdatePoolInDB(
            name=f_name + '-pending-create',
            provisioning_status=constants.PENDING_CREATE
        ))

        # Create pool in LoxiLB
        create_pool_flow.add(loxilb_tasks.CreatePoolInLoxiLB(
            name=f_name + '-create-in-loxilb',
            requires=[constants.LOADBALANCER, constants.POOL]
        ))
        
        # If pool has members, create them
        if pool and pool.members:
            for member in pool.members:
                create_pool_flow.add(
                    self._member_flows.get_create_member_flow(topology=topology)
                )
        
        # If pool has health monitor, create it
        if pool and pool.health_monitor:
            create_pool_flow.add(
                self._health_monitor_flows.get_create_health_monitor_flow(topology=topology)
            )

        # Update status to active
        create_pool_flow.add(database_tasks.UpdatePoolInDB(
            name=f_name + '-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))
        
        return create_pool_flow