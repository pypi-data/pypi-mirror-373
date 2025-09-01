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


class BaseLoxiLBComputeTask(task.Task):
    """Base task for LoxiLB compute operations."""
    def __init__(self, **kwargs):
        LOG.info(f"CONF config files: {CONF.config_file}")
        from octavia_loxilb_driver.common import config        
        config.register_opts(CONF)
        super().__init__(**kwargs)
        self.sdk = openstack_sdk_utils.get_sdk_connection()


class LoxiLBComputeCreate(BaseLoxiLBComputeTask):
    """Create a VM for LoxiLB load balancer with dual network interfaces."""
    def execute(self, lb_id, image_tag, flavor_name, vip_subnet_id):
        LOG.info(f"Provisioning LoxiLB VM for LB {lb_id}")
        try:
            # Validate VIP subnet ID
            if not vip_subnet_id:
                raise exceptions.LoxiLBAPIException("vip_subnet_id is required for provisioning LoxiLB VM")
            
            # Get VIP network ID from subnet
            vip_subnet = self.sdk.network.get_subnet(vip_subnet_id)
            if not vip_subnet:
                raise exceptions.LoxiLBAPIException(f"Could not find subnet with id {vip_subnet_id}")
            vip_network_id = vip_subnet.network_id
            LOG.info(f"Found VIP network_id {vip_network_id} for vip_subnet_id {vip_subnet_id}")

            security_group = getattr(CONF.loxilb, "security_group", None)
            if not security_group:
                security_group = "lb-mgmt-sec-grp"
            else:
                LOG.info(f"Using security_group from CONF.loxilb: {security_group}")

            key_name = getattr(CONF.loxilb, "key_name", "")
            if not key_name:
                LOG.info("No SSH key configured, creating VM without SSH key")
                key_name = "octavia_ssh_key"
            else:
                LOG.info(f"Using SSH key: {key_name}")
            
            # Use management network as primary (VIP port will be attached separately)
            use_mgmt_network = CONF.loxilb.use_mgmt_network
            mgmt_network_id = CONF.loxilb.mgmt_network_id            
        
            if use_mgmt_network and mgmt_network_id:
                LOG.info(f"Creating VM with management network {mgmt_network_id} as primary network")
                primary_network_id = mgmt_network_id
            else:
                LOG.info(f"No management network configured, using VIP network {vip_network_id} as primary network")
                primary_network_id = vip_network_id
        
            # Create VM with primary network only
            # The VIP port will be attached separately by LoxiLBAttachVIPPort task
            server = openstack_sdk_utils.create_vm(
                self.sdk,
                name=f"loxilb-{lb_id}",
                image_tag=image_tag,
                flavor_name=flavor_name,
                network_id=primary_network_id,
                key_name=key_name,
                security_groups=[security_group] if security_group else None
            )
        
            LOG.info(f"Created LoxiLB VM {server.id} with primary network {primary_network_id}. VIP port will be attached separately.")
            
            return server
        except Exception as e:
            LOG.error("Failed to create load balancer %s in LoxiLB: %s", lb_id, str(e))
            raise exceptions.LoxiLBAPIException(f"Failed to create load balancer: {str(e)}")

    def revert(self, result, lb_id, *args, **kwargs):
        if isinstance(result, failure.Failure):
            return
        server = result
        LOG.warning(f"Reverting LoxiLB VM create for LB {lb_id}, deleting VM {server.id}")
        try:
            openstack_sdk_utils.delete_vm(self.sdk, server.id)
        except Exception:
            LOG.exception("Failed to delete LoxiLB VM during revert")


class LoxiLBComputeDelete(BaseLoxiLBComputeTask):
    """Delete a LoxiLB VM."""
    def execute(self, lb_id):
        LOG.info(f"Deleting LoxiLB VM for LB {lb_id}")
        try:
            # Find the server by name convention (e.g., 'loxilb-<lb_id>')
            server_name = f"loxilb-{lb_id}"
            servers = list(self.sdk.compute.servers(name=server_name))
            if not servers:
                LOG.warning(f"No LoxiLB VM found for LB {lb_id} (name: {server_name})")
                return
            for server in servers:
                LOG.info(f"Deleting server {server.id} for LB {lb_id}")
                openstack_sdk_utils.delete_vm(self.sdk, server.id)
        except Exception as e:
            LOG.error(f"Failed to delete LoxiLB VM for LB {lb_id}: {e}")
            raise exceptions.LoxiLBAPIException(f"Failed to delete load balancer VM: {str(e)}")
