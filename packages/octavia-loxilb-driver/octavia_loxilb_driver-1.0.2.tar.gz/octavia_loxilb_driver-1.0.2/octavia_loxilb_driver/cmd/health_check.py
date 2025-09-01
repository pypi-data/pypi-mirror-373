#!/usr/bin/env python3
"""Health check command for LoxiLB Octavia Driver."""

import sys
import argparse
from octavia_loxilb_driver.api.loxilb_client import LoxiLBAPIClient
from octavia_loxilb_driver.common import config
from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def main():
    """Main health check function."""
    parser = argparse.ArgumentParser(description='LoxiLB Octavia Driver Health Check')
    parser.add_argument('--config-file', help='Path to configuration file')
    parser.add_argument('--endpoint', help='LoxiLB API endpoint to check')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup configuration
    if args.config_file:
        CONF(args=['--config-file', args.config_file])
    else:
        CONF(args=[])
    
    config.register_opts(CONF)
    
    if args.verbose:
        logging.setup(CONF, 'octavia-loxilb-health-check')
        LOG.info("Starting LoxiLB health check...")
    
    try:
        if args.endpoint:
            # Check specific endpoint
            from octavia_loxilb_driver.common.config import LoxiLBConfig
            config_obj = LoxiLBConfig()
            config_obj.api_endpoints = [args.endpoint]
            client = LoxiLBAPIClient(config_obj)
        else:
            # Use configuration from file
            client = LoxiLBAPIClient(CONF.loxilb)
        
        if client.health_check():
            if args.verbose:
                LOG.info("Health check passed")
            print("OK: LoxiLB endpoints are healthy")
            sys.exit(0)
        else:
            if args.verbose:
                LOG.error("Health check failed")
            print("ERROR: LoxiLB endpoints are not healthy")
            sys.exit(1)
            
    except Exception as e:
        if args.verbose:
            LOG.exception("Health check error: %s", str(e))
        print(f"ERROR: Health check failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()