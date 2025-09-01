"""Integration tests for the LoxiLB API client.

These tests are designed to be run against actual LoxiLB instances
configured in the docker-compose.yml file. Before running these tests,
ensure that the LoxiLB containers are running:

    cd octavia-loxilb-driver/docker
    docker-compose up -d

The tests will connect to the LoxiLB instances on ports 8080 and 8081.
"""

import os
import sys
import time
import unittest

from oslo_config import cfg
from oslo_log import log as logging

# Add the parent directory to the path so we can import the driver modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from octavia_loxilb_driver.api.loxilb_client import LoxiLBAPIClient
from octavia_loxilb_driver.common import constants, exceptions

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class TestLoxiLBAPIClientIntegration(unittest.TestCase):
    """Integration tests for LoxiLBAPIClient.

    These tests require actual LoxiLB instances to be running.
    """

    def setUp(self):
        """Set up the test environment."""
        super(TestLoxiLBAPIClientIntegration, self).setUp()

        # Register default oslo.log options
        logging.register_options(CONF)

        # Configure logging
        try:
            logging.setup(CONF, "octavia_loxilb_driver")
            logging.set_defaults(
                default_log_levels=["requests=WARN", "urllib3=WARN", "oslo_config=WARN"]
            )
        except Exception as e:
            print(f"Warning: Could not set up logging: {e}")
            # Continue without formal logging setup

        # Configure the LoxiLB client
        CONF.register_opts(
            [
                cfg.ListOpt(
                    "api_endpoints",
                    default=["http://localhost:8080", "http://localhost:8081"],
                ),  # TODO: change to use docker-compose.yml
                cfg.StrOpt("auth_type", default="none"),
                cfg.StrOpt("username", default=""),
                cfg.StrOpt("password", default=""),
                cfg.StrOpt("api_token", default=""),
                cfg.BoolOpt("tls_verify_cert", default=True),
                cfg.StrOpt("tls_ca_cert_file", default=""),
                cfg.StrOpt("tls_client_cert_file", default=""),
                cfg.StrOpt("tls_client_key_file", default=""),
                cfg.IntOpt("api_timeout", default=10),
                cfg.IntOpt("api_retries", default=3),
                cfg.FloatOpt("api_retry_interval", default=1.0),
                cfg.IntOpt("api_connection_pool_size", default=10),
                cfg.IntOpt("api_max_connections_per_pool", default=10),
                cfg.BoolOpt("debug_api_calls", default=True),
            ],
            group="loxilb",
        )

        # Create the client
        self.client = LoxiLBAPIClient()

        # Test data for creating a load balancer
        self.test_lb_data = {
            "serviceArguments": {
                "externalIP": "192.168.1.100",
                "port": 80,
                "protocol": "tcp",
                "name": "test-integration-lb",
                "mode": constants.LB_MODE_DNAT,
                "monitor": True,
                "monitorArgs": {
                    "port": 80,
                    "interval": 5,
                    "timeout": 3,
                    "retries": 3,
                    "type": "tcp",
                },
            },
            "endpoints": [
                {"endpointIP": "10.0.0.10", "targetPort": 8080, "weight": 1},
                {"endpointIP": "10.0.0.11", "targetPort": 8080, "weight": 1},
            ],
            "lbAttrArguments": {
                "selectors": {"app": "web"},
                "secureMode": constants.LB_SECURITY_PLAIN,
                "lbMode": constants.LB_MODE_DNAT,
                "method": constants.LB_ALGORITHM_ROUND_ROBIN,
            },
        }

        # Clean up any existing test load balancers
        try:
            lb = self.client.get_loadbalancer_by_name("test-integration-lb")
            if lb:
                self.client.delete_loadbalancer_by_name("test-integration-lb")
                time.sleep(1)  # Allow time for deletion to complete
        except exceptions.LoxiLBApiException:
            pass

    def tearDown(self):
        """Clean up after the tests."""
        super(TestLoxiLBAPIClientIntegration, self).tearDown()

        # Clean up any test load balancers
        try:
            self.client.delete_loadbalancer_by_name("test-integration-lb")
        except exceptions.LoxiLBApiException:
            pass

    def test_health_check(self):
        """Test health check functionality."""
        try:
            result = self.client.health_check()
            self.assertTrue(result, "Health check failed")
        except exceptions.LoxiLBApiException as e:
            self.fail(f"Health check raised exception: {e}")

    def test_create_list_get_delete_loadbalancer(self):
        """Test the full lifecycle of a load balancer."""
        # Create load balancer
        try:
            create_result = self.client.create_loadbalancer(self.test_lb_data)
            self.assertIsNotNone(create_result)
            print(f"Created load balancer: {create_result}")

            # Wait for LB to be fully created
            time.sleep(2)

            # List load balancers
            list_result = self.client.list_loadbalancers()
            self.assertIsNotNone(list_result)
            self.assertIsInstance(list_result, list)
            print(f"Listed {len(list_result)} load balancers")

            # Get load balancer by name
            get_name_result = self.client.get_loadbalancer_by_name(
                "test-integration-lb"
            )
            self.assertIsNotNone(get_name_result)
            self.assertEqual(
                "test-integration-lb",
                get_name_result.get("serviceArguments", {}).get("name"),
            )
            print(
                f"Got load balancer by name: {get_name_result.get('serviceArguments', {}).get('name')}"
            )

            # Get load balancer by service properties
            get_service_result = self.client.get_loadbalancer_by_service(
                "192.168.1.100", 80, "tcp"
            )
            self.assertIsNotNone(get_service_result)
            print(
                f"Got load balancer by service: {get_service_result.get('serviceArguments', {}).get('name')}"
            )

            # Delete load balancer by name
            delete_result = self.client.delete_loadbalancer_by_name(
                "test-integration-lb"
            )
            self.assertTrue(delete_result)
            print("Deleted load balancer by name")

            # Verify deletion
            time.sleep(2)
            get_after_delete = self.client.get_loadbalancer_by_name(
                "test-integration-lb"
            )
            self.assertIsNone(get_after_delete)
            print("Verified load balancer deletion")

        except exceptions.LoxiLBApiException as e:
            self.fail(f"Test failed with exception: {e}")

    def test_delete_loadbalancer_rule(self):
        """Test deleting a load balancer by service properties."""
        # Create load balancer
        try:
            create_result = self.client.create_loadbalancer(self.test_lb_data)
            self.assertIsNotNone(create_result)
            print(f"Created load balancer: {create_result}")

            # Wait for LB to be fully created
            time.sleep(2)

            # Delete load balancer by service properties
            delete_result = self.client.delete_loadbalancer_rule(
                "192.168.1.100", 80, "tcp"
            )
            self.assertTrue(delete_result)
            print("Deleted load balancer by service properties")

            # Verify deletion
            time.sleep(2)
            get_after_delete = self.client.get_loadbalancer_by_name(
                "test-integration-lb"
            )
            self.assertIsNone(get_after_delete)
            print("Verified load balancer deletion")

        except exceptions.LoxiLBApiException as e:
            self.fail(f"Test failed with exception: {e}")

    def test_get_status(self):
        """Test getting LoxiLB status."""
        try:
            status = self.client.get_status()
            self.assertIsNotNone(status)
            print(f"LoxiLB status: {status}")
        except exceptions.LoxiLBApiException as e:
            self.fail(f"Get status failed with exception: {e}")


if __name__ == "__main__":
    unittest.main()
