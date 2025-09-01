# Copyright 2025 NLX-SeokHwanKong
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg
from oslo_log import log as logging
from taskflow import task
from taskflow.types import failure
from octavia_loxilb_driver.common import exceptions

from octavia_loxilb_driver.common import openstack_sdk_utils

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class BaseLoxiLBNetworkTask(task.Task):
    """Base task for LoxiLB network operations."""
    def __init__(self, **kwargs):
        LOG.info(f"CONF config files: {CONF.config_file}")        
        from octavia_loxilb_driver.common import config
        config.register_opts(CONF)
        super().__init__(**kwargs)
        self.sdk = openstack_sdk_utils.get_sdk_connection()


class LoxiLBAllocateVIP(BaseLoxiLBNetworkTask):
    """Allocate a VIP for the LoxiLB load balancer."""
    def execute(self, loxilb_server, lb_id, vip_subnet_id):
        LOG.info(f"Retrieving existing VIP Port for LB {lb_id}")
        try:            
            if not lb_id:
                raise exceptions.LoxiLBAPIException("lb_id is required for retrieving VIP Port")
            
            # Retrieve the existing VIP port created by Octavia
            # The VIP port name follows the pattern: octavia-lb-{lb_id}
            vip_port_name = f"octavia-lb-{lb_id}"
            LOG.info(f"Looking for existing VIP port with name: {vip_port_name}")
            
            # Search for the VIP port by name
            ports = list(self.sdk.network.ports(name=vip_port_name))
            if not ports:
                # Fallback: search by device_owner pattern
                LOG.info(f"Port not found by name, searching by device_owner pattern")
                ports = list(self.sdk.network.ports(device_owner=f"neutron:LOADBALANCERV2"))
                # Filter by load balancer ID in description or tags
                vip_port = None
                for port in ports:
                    if lb_id in (port.description or "") or lb_id in str(port.tags or []):
                        vip_port = port
                        break
                if not vip_port:
                    raise exceptions.LoxiLBAPIException(f"Could not find VIP port for load balancer {lb_id}")
            else:
                vip_port = ports[0]
            
            LOG.info(f"Found existing VIP port {vip_port.id} with IP {vip_port.fixed_ips[0]['ip_address']} for LB {lb_id}")
            return vip_port
        except Exception as e:
            LOG.error("Failed to retrieve VIP port for load balancer %s: %s", lb_id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to retrieve VIP port: {str(e)}")
        
    def revert(self, result, lb_id, *args, **kwargs):
        if isinstance(result, failure.Failure):
            return
        vip_port = result
        LOG.warning(f"Reverting VIP allocation for LB {lb_id}, deleting port {vip_port.id}")
        try:
            openstack_sdk_utils.delete_port(self.sdk, vip_port.id)
        except Exception:
            LOG.exception("Failed to delete VIP port during revert")


class LoxiLBPlugVIPPort(BaseLoxiLBNetworkTask):
    """Plug VIP port to LoxiLB VM using Allowed Address Pairs approach (similar to Amphora's PlugVIPAmphora)."""
    def execute(self, loxilb_server, loxilb_vip_port, vip_subnet_id):
        LOG.info(f"Plugging VIP port {loxilb_vip_port.id} to LoxiLB server {loxilb_server.id} using AAP approach")
        try:
            if not loxilb_server or not loxilb_vip_port or not vip_subnet_id:
                raise exceptions.LoxiLBAPIException("loxilb_server, loxilb_vip_port, and vip_subnet_id are required for plugging VIP port")
            
            # Debug: Check VIP port status before attachment
            LOG.info(f"VIP port details before plugging:")
            LOG.info(f"  Port ID: {loxilb_vip_port.id}")
            LOG.info(f"  Port status: {loxilb_vip_port.status}")
            LOG.info(f"  Network ID: {loxilb_vip_port.network_id}")
            LOG.info(f"  Fixed IPs: {loxilb_vip_port.fixed_ips}")
            LOG.info(f"  VIP Subnet ID: {vip_subnet_id}")
            
            # Use the new AAP approach similar to Amphora
            amp_data = openstack_sdk_utils.plug_aap_port(
                self.sdk, loxilb_server.id, loxilb_vip_port, vip_subnet_id
            )
            
            LOG.info(f"Successfully plugged VIP port {loxilb_vip_port.id} to server {loxilb_server.id} using AAP")
            LOG.info(f"  Base port ID: {amp_data['base_port_id']}")
            LOG.info(f"  VIP IP: {amp_data['vip_ip']}")
            LOG.info(f"  Allowed address pairs: {amp_data['allowed_address_pairs']}")
            
            return amp_data
            
        except Exception as e:
            LOG.error("Failed to plug VIP port %s to server %s using AAP: %s", loxilb_vip_port.id, loxilb_server.id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to plug VIP port using AAP: {str(e)}")
        
    def revert(self, result, loxilb_server, loxilb_vip_port, vip_subnet_id, *args, **kwargs):
        if isinstance(result, failure.Failure):
            return
        amp_data = result
        LOG.warning(f"Reverting VIP port plugging for server {loxilb_server.id}, removing AAP configuration")
        try:
            # Use the unplug function to clean up AAP configuration
            openstack_sdk_utils.unplug_aap_port(
                self.sdk, loxilb_server.id, loxilb_vip_port, amp_data['base_port_id']
            )
            LOG.info(f"Successfully reverted VIP port plugging for server {loxilb_server.id}")
        except Exception:
            LOG.exception("Failed to revert VIP port plugging during revert")


class LoxiLBDeallocateVIP(BaseLoxiLBNetworkTask):
    """Deallocate a VIP port."""
    def execute(self, vip_port_id):
        LOG.info(f"Deallocating VIP port {vip_port_id}")
        try:            
            if not vip_port_id:
                raise exceptions.LoxiLBAPIException("vip_port_id is required for deleting LoxiLB VIP Port")
            
            LOG.info(f"Found vip_port_id {vip_port_id} ")
            vip_port = openstack_sdk_utils.delete_port(self.sdk, vip_port_id)
            return vip_port
        except Exception as e:
            LOG.error("Failed to delete VIP port %s in LoxiLB: %s", vip_port_id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to delete VIP port: {str(e)}")

