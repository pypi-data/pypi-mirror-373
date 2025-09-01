# Copyright 2025 LoxiLB
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import cotyledon
from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_messaging.rpc import dispatcher

from octavia.common import constants as octavia_constants
from octavia.common import rpc
from octavia_loxilb_driver.common import config as loxilb_config
from octavia_loxilb_driver.controller.queue import endpoints

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class ConsumerService(cotyledon.Service):
    """Consumer service for LoxiLB controller worker.

    This service is responsible for consuming RPC messages sent to the
    LoxiLB controller worker and forwarding them to the appropriate
    endpoint methods.
    """

    def __init__(self, worker_id, conf):
        super().__init__(worker_id)
        self.conf = conf
        # Use the topic from the loxilb config section
        self.topic = conf.loxilb.rpc_topic
        self.server = conf.host
        self.endpoints = []
        self.access_policy = dispatcher.DefaultRPCAccessPolicy
        self.message_listener = None
        LOG.info("LoxiLB consumer service initialized with topic: %s", self.topic)

    def run(self):
        """Start the consumer service."""
        LOG.info('Starting LoxiLB consumer service...')
        target = messaging.Target(
            topic=self.topic,
            namespace=octavia_constants.RPC_NAMESPACE_CONTROLLER_AGENT,
            server=self.server,
            fanout=False)
        
        self.endpoints = [endpoints.Endpoints()]
        self.message_listener = rpc.get_server(
            target, self.endpoints,
            executor='threading',
            access_policy=self.access_policy
        )
        
        LOG.info('LoxiLB consumer service starting on topic: %s, namespace: %s',
                 self.topic, octavia_constants.RPC_NAMESPACE_CONTROLLER_AGENT)
        self.message_listener.start()

    def terminate(self):
        """Terminate the consumer service."""
        if self.message_listener:
            LOG.info('Stopping LoxiLB consumer service...')
            self.message_listener.stop()

            LOG.info('LoxiLB consumer service stopped. Waiting for '
                     'final messages to be processed...')
            self.message_listener.wait()
        
        if self.endpoints:
            LOG.info('Shutting down LoxiLB endpoint worker executors...')
            for e in self.endpoints:
                try:
                    e.worker.executor.shutdown()
                except AttributeError:
                    pass
        
        super().terminate()
