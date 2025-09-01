#!/usr/bin/env python

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

import sys

import cotyledon
from cotyledon import oslo_config_glue
from oslo_config import cfg
from oslo_log import log as logging

from octavia.common import service as octavia_service
from octavia_loxilb_driver.common import config as loxilb_config
from octavia_loxilb_driver.controller.queue import consumer

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def main():
    """Main entry point for the LoxiLB worker service."""
    # Initialize Octavia service
    octavia_service.prepare_service(sys.argv)
    
    # Register LoxiLB configuration options
    loxilb_config.register_opts()
    
    # Create service manager
    sm = cotyledon.ServiceManager()
    
    # Add LoxiLB consumer service
    workers = CONF.controller_worker.workers if hasattr(CONF.controller_worker, 'workers') else 1
    LOG.info("Starting LoxiLB worker with %d workers", workers)
    sm.add(consumer.ConsumerService, workers=workers, args=(CONF,))
    
    # Setup configuration reloading
    oslo_config_glue.setup(sm, CONF, reload_method="mutate")
    
    # Run the service manager
    sm.run()


if __name__ == '__main__':
    main()
