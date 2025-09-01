#!/usr/bin/env python3
"""Setup command for LoxiLB Octavia Driver installation and configuration."""

import sys
import argparse
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

try:
    import openstack
    from openstack import connection
    HAS_OPENSTACK_SDK = True
except ImportError:
    HAS_OPENSTACK_SDK = False

from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

# Default configuration values
DEFAULT_LOXILB_FLAVOR = {
    'name': 'loxilb-flavor',
    'vcpus': 2,
    'ram': 8192,  # 8GB
    'disk': 40    # 40GB
}

DEFAULT_MGMT_NETWORK = {
    'name': 'octavia-mgmt-net',
    'cidr': '192.168.100.0/24'
}

DEFAULT_SECURITY_GROUP = {
    'name': 'loxilb-mgmt-sec-grp',
    'rules': [
        {'protocol': 'tcp', 'port_range_min': 22, 'port_range_max': 22},      # SSH
        {'protocol': 'tcp', 'port_range_min': 9443, 'port_range_max': 9443},  # Management
        {'protocol': 'tcp', 'port_range_min': 11111, 'port_range_max': 11111}, # LoxiLB API
        {'protocol': 'tcp', 'port_range_min': 8091, 'port_range_max': 8091},  # LoxiLB Health
        {'protocol': 'tcp', 'port_range_min': 22222, 'port_range_max': 22222}, # LoxiLB Data
        {'protocol': 'icmp', 'port_range_min': None, 'port_range_max': None},  # ICMP
    ]
}


class LoxiLBSetup:
    """LoxiLB Octavia Driver setup and configuration."""
    
    def __init__(self, args):
        """Initialize setup with command line arguments."""
        self.args = args
        self.conn = None
        self.verbose = args.verbose
        self.config_template = args.config_template
        
        # Load configuration profiles for different deployment types
        self.deployment_profiles = {
            'devstack': {
                'flavor': {'name': 'loxilb-devstack', 'vcpus': 1, 'ram': 4096, 'disk': 20},
                'network': {'name': 'octavia-mgmt-net-dev', 'cidr': '192.168.200.0/24'},
                'security_group': {'name': 'loxilb-dev-sec-grp'},
            },
            'kolla': {
                'flavor': DEFAULT_LOXILB_FLAVOR,
                'network': DEFAULT_MGMT_NETWORK,  
                'security_group': DEFAULT_SECURITY_GROUP,
            },
            'production': {
                'flavor': {'name': 'loxilb-prod', 'vcpus': 4, 'ram': 16384, 'disk': 80},
                'network': {'name': 'octavia-mgmt-net-prod', 'cidr': '10.0.100.0/24'},
                'security_group': {'name': 'loxilb-prod-sec-grp'},
            }
        }
        
        # Select deployment profile
        self.profile = self.deployment_profiles.get(args.deployment_type, 
                                                    self.deployment_profiles['kolla'])
        
        # Override with custom values if provided
        if args.custom_config:
            self._load_custom_config(args.custom_config)
        
    def print_info(self, message):
        """Print info message."""
        print(f"[INFO] {message}")
        if self.verbose:
            LOG.info(message)
    
    def print_success(self, message):
        """Print success message."""
        print(f"[SUCCESS] {message}")
        if self.verbose:
            LOG.info(message)
    
    def print_warning(self, message):
        """Print warning message."""
        print(f"[WARNING] {message}")
        if self.verbose:
            LOG.warning(message)
    
    def print_error(self, message):
        """Print error message."""
        print(f"[ERROR] {message}")
        if self.verbose:
            LOG.error(message)

    
    def _load_custom_config(self, config_file):
        """Load custom configuration from file."""
        try:
            import json
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
            
            # Merge custom config with profile
            for section in ['flavor', 'network', 'security_group']:
                if section in custom_config:
                    self.profile[section].update(custom_config[section])
                    
        except Exception as e:
            self.print_warning(f"Failed to load custom config {config_file}: {e}")
    
    def generate_octavia_config(self):
        """Generate Octavia configuration section for LoxiLB."""
        if not self.conn:
            return None
        
        # Get created resources
        flavor = self.conn.compute.find_flavor(self.profile['flavor']['name'])
        network = self.conn.network.find_network(self.profile['network']['name'])
        sg = self.conn.network.find_security_group(self.profile['security_group']['name'])
        image = None
        for img in self.conn.image.images():
            if img.name == 'loxilb-image':
                image = img
                break
        
        config_template = f"""
[loxilb]
# LoxiLB VM Configuration
image_id = {image.id if image else 'LOXILB_IMAGE_ID_HERE'}
flavor_id = {flavor.id if flavor else 'LOXILB_FLAVOR_ID_HERE'}
security_group_ids = {sg.id if sg else 'LOXILB_SECURITY_GROUP_ID_HERE'}
network_id = {network.id if network else 'LOXILB_NETWORK_ID_HERE'}

# API Configuration
api_timeout = 30
api_retries = 3
api_retry_interval = 5

# Authentication
loxilb_auth_type = none

# Deployment Configuration
use_mgmt_network = true
mgmt_network_id = {network.id if network else 'LOXILB_NETWORK_ID_HERE'}
default_topology = SINGLE

# OpenStack Authentication (legacy - use [service_auth] instead)
auth_url = {os.environ.get('OS_AUTH_URL', 'http://localhost:5000')}
auth_type = password
username = octavia
project_name = service
user_domain_name = Default
project_domain_name = Default
"""
        return config_template
    
    def check_prerequisites(self):
        """Check system prerequisites."""
        self.print_info("Checking prerequisites...")
        
        if not HAS_OPENSTACK_SDK:
            self.print_error("OpenStack SDK not available. Install with: pip install openstacksdk")
            return False
        
        # Check for OpenStack credentials
        required_env = ['OS_AUTH_URL', 'OS_USERNAME', 'OS_PASSWORD', 'OS_PROJECT_NAME']
        missing_env = [env for env in required_env if not os.environ.get(env)]
        
        if missing_env:
            self.print_error(f"Missing OpenStack environment variables: {', '.join(missing_env)}")
            self.print_error("Please source your OpenStack RC file first")
            return False
        
        try:
            self.conn = openstack.connect()
            self.conn.authorize()
            self.print_success("OpenStack connection established")
            return True
        except Exception as e:
            self.print_error(f"Failed to connect to OpenStack: {e}")
            return False
    
    def setup_image(self):
        """Download and register LoxiLB image if specified."""
        if not self.args.image_url:
            self.print_info("No image URL provided, skipping image setup")
            return True
        
        self.print_info(f"Setting up LoxiLB image from {self.args.image_url}")
        
        # Check if image already exists
        existing_image = None
        for image in self.conn.image.images():
            if image.name == 'loxilb-image':
                existing_image = image
                break
        
        if existing_image and not self.args.force:
            self.print_success(f"LoxiLB image already exists: {existing_image.id}")
            return True
        
        try:
            # Download image
            self.print_info("Downloading LoxiLB image...")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.qcow2') as tmp_file:
                import urllib.request
                urllib.request.urlretrieve(self.args.image_url, tmp_file.name)
                
                # Upload to Glance
                self.print_info("Uploading image to Glance...")
                image = self.conn.image.create_image(
                    name='loxilb-image',
                    filename=tmp_file.name,
                    disk_format='qcow2',
                    container_format='bare',
                    wait=True
                )
                
                os.unlink(tmp_file.name)
                self.print_success(f"LoxiLB image uploaded: {image.id}")
                return True
                
        except Exception as e:
            self.print_error(f"Failed to setup LoxiLB image: {e}")
            return False
    
    def setup_flavor(self):
        """Create LoxiLB flavor based on deployment profile."""
        flavor_config = self.profile['flavor']
        self.print_info(f"Setting up LoxiLB flavor: {flavor_config['name']}")
        
        # Check if flavor exists
        existing_flavor = self.conn.compute.find_flavor(flavor_config['name'])
        if existing_flavor and not self.args.force:
            self.print_success(f"LoxiLB flavor already exists: {existing_flavor.id}")
            return True
        
        try:
            flavor = self.conn.compute.create_flavor(
                name=flavor_config['name'],
                vcpus=flavor_config['vcpus'],
                ram=flavor_config['ram'],
                disk=flavor_config['disk']
            )
            self.print_success(f"LoxiLB flavor created: {flavor.id}")
            return True
        except Exception as e:
            self.print_error(f"Failed to create LoxiLB flavor: {e}")
            return False
    
    def setup_networks(self):
        """Create management network based on deployment profile."""
        network_config = self.profile['network']
        self.print_info(f"Setting up management network: {network_config['name']}")
        
        # Check if network exists
        existing_network = self.conn.network.find_network(network_config['name'])
        if existing_network and not self.args.force:
            self.print_success(f"Management network already exists: {existing_network.id}")
            return True
        
        try:
            # Create network
            network = self.conn.network.create_network(
                name=network_config['name']
            )
            
            # Create subnet
            subnet = self.conn.network.create_subnet(
                name=f"{network_config['name']}-subnet",
                network_id=network.id,
                cidr=network_config['cidr'],
                ip_version=4
            )
            
            self.print_success(f"Management network created: {network.id}")
            self.print_success(f"Management subnet created: {subnet.id}")
            return True
        except Exception as e:
            self.print_error(f"Failed to create management network: {e}")
            return False
    
    def setup_security_groups(self):
        """Create security group for LoxiLB management based on deployment profile."""
        sg_config = self.profile['security_group']
        self.print_info(f"Setting up security groups: {sg_config['name']}")
        
        # Check if security group exists
        existing_sg = self.conn.network.find_security_group(sg_config['name'])
        if existing_sg and not self.args.force:
            self.print_success(f"Security group already exists: {existing_sg.id}")
            return True
        
        try:
            # Create security group
            sg = self.conn.network.create_security_group(
                name=sg_config['name'],
                description="Security group for LoxiLB management access"
            )
            
            # Add rules from DEFAULT_SECURITY_GROUP (common rules for all profiles)
            for rule in DEFAULT_SECURITY_GROUP['rules']:
                rule_data = {
                    'security_group_id': sg.id,
                    'direction': 'ingress',
                    'ethertype': 'IPv4',
                    'protocol': rule['protocol']
                }
                
                if rule['port_range_min'] is not None:
                    rule_data['port_range_min'] = rule['port_range_min']
                    rule_data['port_range_max'] = rule['port_range_max']
                
                self.conn.network.create_security_group_rule(**rule_data)
            
            self.print_success(f"Security group created: {sg.id}")
            return True
        except Exception as e:
            self.print_error(f"Failed to create security group: {e}")
            return False
    
    def configure_octavia(self):
        """Configure Octavia to use LoxiLB driver."""
        self.print_info("Configuring Octavia...")
        
        # Generate configuration template
        config_template = self.generate_octavia_config()
        if config_template:
            self.print_info("Generated LoxiLB configuration section:")
            print(config_template)
            
            if self.args.output_config:
                try:
                    with open(self.args.output_config, 'w') as f:
                        f.write(config_template)
                    self.print_success(f"Configuration written to {self.args.output_config}")
                except Exception as e:
                    self.print_error(f"Failed to write configuration: {e}")
        
        self.print_warning("Manual Octavia configuration steps:")
        self.print_info("1. Add 'loxilb:LoxiLB driver' to enabled_provider_drivers in [api_settings]")
        self.print_info("2. Add 'loxilb' to enabled_provider_agents in [driver_agent]")
        self.print_info("3. Add the [loxilb] section shown above to octavia.conf")
        self.print_info("4. Restart Octavia services: systemctl restart octavia-*")
        
        return True
    
    def run(self):
        """Run the complete setup process."""
        self.print_info("Starting LoxiLB Octavia Driver setup...")
        
        steps = [
            self.check_prerequisites,
            self.setup_image,
            self.setup_flavor,
            self.setup_networks,
            self.setup_security_groups,
            self.configure_octavia,
        ]
        
        for step in steps:
            if not step():
                self.print_error("Setup failed")
                return False
        
        self.print_success("LoxiLB Octavia Driver setup completed successfully!")
        return True


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description='Setup LoxiLB Octavia Driver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic setup (requires existing LoxiLB image in Glance)
  octavia-loxilb-setup
  
  # Setup with automatic image download
  octavia-loxilb-setup --image-url https://github.com/loxilb-io/loxilb/releases/latest/download/loxilb-vm.qcow2
  
  # Setup for DevStack environment
  octavia-loxilb-setup --deployment-type devstack
  
  # Setup for production with custom configuration
  octavia-loxilb-setup --deployment-type production --custom-config /path/to/config.json
  
  # Force recreate all resources and output configuration
  octavia-loxilb-setup --force --output-config /tmp/loxilb-octavia.conf
        """
    )
    
    parser.add_argument('--image-url', 
                       help='URL to download LoxiLB VM image')
    parser.add_argument('--force', action='store_true',
                       help='Force recreation of existing resources')
    parser.add_argument('--config-file',
                       help='Path to Octavia configuration file')
    parser.add_argument('--deployment-type', 
                       choices=['devstack', 'kolla', 'production'],
                       default='kolla',
                       help='Deployment type for resource sizing and naming (default: kolla)')
    parser.add_argument('--custom-config',
                       help='Path to JSON file with custom configuration overrides')
    parser.add_argument('--output-config',
                       help='Path to output generated Octavia configuration section')
    parser.add_argument('--config-template',
                       help='Configuration template to use')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.setup(CONF, 'octavia-loxilb-setup')
    
    setup = LoxiLBSetup(args)
    
    try:
        success = setup.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        setup.print_error("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        setup.print_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()