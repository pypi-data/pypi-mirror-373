# Copyright 2023 NetLOX Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg
from oslo_log import log as logging
from taskflow import task

from octavia.common import constants
from octavia.common import rpc
from octavia.controller.worker.v2.tasks import notification_tasks as octavia_notification_tasks

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class LoadBalancerToDict(task.Task):
    """Task to convert LoadBalancer object to a dictionary for notification tasks."""

    def execute(self, loadbalancer, **kwargs):
        """Convert LoadBalancer object to dictionary.

        :param loadbalancer: The load balancer object.
        :returns: Dictionary representation of the load balancer
        """
        LOG.debug("Converting LoadBalancer object to dictionary for %s", loadbalancer.id)
        
        # Create a dictionary representation of the loadbalancer object
        lb_dict = {
            constants.LOADBALANCER_ID: loadbalancer.id,
            constants.OPERATING_STATUS: loadbalancer.operating_status,
            constants.PROVISIONING_STATUS: loadbalancer.provisioning_status,
            constants.PROJECT_ID: getattr(loadbalancer, 'project_id', None)
        }
        
        return lb_dict


class SendCreateNotification(task.Task):
    """Task to send a create notification."""

    def execute(self, loadbalancer, **kwargs):
        """Send a create notification.

        :param loadbalancer: The load balancer object.
        :returns: None
        """
        LOG.debug("Sending create notification for %s", loadbalancer.id)
        
        # Access the project_id as an attribute, not as a dictionary key
        project_id = getattr(loadbalancer, 'project_id', None)
        
        rpc.get_notifier().info(
            {},
            'octavia.loadbalancer.create.end',
            {'id': loadbalancer.id,
             'operating_status': loadbalancer.operating_status,
             'provisioning_status': loadbalancer.provisioning_status,
             'project_id': project_id})


class SendDeleteNotification(task.Task):
    """Task to send a delete notification."""

    def execute(self, loadbalancer, **kwargs):
        """Send a delete notification.

        :param loadbalancer: The load balancer object.
        :returns: None
        """
        LOG.debug("Sending delete notification for %s", loadbalancer.id)
        
        # Access the project_id as an attribute, not as a dictionary key
        project_id = getattr(loadbalancer, 'project_id', None)
        
        rpc.get_notifier().info(
            {},
            'octavia.loadbalancer.delete.end',
            {'id': loadbalancer.id,
             'operating_status': loadbalancer.operating_status,
             'provisioning_status': loadbalancer.provisioning_status,
             'project_id': project_id})


class SendUpdateNotification(task.Task):
    """Task to send an update notification."""

    def execute(self, loadbalancer, **kwargs):
        """Send an update notification.

        :param loadbalancer: The load balancer object.
        :returns: None
        """
        LOG.debug("Sending update notification for %s", loadbalancer.id)
        
        # Access the project_id as an attribute, not as a dictionary key
        project_id = getattr(loadbalancer, 'project_id', None)
        
        rpc.get_notifier().info(
            {},
            'octavia.loadbalancer.update.end',
            {'id': loadbalancer.id,
             'operating_status': loadbalancer.operating_status,
             'provisioning_status': loadbalancer.provisioning_status,
             'project_id': project_id})


# Wrapper tasks for core Octavia notification tasks
class CoreSendCreateNotification(task.Task):
    """Wrapper task for core Octavia create notification task."""

    def execute(self, loadbalancer, **kwargs):
        """Convert LoadBalancer object to dict and call core notification task.

        :param loadbalancer: The load balancer object.
        :returns: None
        """
        LOG.debug("Wrapping core create notification for %s", loadbalancer.id)
        
        # Create a dictionary representation of the loadbalancer object
        lb_dict = {
            constants.LOADBALANCER_ID: loadbalancer.id,
            constants.OPERATING_STATUS: loadbalancer.operating_status,
            constants.PROVISIONING_STATUS: loadbalancer.provisioning_status,
            constants.PROJECT_ID: getattr(loadbalancer, 'project_id', None)
        }
        
        # Use the core notification task with our dictionary
        task = octavia_notification_tasks.SendCreateNotification()
        task.execute(lb_dict)


class CoreSendDeleteNotification(task.Task):
    """Wrapper task for core Octavia delete notification task."""

    def execute(self, loadbalancer, **kwargs):
        """Convert LoadBalancer object to dict and call core notification task.

        :param loadbalancer: The load balancer object.
        :returns: None
        """
        LOG.debug("Wrapping core delete notification for %s", loadbalancer.id)
        
        # Create a dictionary representation of the loadbalancer object
        lb_dict = {
            constants.LOADBALANCER_ID: loadbalancer.id,
            constants.OPERATING_STATUS: loadbalancer.operating_status,
            constants.PROVISIONING_STATUS: loadbalancer.provisioning_status,
            constants.PROJECT_ID: getattr(loadbalancer, 'project_id', None)
        }
        
        # Use the core notification task with our dictionary
        task = octavia_notification_tasks.SendDeleteNotification()
        task.execute(lb_dict)


class CoreSendUpdateNotification(task.Task):
    """Wrapper task for core Octavia update notification task."""

    def execute(self, loadbalancer, **kwargs):
        """Convert LoadBalancer object to dict and call core notification task.

        :param loadbalancer: The load balancer object.
        :returns: None
        """
        LOG.debug("Wrapping core update notification for %s", loadbalancer.id)
        
        # Create a dictionary representation of the loadbalancer object
        lb_dict = {
            constants.LOADBALANCER_ID: loadbalancer.id,
            constants.OPERATING_STATUS: loadbalancer.operating_status,
            constants.PROVISIONING_STATUS: loadbalancer.provisioning_status,
            constants.PROJECT_ID: getattr(loadbalancer, 'project_id', None)
        }
        
        # Use the core notification task with our dictionary
        task = octavia_notification_tasks.SendUpdateNotification()
        task.execute(lb_dict)
