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
from taskflow.patterns import linear_flow

from octavia_loxilb_driver.controller.worker.tasks import loxilb_compute_tasks
from octavia_loxilb_driver.controller.worker.tasks import loxilb_network_tasks

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class LoxiLBLoadBalancerFlows:
    def get_create_load_balancer_flow(self):
        """Creates a flow to provision a LoxiLB VM and allocate a VIP for LB."""
        create_lb_flow = linear_flow.Flow("CREATE_LOXILB_LB_FLOW")
        create_lb_flow.add(
            loxilb_compute_tasks.LoxiLBComputeCreate(
                name="LoxiLBComputeCreate",
                provides="loxilb_server"
            )
        )
        create_lb_flow.add(
            loxilb_network_tasks.LoxiLBAllocateVIP(
                name="LoxiLBAllocateVIP",
                requires=["loxilb_server"],
                provides="loxilb_vip_port"
            )
        )
        create_lb_flow.add(
            loxilb_network_tasks.LoxiLBPlugVIPPort(
                name="LoxiLBPlugVIPPort",
                requires=["loxilb_server", "loxilb_vip_port"],
                provides="loxilb_vip_interface"
            )
        )
        # Add more tasks here as needed (e.g., configure LoxiLB, register listeners)
        return create_lb_flow

    def get_delete_load_balancer_flow(self):
        """Creates a flow to deallocate VIP and delete the LoxiLB VM for LB."""
        delete_lb_flow = linear_flow.Flow("DELETE_LOXILB_LB_FLOW")
        delete_lb_flow.add(
            loxilb_network_tasks.LoxiLBDeallocateVIP(
                name="LoxiLBDeallocateVIP",
                requires=["vip_port_id"]
            )
        )
        delete_lb_flow.add(
            loxilb_compute_tasks.LoxiLBComputeDelete(
                name="LoxiLBComputeDelete",
                requires=["lb_id"]
            )
        )
        return delete_lb_flow
