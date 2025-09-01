"""Unit tests for the LoxiLB API client."""

import json
from unittest import mock

import requests
from oslo_config import cfg

from octavia_loxilb_driver.api.loxilb_client import LoxiLBAPIClient
from octavia_loxilb_driver.common import constants
from octavia_loxilb_driver.tests.unit import base

CONF = cfg.CONF


class TestLoxiLBAPIClient(base.TestCase):
    """Test cases         # Mock connection error
        self.session_mock.request.side_effect = requests.exceptions.ConnectionError(
            "Connection refused"
        )

        # Call method and verify exception (wrapped in RetryError)
        with self.assertRaises(RetryError):
            self.client.get("/some/path")

        # Mock timeout error
        self.session_mock.request.side_effect = requests.exceptions.Timeout(
            "Request timed out"
        )

        # Call method and verify exception (wrapped in RetryError)
        with self.assertRaises(RetryError):
            self.client.get("/some/path")nt."""

    def setUp(self):
        super(TestLoxiLBAPIClient, self).setUp()

        # Mock requests.Session
        self.session_mock = mock.MagicMock()
        self.session_patch = mock.patch(
            "requests.Session", return_value=self.session_mock
        )
        self.session_patch.start()

        # Create client
        self.client = LoxiLBAPIClient()

        # Set up common test data
        self.test_lb_data = {
            "serviceArguments": {
                "externalIP": "192.168.1.100",
                "port": 80,
                "protocol": "tcp",
                "name": "test-lb",
            },
            "endpoints": [{"endpointIP": "10.0.0.1", "weight": 1, "targetPort": 8080}],
        }

    def test_create_loadbalancer(self):
        """Test create_loadbalancer method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123"}
        mock_response.content = json.dumps({"id": "123"}).encode("utf-8")
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.create_loadbalancer(self.test_lb_data)

        # Verify
        self.session_mock.request.assert_called_once_with(
            "POST",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['loadbalancer']}",
            json=self.test_lb_data,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertEqual({"id": "123"}, result)

    def test_list_loadbalancers(self):
        """Test list_loadbalancers method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"lbAttr": [self.test_lb_data]}
        mock_response.content = json.dumps({"lbAttr": [self.test_lb_data]}).encode(
            "utf-8"
        )
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.list_loadbalancers()

        # Verify
        self.session_mock.request.assert_called_once_with(
            "GET",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['loadbalancer_all']}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertEqual([self.test_lb_data], result)

    def test_get_loadbalancer_by_service(self):
        """Test get_loadbalancer_by_service method."""
        # Mock response for list_loadbalancers
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"lbAttr": [self.test_lb_data]}
        mock_response.content = json.dumps({"lbAttr": [self.test_lb_data]}).encode(
            "utf-8"
        )
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.get_loadbalancer_by_service("192.168.1.100", 80, "tcp")

        # Verify
        self.session_mock.request.assert_called_once_with(
            "GET",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['loadbalancer_all']}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertEqual(self.test_lb_data, result)

    def test_get_loadbalancer_by_name(self):
        """Test get_loadbalancer_by_name method."""
        # Mock response for list_loadbalancers
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"lbAttr": [self.test_lb_data]}
        mock_response.content = json.dumps({"lbAttr": [self.test_lb_data]}).encode(
            "utf-8"
        )
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.get_loadbalancer_by_name("test-lb")

        # Verify
        self.session_mock.request.assert_called_once_with(
            "GET",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['loadbalancer_all']}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertEqual(self.test_lb_data, result)

    def test_delete_loadbalancer_rule(self):
        """Test delete_loadbalancer_rule method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 204
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.delete_loadbalancer_rule("192.168.1.100", 80, "tcp")

        # Verify
        expected_path = (
            f"{constants.API_PATHS['loadbalancer_by_service']}/192.168.1.100"
            f"/port/80/protocol/tcp"
        )
        self.session_mock.request.assert_called_once_with(
            "DELETE",
            f"{self.client.endpoints[0]['url']}{expected_path}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertTrue(result)

    def test_delete_loadbalancer_by_name(self):
        """Test delete_loadbalancer_by_name method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 204
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.delete_loadbalancer_by_name("test-lb")

        # Verify
        expected_path = f"{constants.API_PATHS['loadbalancer_by_name']}/test-lb"
        self.session_mock.request.assert_called_once_with(
            "DELETE",
            f"{self.client.endpoints[0]['url']}{expected_path}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertTrue(result)

    def test_delete_all_loadbalancers(self):
        """Test delete_all_loadbalancers method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 204
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.delete_all_loadbalancers()

        # Verify
        self.session_mock.request.assert_called_once_with(
            "DELETE",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['loadbalancer_all']}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertTrue(result)

    def test_get_status(self):
        """Test get_status method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_response.content = json.dumps({"status": "ok"}).encode("utf-8")
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.get_status()

        # Verify
        self.session_mock.request.assert_called_once_with(
            "GET",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['status']}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertEqual({"status": "ok"}, result)

    def test_health_check(self):
        """Test health_check method."""
        # Mock get_status
        with mock.patch.object(self.client, "get_status") as mock_get_status:
            mock_get_status.return_value = {"status": "ok"}

            # Call method
            result = self.client.health_check()

            # Verify
            mock_get_status.assert_called_once()
            self.assertTrue(result)

    def test_health_check_failure(self):
        """Test health_check method with failure."""
        # Mock get_status
        with mock.patch.object(self.client, "get_status") as mock_get_status:
            mock_get_status.return_value = {}

            # Call method
            result = self.client.health_check()

            # Verify
            mock_get_status.assert_called_once()
            self.assertFalse(result)

    def test_get_metrics(self):
        """Test get_metrics method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_metrics = "# HELP loxilb_processed_bytes Total bytes processed\n# TYPE loxilb_processed_bytes counter\nloxilb_processed_bytes 1024"
        mock_response.json.return_value = mock_metrics
        mock_response.content = mock_metrics.encode("utf-8")
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.get_metrics()

        # Verify
        self.session_mock.request.assert_called_once_with(
            "GET",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['metrics']}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertEqual(mock_metrics, result)

    def test_get_lb_rule_count_metrics(self):
        """Test get_lb_rule_count_metrics method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_metrics = {"lbRuleCount": 5}
        mock_response.json.return_value = mock_metrics
        mock_response.content = json.dumps(mock_metrics).encode("utf-8")
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.get_lb_rule_count_metrics()

        # Verify
        self.session_mock.request.assert_called_once_with(
            "GET",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['metrics_lbrulecount']}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertEqual(mock_metrics, result)

    def test_get_lb_processed_traffic_metrics(self):
        """Test get_lb_processed_traffic_metrics method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_metrics = {"bytesProcessed": 1024, "packetsProcessed": 10}
        mock_response.json.return_value = mock_metrics
        mock_response.content = json.dumps(mock_metrics).encode("utf-8")
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.get_lb_processed_traffic_metrics()

        # Verify
        self.session_mock.request.assert_called_once_with(
            "GET",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['metrics_lbprocessedtraffic']}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertEqual(mock_metrics, result)

    def test_get_endpoint_distribution_traffic_metrics(self):
        """Test get_endpoint_distribution_traffic_metrics method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_metrics = {
            "test-lb": {"10.0.0.1": {"bytesProcessed": 512, "packetsProcessed": 5}}
        }
        mock_response.json.return_value = mock_metrics
        mock_response.content = json.dumps(mock_metrics).encode("utf-8")
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.get_endpoint_distribution_traffic_metrics()

        # Verify
        self.session_mock.request.assert_called_once_with(
            "GET",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['metrics_epdisttraffic']}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertEqual(mock_metrics, result)

    def test_get_service_distribution_traffic_metrics(self):
        """Test get_service_distribution_traffic_metrics method."""
        # Mock response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_metrics = {"test-lb": {"bytesProcessed": 1024, "packetsProcessed": 10}}
        mock_response.json.return_value = mock_metrics
        mock_response.content = json.dumps(mock_metrics).encode("utf-8")
        self.session_mock.request.return_value = mock_response

        # Call method
        result = self.client.get_service_distribution_traffic_metrics()

        # Verify
        self.session_mock.request.assert_called_once_with(
            "GET",
            f"{self.client.endpoints[0]['url']}{constants.API_PATHS['metrics_servicedisttraffic']}",
            json=None,
            params={},
            timeout=CONF.loxilb.api_timeout,
        )
        self.assertEqual(mock_metrics, result)


    # def test_error_handling(self):
    #     """Test error handling in API client."""
    #     from tenacity import RetryError
        
    #     # Mock response for 404
    #     mock_response = mock.MagicMock()
    #     mock_response.status_code = 404
    #     mock_response.text = "Not found"
    #     self.session_mock.request.return_value = mock_response

    #     # Call method and verify exception (wrapped in RetryError)
    #     with self.assertRaises(RetryError):
    #         self.client.get("/some/path")

    #     # Mock response for 409
    #     mock_response.status_code = 409
    #     mock_response.text = "Conflict"

    #     # Call method and verify exception (wrapped in RetryError)
    #     with self.assertRaises(RetryError):
    #         self.client.get("/some/path")

    #     # Mock response for 401
    #     mock_response.status_code = 401
    #     mock_response.text = "Unauthorized"

    #     # Call method and verify exception (wrapped in RetryError)
    #     with self.assertRaises(RetryError):
    #         self.client.get("/some/path")

    #     # Mock response for 500
    #     mock_response.status_code = 500
    #     mock_response.text = "Server error"

    #     # Call method and verify exception (wrapped in RetryError)
    #     with self.assertRaises(RetryError):
    #         self.client.get("/some/path")

    #     # Mock connection error
    #     self.session_mock.request.side_effect = requests.exceptions.ConnectionError(
    #         "Connection refused"
    #     )

    #     # Call method and verify exception (wrapped in RetryError)
    #     with self.assertRaises(RetryError):
    #         self.client.get("/some/path")

    #     # Mock timeout error
    #     self.session_mock.request.side_effect = requests.exceptions.Timeout(
    #         "Request timed out"
    #     )

    #     # Call method and verify exception
    #     with self.assertRaises(exceptions.LoxiLBTimeoutException):
    #         self.client.get_status()
