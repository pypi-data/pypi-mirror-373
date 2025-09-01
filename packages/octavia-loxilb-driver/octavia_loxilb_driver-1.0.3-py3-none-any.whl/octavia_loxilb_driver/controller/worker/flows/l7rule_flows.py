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


class L7RuleFlows(object):
    """L7 Rule flows for LoxiLB driver."""

    def get_create_l7rule_flow(self, topology='SINGLE'):
        """Create an L7 rule flow.
        
        :param topology: Load balancer topology
        :returns: The flow for creating an L7 rule
        """
        f_name = 'loxilb-create-l7rule-flow'
        create_l7rule_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        create_l7rule_flow.add(lifecycle_tasks.L7RuleToErrorOnRevertTask(
            name='l7rule-to-error-on-revert',
            requires=[constants.L7RULE]
        ))

        # Update status to pending create
        create_l7rule_flow.add(database_tasks.UpdateL7RuleInDB(
            name='update-l7rule-pending-create',
            provisioning_status=constants.PENDING_CREATE
        ))

        # Create L7 rule in LoxiLB
        create_l7rule_flow.add(loxilb_tasks.CreateL7RuleInLoxiLB(
            name='create-l7rule-in-loxilb',
            requires=[constants.LOADBALANCER, constants.LISTENER, constants.L7POLICY, constants.L7RULE]
        ))

        # Update status to active
        create_l7rule_flow.add(database_tasks.UpdateL7RuleInDB(
            name='update-l7rule-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))
        
        # Update L7 policy status
        create_l7rule_flow.add(database_tasks.UpdateL7PolicyInDB(
            name='update-l7policy-active-for-l7rule-create',
            requires=constants.L7POLICY,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update listener status
        create_l7rule_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-active-for-l7rule-create',
            requires=constants.LISTENER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        create_l7rule_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-l7rule-create',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            create_l7rule_flow.add(
                notification_tasks.SendCreateNotification(
                    name='send-l7rule-create-notification',
                    requires=constants.L7RULE
                )
            )

        return create_l7rule_flow

    def get_delete_l7rule_flow(self):
        """Delete an L7 rule flow.
        
        :returns: The flow for deleting an L7 rule
        """
        f_name = 'loxilb-delete-l7rule-flow'
        delete_l7rule_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        delete_l7rule_flow.add(lifecycle_tasks.L7RuleToErrorOnRevertTask(
            name='l7rule-to-error-on-revert',
            requires=[constants.L7RULE]
        ))

        # Update status to pending delete
        delete_l7rule_flow.add(database_tasks.UpdateL7RuleInDB(
            name='update-l7rule-pending-delete',
            provisioning_status=constants.PENDING_DELETE
        ))

        # Delete L7 rule from LoxiLB
        delete_l7rule_flow.add(loxilb_tasks.DeleteL7RuleInLoxiLB(
            name='delete-l7rule-in-loxilb',
            requires=[constants.LOADBALANCER, constants.LISTENER, constants.L7POLICY, constants.L7RULE]
        ))

        # Mark as deleted
        delete_l7rule_flow.add(database_tasks.MarkL7RuleDeletedInDB(
            name='mark-l7rule-deleted',
            requires=constants.L7RULE
        ))
        
        # Update L7 policy status
        delete_l7rule_flow.add(database_tasks.UpdateL7PolicyInDB(
            name='update-l7policy-active-for-l7rule-delete',
            requires=constants.L7POLICY,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update listener status
        delete_l7rule_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-active-for-l7rule-delete',
            requires=constants.LISTENER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        delete_l7rule_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-l7rule-delete',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            delete_l7rule_flow.add(
                notification_tasks.SendDeleteNotification(
                    name='send-l7rule-delete-notification',
                    requires=constants.L7RULE
                )
            )

        return delete_l7rule_flow

    def get_update_l7rule_flow(self):
        """Update an L7 rule flow.
        
        :returns: The flow for updating an L7 rule
        """
        f_name = 'loxilb-update-l7rule-flow'
        update_l7rule_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        update_l7rule_flow.add(lifecycle_tasks.L7RuleToErrorOnRevertTask(
            name='l7rule-to-error-on-revert',
            requires=[constants.L7RULE]
        ))

        # Update status to pending update
        update_l7rule_flow.add(database_tasks.UpdateL7RuleInDB(
            name='update-l7rule-pending-update',
            provisioning_status=constants.PENDING_UPDATE
        ))

        # Update L7 rule in LoxiLB
        update_l7rule_flow.add(loxilb_tasks.UpdateL7RuleInLoxiLB(
            name='update-l7rule-in-loxilb',
            requires=[constants.LOADBALANCER, constants.LISTENER, constants.L7POLICY, constants.L7RULE, constants.UPDATE_DICT]
        ))

        # Update status to active
        update_l7rule_flow.add(database_tasks.UpdateL7RuleInDB(
            name='update-l7rule-active',
            provisioning_status=constants.ACTIVE
        ))
        
        # Update L7 policy status
        update_l7rule_flow.add(database_tasks.UpdateL7PolicyInDB(
            name='update-l7policy-active-for-l7rule-update',
            requires=constants.L7POLICY,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update listener status
        update_l7rule_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-active-for-l7rule-update',
            requires=constants.LISTENER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        update_l7rule_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-l7rule-update',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            update_l7rule_flow.add(
                notification_tasks.SendUpdateNotification(
                    name='send-l7rule-update-notification',
                    requires=constants.L7RULE
                )
            )

        return update_l7rule_flow
