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
from oslo_reports import guru_meditation_report as gmr

from octavia.common import service as octavia_service
from octavia_loxilb_driver.common import config as loxilb_config
from octavia_loxilb_driver.controller.queue import consumer
from octavia_loxilb_driver import version

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def main():
    """Main entry point for starting the LoxiLB controller worker."""
    # Use Octavia's service preparation function
    octavia_service.prepare_service(sys.argv)
    
    # Register LoxiLB configuration options
    loxilb_config.register_opts(CONF)
    
    # Set up logging
    LOG.info("Starting LoxiLB controller worker...")
    LOG.debug('Full set of CONF:')
    CONF.log_opt_values(LOG, logging.DEBUG)
    
    # Set up guru meditation report
    gmr.TextGuruMeditation.setup_autorun(version)
    
    # Create and run the service manager with cotyledon
    sm = cotyledon.ServiceManager()
    sm.add(consumer.ConsumerService,
           workers=CONF.loxilb.worker_threads,
           args=(CONF,))
    
    # Set up configuration reloading
    oslo_config_glue.setup(sm, CONF, reload_method="mutate")
    
    LOG.info("LoxiLB controller worker starting with %d workers", 
             CONF.loxilb.worker_threads)
    
    # Run the service manager
    sm.run()


if __name__ == '__main__':
    main()
