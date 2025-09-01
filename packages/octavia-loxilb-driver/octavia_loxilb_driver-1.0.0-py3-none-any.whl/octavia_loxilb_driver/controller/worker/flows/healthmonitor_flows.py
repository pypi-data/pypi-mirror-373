# Copyright 2025 LoxiLB
# Licensed under the Apache License, Version 2.0

from oslo_config import cfg
from oslo_log import log as logging
from taskflow.patterns import linear_flow

from octavia.common import constants
from octavia_loxilb_driver.controller.worker.tasks import loxilb_tasks
from octavia_loxilb_driver.controller.worker.tasks import database_tasks

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class HealthMonitorFlows(object):
    """Health monitor flows for LoxiLB driver."""

    def get_create_health_monitor_flow(self, topology='SINGLE'):
        """Create a health monitor flow.
        
        :param topology: Load balancer topology
        :returns: The flow for creating a health monitor
        """
        LOG.info("Starting create health monitor flow for topology: %s", topology)
        create_hm_flow = linear_flow.Flow('loxilb-create-healthmonitor-flow')

        # Update status to pending
        create_hm_flow.add(database_tasks.UpdateHealthMonitorInDB(
            name='update-hm-pending-create',
            provisioning_status=constants.PENDING_CREATE,
            operating_status=constants.OFFLINE
        ))

        # Create health monitor in LoxiLB
        create_hm_flow.add(loxilb_tasks.CreateHealthMonitorInLoxiLB())

        # Update status to active
        create_hm_flow.add(database_tasks.UpdateHealthMonitorInDB(
            name='update-hm-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))

        LOG.info("Completed create health monitor flow setup.")
        return create_hm_flow

    def get_delete_health_monitor_flow(self, topology='SINGLE'):
        """Delete a health monitor flow.
        
        :param topology: Load balancer topology
        :returns: The flow for deleting a health monitor
        """
        LOG.info("Starting delete health monitor flow for topology: %s", topology)
        delete_hm_flow = linear_flow.Flow('loxilb-delete-healthmonitor-flow')

        # Update status to pending delete
        delete_hm_flow.add(database_tasks.UpdateHealthMonitorInDB(
            name='update-hm-pending-delete',
            provisioning_status=constants.PENDING_DELETE,
            operating_status=constants.OFFLINE
        ))

        # Delete health monitor from LoxiLB
        delete_hm_flow.add(loxilb_tasks.DeleteHealthMonitorInLoxiLB())

        # Mark as deleted
        delete_hm_flow.add(database_tasks.MarkHealthMonitorDeletedInDB())

        LOG.info("Completed delete health monitor flow setup.")
        return delete_hm_flow

    def get_update_health_monitor_flow(self, topology='SINGLE'):
        """Update a health monitor flow.
        
        :param topology: Load balancer topology
        :returns: The flow for updating a health monitor
        """
        LOG.info("Starting update health monitor flow for topology: %s", topology)
        update_hm_flow = linear_flow.Flow('loxilb-update-healthmonitor-flow')

        # Update status to pending update
        update_hm_flow.add(database_tasks.UpdateHealthMonitorInDB(
            name='update-hm-pending-update',
            provisioning_status=constants.PENDING_UPDATE,
            operating_status=constants.OFFLINE
        ))

        # Update health monitor in LoxiLB
        update_hm_flow.add(loxilb_tasks.UpdateHealthMonitorInLoxiLB())

        # Update status to active
        update_hm_flow.add(database_tasks.UpdateHealthMonitorInDB(
            name='update-hm-active',
            provisioning_status=constants.ACTIVE,
            operating_status=constants.ONLINE
        ))

        LOG.info("Completed update health monitor flow setup.")
        return update_hm_flow