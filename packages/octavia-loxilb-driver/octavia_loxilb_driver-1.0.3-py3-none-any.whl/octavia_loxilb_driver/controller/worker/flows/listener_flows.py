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

from octavia_loxilb_driver.controller.worker.flows import l7policy_flows
from octavia_loxilb_driver.controller.worker.tasks import loxilb_tasks
from octavia_loxilb_driver.controller.worker.tasks import database_tasks

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class ListenerFlows(object):
    """Listener flows for LoxiLB driver."""
    
    def __init__(self):
        self._l7policy_flows = l7policy_flows.L7PolicyFlows()

    def get_create_listener_flow(self, topology='SINGLE'):
        """Create a listener flow.
        
        :param topology: Load balancer topology
        :returns: The flow for creating a listener
        """
        f_name = 'loxilb-create-listener-flow'
        create_listener_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        create_listener_flow.add(lifecycle_tasks.ListenerToErrorOnRevertTask(
            name='listener-to-error-on-revert',
            requires=[constants.LISTENER]
        ))

        # Update status to pending create
        create_listener_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-pending-create',
            provisioning_status=constants.PENDING_CREATE
        ))

        # Create listener in LoxiLB
        create_listener_flow.add(loxilb_tasks.CreateListenerInLoxiLB(
            name='create-listener-in-loxilb',
            requires=[constants.LOADBALANCER, constants.LISTENER]
        ))

        # Update status to active
        create_listener_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))
        
        # Update load balancer status
        create_listener_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-listener-create',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            create_listener_flow.add(
                notification_tasks.SendCreateNotification(
                    name='send-listener-create-notification',
                    requires=constants.LISTENER
                )
            )

        return create_listener_flow

    def get_delete_listener_flow(self, cascade=False):
        """Delete a listener flow.
        
        :param cascade: Whether to cascade delete child resources
        :returns: The flow for deleting a listener
        """
        f_name = 'loxilb-delete-listener-flow'
        delete_listener_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        delete_listener_flow.add(lifecycle_tasks.ListenerToErrorOnRevertTask(
            name='listener-to-error-on-revert',
            requires=[constants.LISTENER]
        ))

        # Update status to pending delete
        delete_listener_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-pending-delete',
            provisioning_status=constants.PENDING_DELETE
        ))
        
        # If cascade delete, add flows to delete all child objects
        if cascade:
            delete_listener_flow.add(self._get_cascade_delete_l7policies_flow())

        # Delete listener from LoxiLB
        delete_listener_flow.add(loxilb_tasks.DeleteListenerInLoxiLB(
            name='delete-listener-in-loxilb',
            requires=[constants.LOADBALANCER, constants.LISTENER]
        ))

        # Mark as deleted
        delete_listener_flow.add(database_tasks.MarkListenerDeletedInDB(
            name='mark-listener-deleted',
            requires=constants.LISTENER
        ))
        
        # Update load balancer status
        delete_listener_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-listener-delete',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            delete_listener_flow.add(
                notification_tasks.SendDeleteNotification(
                    name='send-listener-delete-notification',
                    requires=constants.LISTENER
                )
            )

        return delete_listener_flow
    
    def _get_cascade_delete_l7policies_flow(self):
        """Creates a flow to delete all L7 policies of a listener.
        
        :returns: The flow for deleting all L7 policies
        """
        cascade_flow = linear_flow.Flow('loxilb-cascade-delete-l7policies-flow')
        
        # Delete all L7 policies
        cascade_flow.add(loxilb_tasks.DeleteAllL7PoliciesInLoxiLB(
            name='delete-all-l7policies',
            requires=constants.LISTENER
        ))
        
        # Mark all L7 policies as deleted in DB
        cascade_flow.add(database_tasks.MarkL7PoliciesDeletedInDB(
            name='mark-l7policies-deleted',
            requires=constants.LISTENER
        ))
        
        return cascade_flow

    def get_update_listener_flow(self):
        """Update a listener flow.
        
        :returns: The flow for updating a listener
        """
        f_name = 'loxilb-update-listener-flow'
        update_listener_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        update_listener_flow.add(lifecycle_tasks.ListenerToErrorOnRevertTask(
            name='listener-to-error-on-revert',
            requires=[constants.LISTENER]
        ))

        # Update status to pending update
        update_listener_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-pending-update',
            provisioning_status=constants.PENDING_UPDATE
        ))

        # Update listener in LoxiLB
        update_listener_flow.add(loxilb_tasks.UpdateListenerInLoxiLB(
            name='update-listener-in-loxilb',
            requires=[constants.LISTENER, constants.UPDATE_DICT, constants.LOADBALANCER]
        ))

        # Update status to active
        update_listener_flow.add(database_tasks.UpdateListenerInDB(
            name='update-listener-active',
            provisioning_status=constants.ACTIVE
        ))
        
        # Update load balancer status
        update_listener_flow.add(database_tasks.UpdateLoadBalancerInDB(
            name='update-lb-active-for-listener-update',
            requires=constants.LOADBALANCER,
            provisioning_status=constants.ACTIVE
        ))
        
        # Add notification if enabled
        if CONF.controller_worker.event_notifications:
            update_listener_flow.add(
                notification_tasks.SendUpdateNotification(
                    name='send-listener-update-notification',
                    requires=constants.LISTENER
                )
            )

        return update_listener_flow
    
    def get_fully_populated_create_listener_flow(self, topology='SINGLE', listener=None):
        """Create a fully populated listener flow.
        
        :param topology: Load balancer topology
        :param listener: Listener object to create
        :returns: The flow for creating a fully populated listener
        """
        f_name = 'loxilb-fully-populated-create-listener-flow'
        if listener:
            f_name += '-' + listener.id
            
        create_listener_flow = linear_flow.Flow(f_name)
        
        # Add error handling task
        create_listener_flow.add(lifecycle_tasks.ListenerToErrorOnRevertTask(
            name=f_name + '-to-error-on-revert',
            requires=[constants.LISTENER],
            inject={constants.LISTENER: listener} if listener else {}
        ))

        # Update status to pending create
        create_listener_flow.add(database_tasks.UpdateListenerInDB(
            name=f_name + '-pending-create',
            provisioning_status=constants.PENDING_CREATE
        ))

        # Create listener in LoxiLB
        create_listener_flow.add(loxilb_tasks.CreateListenerInLoxiLB(
            name=f_name + '-create-in-loxilb',
            requires=[constants.LOADBALANCER, constants.LISTENER]
        ))
        
        # If listener has L7 policies, create them
        if listener and listener.l7policies:
            for l7policy in listener.l7policies:
                create_listener_flow.add(
                    self._l7policy_flows.get_create_l7policy_flow(topology=topology)
                )

        # Update status to active
        create_listener_flow.add(database_tasks.UpdateListenerInDB(
            name=f_name + '-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))
        
        return create_listener_flow