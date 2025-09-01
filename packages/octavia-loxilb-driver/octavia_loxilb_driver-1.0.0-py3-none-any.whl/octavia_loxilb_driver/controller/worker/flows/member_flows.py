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

from octavia_loxilb_driver.controller.worker.tasks import loxilb_tasks
from octavia_loxilb_driver.controller.worker.tasks import database_tasks

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class MemberFlows(object):
    """Member flows for LoxiLB driver."""

    def get_create_member_flow(self, topology='SINGLE'):
        """Create a member flow.
        
        :param topology: Load balancer topology
        :returns: The flow for creating a member
        """
        f_name = 'loxilb-create-member-flow'
        create_member_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        create_member_flow.add(lifecycle_tasks.MemberToErrorOnRevertTask(
            name='member-to-error-on-revert',
            requires=[constants.MEMBER]
        ))

        # Update status to pending create
        create_member_flow.add(database_tasks.UpdateMemberInDB(
            name='update-member-pending-create',
            provisioning_status=constants.PENDING_CREATE
        ))

        # Create member in LoxiLB
        create_member_flow.add(loxilb_tasks.CreateMemberInLoxiLB(
            name='create-member-in-loxilb',
            requires=[constants.LOADBALANCER, constants.POOL, constants.MEMBER]
        ))

        # Update status to active
        create_member_flow.add(database_tasks.UpdateMemberInDB(
            name='update-member-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))
        
        # Update pool status
        create_member_flow.add(database_tasks.UpdatePoolInDB(
            name='update-pool-active-for-member-create',
            requires=constants.POOL,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        create_member_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-member-create',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            create_member_flow.add(
                notification_tasks.SendCreateNotification(
                    name='send-member-create-notification',
                    requires=constants.MEMBER
                )
            )

        return create_member_flow

    def get_delete_member_flow(self, topology='SINGLE'):
        """Delete a member flow.
        
        :returns: The flow for deleting a member
        """
        f_name = 'loxilb-delete-member-flow'
        delete_member_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        delete_member_flow.add(lifecycle_tasks.MemberToErrorOnRevertTask(
            name='member-to-error-on-revert',
            requires=[constants.MEMBER]
        ))

        # Update status to pending delete
        delete_member_flow.add(database_tasks.UpdateMemberInDB(
            name='update-member-pending-delete',
            provisioning_status=constants.PENDING_DELETE
        ))

        # Delete member from LoxiLB
        delete_member_flow.add(loxilb_tasks.DeleteMemberInLoxiLB(
            name='delete-member-in-loxilb',
            requires=[constants.LOADBALANCER, constants.POOL, constants.MEMBER]
        ))

        # Mark as deleted
        delete_member_flow.add(database_tasks.MarkMemberDeletedInDB(
            name='mark-member-deleted',
            requires=constants.MEMBER
        ))
        
        # Update pool status
        delete_member_flow.add(database_tasks.UpdatePoolInDB(
            name='update-pool-active-for-member-delete',
            requires=constants.POOL,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        delete_member_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-member-delete',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            delete_member_flow.add(
                notification_tasks.SendDeleteNotification(
                    name='send-member-delete-notification',
                    requires=constants.MEMBER
                )
            )

        return delete_member_flow

    def get_update_member_flow(self):
        """Update a member flow.
        
        :returns: The flow for updating a member
        """
        f_name = 'loxilb-update-member-flow'
        update_member_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        update_member_flow.add(lifecycle_tasks.MemberToErrorOnRevertTask(
            name='member-to-error-on-revert',
            requires=[constants.MEMBER]
        ))

        # Update status to pending update
        update_member_flow.add(database_tasks.UpdateMemberInDB(
            name='update-member-pending-update',
            provisioning_status=constants.PENDING_UPDATE
        ))

        # Update member in LoxiLB
        update_member_flow.add(loxilb_tasks.UpdateMemberInLoxiLB(
            name='update-member-in-loxilb',
            requires=[constants.LOADBALANCER, constants.POOL, constants.MEMBER, constants.UPDATE_DICT]
        ))

        # Update status to active
        update_member_flow.add(database_tasks.UpdateMemberInDB(
            name='update-member-active',
            provisioning_status=constants.ACTIVE
        ))
        
        # Update pool status
        update_member_flow.add(database_tasks.UpdatePoolInDB(
            name='update-pool-active-for-member-update',
            requires=constants.POOL,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        update_member_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-member-update',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            update_member_flow.add(
                notification_tasks.SendUpdateNotification(
                    name='send-member-update-notification',
                    requires=constants.MEMBER
                )
            )

        return update_member_flow
    
    def get_batch_update_members_flow(self, pool_id, members=None):
        """Update multiple members flow.
        
        :param pool_id: ID of the pool the members belong to
        :param members: List of member objects to update
        :returns: The flow for batch updating members
        """
        f_name = 'loxilb-batch-update-members-flow'
        batch_update_flow = linear_flow.Flow(f_name)
        
        # Update pool status to pending update
        batch_update_flow.add(database_tasks.UpdatePoolInDB(
            name='update-pool-pending-update-for-batch',
            pool_id=pool_id,
            provisioning_status=constants.PENDING_UPDATE
        ))
        
        # Create unordered flow for member updates
        member_update_flow = unordered_flow.Flow('loxilb-member-updates-flow')
        
        # Add member update tasks
        if members:
            for member in members:
                member_update_flow.add(loxilb_tasks.UpdateMemberInLoxiLB(
                    name=f'update-member-{member.id}-in-loxilb',
                    requires=[constants.LOADBALANCER, constants.POOL, constants.MEMBER, constants.UPDATE_DICT],
                    inject={constants.MEMBER: member}
                ))
        
        # Add the unordered flow to the main flow
        batch_update_flow.add(member_update_flow)
        
        # Update pool status to active
        batch_update_flow.add(database_tasks.UpdatePoolInDB(
            name='update-pool-active-after-batch',
            pool_id=pool_id,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        batch_update_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-batch-update',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        return batch_update_flow