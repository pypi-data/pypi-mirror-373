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

from octavia_loxilb_driver.controller.worker.flows import l7rule_flows
from octavia_loxilb_driver.controller.worker.tasks import loxilb_tasks
from octavia_loxilb_driver.controller.worker.tasks import database_tasks

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class L7PolicyFlows(object):
    """L7 Policy flows for LoxiLB driver."""
    
    def __init__(self):
        self._l7rule_flows = l7rule_flows.L7RuleFlows()

    def get_create_l7policy_flow(self, topology='SINGLE'):
        """Create an L7 policy flow.
        
        :param topology: Load balancer topology
        :returns: The flow for creating an L7 policy
        """
        f_name = 'loxilb-create-l7policy-flow'
        create_l7policy_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        create_l7policy_flow.add(lifecycle_tasks.L7PolicyToErrorOnRevertTask(
            name='l7policy-to-error-on-revert',
            requires=[constants.L7POLICY]
        ))

        # Update status to pending create
        create_l7policy_flow.add(database_tasks.UpdateL7PolicyInDB(
            name='update-l7policy-pending-create',
            provisioning_status=constants.PENDING_CREATE
        ))

        # Create L7 policy in LoxiLB
        create_l7policy_flow.add(loxilb_tasks.CreateL7PolicyInLoxiLB(
            name='create-l7policy-in-loxilb',
            requires=[constants.LOADBALANCER, constants.LISTENER, constants.L7POLICY]
        ))

        # Update status to active
        create_l7policy_flow.add(database_tasks.UpdateL7PolicyInDB(
            name='update-l7policy-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))
        
        # Update listener status
        create_l7policy_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-active-for-l7policy-create',
            requires=constants.LISTENER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        create_l7policy_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-l7policy-create',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            create_l7policy_flow.add(
                notification_tasks.SendCreateNotification(
                    name='send-l7policy-create-notification',
                    requires=constants.L7POLICY
                )
            )

        return create_l7policy_flow

    def get_delete_l7policy_flow(self, cascade=False):
        """Delete an L7 policy flow.
        
        :param cascade: Whether to cascade delete child resources
        :returns: The flow for deleting an L7 policy
        """
        f_name = 'loxilb-delete-l7policy-flow'
        delete_l7policy_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        delete_l7policy_flow.add(lifecycle_tasks.L7PolicyToErrorOnRevertTask(
            name='l7policy-to-error-on-revert',
            requires=[constants.L7POLICY]
        ))

        # Update status to pending delete
        delete_l7policy_flow.add(database_tasks.UpdateL7PolicyInDB(
            name='update-l7policy-pending-delete',
            provisioning_status=constants.PENDING_DELETE
        ))
        
        # If cascade delete, add flows to delete all child objects
        if cascade:
            delete_l7policy_flow.add(self._get_cascade_delete_l7rules_flow())

        # Delete L7 policy from LoxiLB
        delete_l7policy_flow.add(loxilb_tasks.DeleteL7PolicyInLoxiLB(
            name='delete-l7policy-in-loxilb',
            requires=[constants.LOADBALANCER, constants.LISTENER, constants.L7POLICY]
        ))

        # Mark as deleted
        delete_l7policy_flow.add(database_tasks.MarkL7PolicyDeletedInDB(
            name='mark-l7policy-deleted',
            requires=constants.L7POLICY
        ))
        
        # Update listener status
        delete_l7policy_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-active-for-l7policy-delete',
            requires=constants.LISTENER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        delete_l7policy_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-l7policy-delete',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            delete_l7policy_flow.add(
                notification_tasks.SendDeleteNotification(
                    name='send-l7policy-delete-notification',
                    requires=constants.L7POLICY
                )
            )

        return delete_l7policy_flow
    
    def _get_cascade_delete_l7rules_flow(self):
        """Creates a flow to delete all L7 rules of an L7 policy.
        
        :returns: The flow for deleting all L7 rules
        """
        cascade_flow = linear_flow.Flow('loxilb-cascade-delete-l7rules-flow')
        
        # Delete all L7 rules
        cascade_flow.add(loxilb_tasks.DeleteAllL7RulesInLoxiLB(
            name='delete-all-l7rules',
            requires=constants.L7POLICY
        ))
        
        # Mark all L7 rules as deleted in DB
        cascade_flow.add(database_tasks.MarkL7RulesDeletedInDB(
            name='mark-l7rules-deleted',
            requires=constants.L7POLICY
        ))
        
        return cascade_flow

    def get_update_l7policy_flow(self):
        """Update an L7 policy flow.
        
        :returns: The flow for updating an L7 policy
        """
        f_name = 'loxilb-update-l7policy-flow'
        update_l7policy_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        update_l7policy_flow.add(lifecycle_tasks.L7PolicyToErrorOnRevertTask(
            name='l7policy-to-error-on-revert',
            requires=[constants.L7POLICY]
        ))

        # Update status to pending update
        update_l7policy_flow.add(database_tasks.UpdateL7PolicyInDB(
            name='update-l7policy-pending-update',
            provisioning_status=constants.PENDING_UPDATE
        ))

        # Update L7 policy in LoxiLB
        update_l7policy_flow.add(loxilb_tasks.UpdateL7PolicyInLoxiLB(
            name='update-l7policy-in-loxilb',
            requires=[constants.LOADBALANCER, constants.LISTENER, constants.L7POLICY, constants.UPDATE_DICT]
        ))

        # Update status to active
        update_l7policy_flow.add(database_tasks.UpdateL7PolicyInDB(
            name='update-l7policy-active',
            provisioning_status=constants.ACTIVE
        ))
        
        # Update listener status
        update_l7policy_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-active-for-l7policy-update',
            requires=constants.LISTENER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        update_l7policy_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-l7policy-update',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            update_l7policy_flow.add(
                notification_tasks.SendUpdateNotification(
                    name='send-l7policy-update-notification',
                    requires=constants.L7POLICY
                )
            )

        return update_l7policy_flow
    
    def get_fully_populated_create_l7policy_flow(self, topology='SINGLE', l7policy=None):
        """Create a fully populated L7 policy flow.
        
        :param topology: Load balancer topology
        :param l7policy: L7 policy object to create
        :returns: The flow for creating a fully populated L7 policy
        """
        f_name = 'loxilb-fully-populated-create-l7policy-flow'
        if l7policy:
            f_name += '-' + l7policy.id
            
        create_l7policy_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        create_l7policy_flow.add(lifecycle_tasks.L7PolicyToErrorOnRevertTask(
            name=f_name + '-to-error-on-revert',
            requires=[constants.L7POLICY],
            inject={constants.L7POLICY: l7policy} if l7policy else {}
        ))

        # Update status to pending create
        create_l7policy_flow.add(database_tasks.UpdateL7PolicyInDB(
            name=f_name + '-pending-create',
            provisioning_status=constants.PENDING_CREATE
        ))

        # Create L7 policy in LoxiLB
        create_l7policy_flow.add(loxilb_tasks.CreateL7PolicyInLoxiLB(
            name=f_name + '-create-in-loxilb',
            requires=[constants.LOADBALANCER, constants.LISTENER, constants.L7POLICY]
        ))
        
        # If L7 policy has rules, create them
        if l7policy and l7policy.rules:
            for rule in l7policy.rules:
                create_l7policy_flow.add(
                    self._l7rule_flows.get_create_l7rule_flow(topology=topology)
                )

        # Update status to active
        create_l7policy_flow.add(database_tasks.UpdateL7PolicyInDB(
            name=f_name + '-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))
        
        return create_l7policy_flow
