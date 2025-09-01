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


class LoxiLBFlows:
    def get_create_loxilb_flow(self):
        """Creates a flow to provision a LoxiLB VM, allocate a VIP, and attach it."""
        create_loxilb_flow = linear_flow.Flow("CREATE_LOXILB_FLOW")
        create_loxilb_flow.add(
            loxilb_compute_tasks.LoxiLBComputeCreate(
                name="LoxiLBComputeCreate",
                provides="loxilb_server"
            )
        )
        create_loxilb_flow.add(
            loxilb_network_tasks.LoxiLBAllocateVIP(
                name="LoxiLBAllocateVIP",
                requires=["loxilb_server"],
                provides="loxilb_vip_port"
            )
        )
        create_loxilb_flow.add(
            loxilb_network_tasks.LoxiLBPlugVIPPort(
                name="LoxiLBPlugVIPPort",
                requires=["loxilb_server", "loxilb_vip_port", "vip_subnet_id"],
                provides="loxilb_amp_data"
            )
        )
        return create_loxilb_flow

    def get_delete_loxilb_flow(self):
        """Creates a flow to deallocate VIP and delete the LoxiLB VM."""
        delete_loxilb_flow = linear_flow.Flow("DELETE_LOXILB_FLOW")
        delete_loxilb_flow.add(
            loxilb_network_tasks.LoxiLBDeallocateVIP(
                name="LoxiLBDeallocateVIP",
                requires=["loxilb_vip_port"]
            )
        )
        delete_loxilb_flow.add(
            loxilb_compute_tasks.LoxiLBComputeDelete(
                name="LoxiLBComputeDelete",
                requires=["loxilb_server"]
            )
        )
        return delete_loxilb_flow
