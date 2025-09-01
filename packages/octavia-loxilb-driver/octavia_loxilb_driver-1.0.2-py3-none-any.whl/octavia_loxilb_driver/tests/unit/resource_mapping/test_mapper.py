"""Unit tests for resource mapping between Octavia and LoxiLB."""

import copy
import json
import unittest
from unittest import mock

from oslo_config import cfg

from octavia_loxilb_driver.common import constants, exceptions, utils
from octavia_loxilb_driver.resource_mapping import mapper
from octavia_loxilb_driver.tests.unit import base

CONF = cfg.CONF


class TestResourceMapper(base.TestCase):
    """Test cases for ResourceMapper."""

    def setUp(self):
        super().setUp()
        # Set up test configuration
        self.config = mock.MagicMock()
        self.config.debug_resource_mapping = False
        
        # Create mapper instance
        self.mapper = mapper.ResourceMapper(self.config)
        
        # Test data templates
        self.sample_loadbalancer = {
            "id": "lb-12345",
            "name": "test-lb",
            "description": "Test load balancer",
            "vip_address": "192.168.1.100",
            "vip": {
                "ip_address": "192.168.1.100",
                "port_id": "port-123",
                "subnet_id": "subnet-123",
                "network_id": "network-123"
            },
            "admin_state_up": True,
            "provisioning_status": "ACTIVE",
            "operating_status": "ONLINE",
            "provider": "loxilb",
            "project_id": "project-123"
        }
        
        self.sample_listener = {
            "id": "listener-12345",
            "name": "test-listener",
            "protocol": "HTTP",
            "protocol_port": 80,
            "admin_state_up": True,
            "connection_limit": -1,
            "default_pool_id": "pool-12345"
        }
        
        self.sample_pool = {
            "id": "pool-12345",
            "name": "test-pool",
            "protocol": "HTTP",
            "lb_algorithm": "ROUND_ROBIN",
            "admin_state_up": True,
            "members": [
                {
                    "id": "member-1",
                    "address": "10.0.0.10",
                    "protocol_port": 8080,
                    "weight": 1,
                    "admin_state_up": True
                },
                {
                    "id": "member-2", 
                    "address": "10.0.0.11",
                    "protocol_port": 8080,
                    "weight": 1,
                    "admin_state_up": True
                }
            ]
        }
        
        self.sample_health_monitor = {
            "id": "hm-12345",
            "type": "HTTP",
            "delay": 5,
            "timeout": 3,
            "max_retries": 3,
            "url_path": "/health",
            "expected_codes": "200",
            "admin_state_up": True
        }
        
        # Set up the pool with default_pool reference in listener
        self.sample_listener["default_pool"] = self.sample_pool
        
        # Sample LoxiLB response data
        self.sample_loxilb_lb = {
            "serviceArguments": {
                "externalIP": "192.168.1.100",
                "port": 80,
                "protocol": "tcp",
                "sel": 0,
                "name": "test-lb",
                "monitor": False,
                "inactiveTimeOut": 60
            },
            "endpoints": [
                {
                    "endpointIP": "10.0.0.10",
                    "targetPort": 8080,
                    "weight": 1,
                    "state": "active"
                },
                {
                    "endpointIP": "10.0.0.11", 
                    "targetPort": 8080,
                    "weight": 1,
                    "state": "active"
                }
            ]
        }

    def test_loadbalancer_to_loxilb_basic(self):
        """Test basic load balancer mapping."""
        result = self.mapper.loadbalancer_to_loxilb(
            self.sample_loadbalancer,
            self.sample_listener,
            self.sample_pool
        )
        
        # Verify structure
        self.assertIn("serviceArguments", result)
        self.assertIn("endpoints", result)
        
        # Verify service arguments
        service_args = result["serviceArguments"]
        self.assertEqual(service_args["externalIP"], "192.168.1.100")
        self.assertEqual(service_args["port"], 80)
        self.assertEqual(service_args["protocol"], "tcp")
        self.assertEqual(service_args["sel"], 0)  # Round robin
        self.assertFalse(service_args["monitor"])  # No health monitor
        
        # Verify endpoints
        endpoints = result["endpoints"]
        self.assertEqual(len(endpoints), 2)
        self.assertEqual(endpoints[0]["endpointIP"], "10.0.0.10")
        self.assertEqual(endpoints[0]["targetPort"], 8080)
        self.assertEqual(endpoints[0]["weight"], 1)

    def test_loadbalancer_to_loxilb_with_ssl(self):
        """Test load balancer mapping with SSL configuration."""
        # Modify listener for HTTPS
        ssl_listener = copy.deepcopy(self.sample_listener)
        ssl_listener["protocol"] = "HTTPS"
        ssl_listener["protocol_port"] = 443
        ssl_listener["default_tls_container_ref"] = "container-123"
        
        result = self.mapper.loadbalancer_to_loxilb(
            self.sample_loadbalancer,
            ssl_listener,
            self.sample_pool
        )
        
        service_args = result["serviceArguments"]
        self.assertEqual(service_args["port"], 443)
        self.assertEqual(service_args["protocol"], "tcp")  # HTTPS maps to TCP in LoxiLB

    def test_loadbalancer_to_loxilb_with_health_monitor(self):
        """Test load balancer mapping with health monitoring."""
        # Add health monitor to pool
        pool_with_hm = copy.deepcopy(self.sample_pool)
        pool_with_hm["healthmonitor"] = self.sample_health_monitor
        
        result = self.mapper.loadbalancer_to_loxilb(
            self.sample_loadbalancer,
            self.sample_listener,
            pool_with_hm
        )
        
        service_args = result["serviceArguments"]
        self.assertTrue(service_args["monitor"])
        self.assertEqual(service_args["probetype"], "http")
        self.assertEqual(service_args["probeTimeout"], 3)
        self.assertEqual(service_args["probeRetries"], 3)

    def test_loadbalancer_to_loxilb_with_session_persistence(self):
        """Test load balancer mapping with session persistence."""
        # Add session persistence to pool
        pool_with_persistence = copy.deepcopy(self.sample_pool)
        pool_with_persistence["session_persistence"] = {
            "type": "SOURCE_IP"
        }
        pool_with_persistence["lb_algorithm"] = "SOURCE_IP"
        
        result = self.mapper.loadbalancer_to_loxilb(
            self.sample_loadbalancer,
            self.sample_listener,
            pool_with_persistence
        )
        
        service_args = result["serviceArguments"]
        self.assertEqual(service_args["sel"], 1)  # SOURCE_IP algorithm

    def test_loadbalancer_to_loxilb_validation_errors(self):
        """Test validation error handling."""
        # Test missing load balancer
        with self.assertRaises(exceptions.LoxiLBMappingException):
            self.mapper.loadbalancer_to_loxilb(None, self.sample_listener)
        
        # Test missing listener
        with self.assertRaises(exceptions.LoxiLBMappingException):
            self.mapper.loadbalancer_to_loxilb(self.sample_loadbalancer, None)
        
        # Test missing VIP address
        lb_no_vip = copy.deepcopy(self.sample_loadbalancer)
        del lb_no_vip["vip_address"]
        del lb_no_vip["vip"]
        
        with self.assertRaises(exceptions.LoxiLBMappingException):
            self.mapper.loadbalancer_to_loxilb(lb_no_vip, self.sample_listener)

    def test_loxilb_to_octavia_loadbalancer_basic(self):
        """Test basic reverse mapping."""
        result = self.mapper.loxilb_to_octavia_loadbalancer(self.sample_loxilb_lb)
        
        # Verify structure
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("vip_address", result)
        self.assertIn("listeners", result)
        
        # Verify basic fields
        self.assertEqual(result["vip_address"], "192.168.1.100")
        self.assertEqual(result["provider"], constants.PROVIDER_NAME)
        self.assertEqual(result["operating_status"], "ONLINE")  # Both endpoints active
        
        # Verify listener
        self.assertEqual(len(result["listeners"]), 1)
        listener = result["listeners"][0]
        self.assertEqual(listener["protocol"], "HTTP")  # TCP mapped to HTTP
        self.assertEqual(listener["protocol_port"], 80)
        
        # Verify pool and members
        pool = listener["default_pool"]
        self.assertEqual(pool["lb_algorithm"], "ROUND_ROBIN")
        self.assertEqual(len(pool["members"]), 2)

    def test_loxilb_to_octavia_loadbalancer_with_stats(self):
        """Test reverse mapping with statistics."""
        # Add statistics to LoxiLB response
        loxilb_with_stats = copy.deepcopy(self.sample_loxilb_lb)
        loxilb_with_stats["stats"] = {
            "bytes_in": "1000000",
            "bytes_out": "2000000",
            "total_connections": "1000"
        }
        
        # Add endpoint counters
        for endpoint in loxilb_with_stats["endpoints"]:
            endpoint["counter"] = json.dumps({
                "bytes_in": 500000,
                "bytes_out": 1000000,
                "total_connections": 500
            })
        
        result = self.mapper.loxilb_to_octavia_loadbalancer(loxilb_with_stats)
        
        # Verify statistics are included
        self.assertIn("stats", result)
        stats = result["stats"]
        self.assertEqual(stats["bytes_in"], 1000000)
        self.assertEqual(stats["total_connections"], 1000)

    def test_loxilb_to_octavia_loadbalancer_malformed_data(self):
        """Test error handling for malformed LoxiLB data."""
        # Test empty input
        with self.assertRaises(exceptions.LoxiLBMappingException):
            self.mapper.loxilb_to_octavia_loadbalancer({})
        
        # Test missing serviceArguments
        with self.assertRaises(exceptions.LoxiLBMappingException):
            self.mapper.loxilb_to_octavia_loadbalancer({"endpoints": []})
        
        # Test missing required fields in serviceArguments
        malformed_lb = {
            "serviceArguments": {"protocol": "tcp"},  # Missing IP and port
            "endpoints": []
        }
        with self.assertRaises(exceptions.LoxiLBMappingException):
            self.mapper.loxilb_to_octavia_loadbalancer(malformed_lb)

    def test_algorithm_mapping_bidirectional(self):
        """Test algorithm mapping in both directions."""
        # Test Octavia to LoxiLB
        self.assertEqual(utils.map_octavia_algorithm_to_loxilb("ROUND_ROBIN"), 0)
        self.assertEqual(utils.map_octavia_algorithm_to_loxilb("SOURCE_IP"), 3)  # Maps to persistence
        self.assertEqual(utils.map_octavia_algorithm_to_loxilb("SOURCE_IP_PORT"), 1)  # Maps to hash
        self.assertEqual(utils.map_octavia_algorithm_to_loxilb("LEAST_CONNECTIONS"), 4)
        
        # Test LoxiLB to Octavia
        self.assertEqual(utils.map_loxilb_algorithm_to_octavia(0), "ROUND_ROBIN")
        self.assertEqual(utils.map_loxilb_algorithm_to_octavia(1), "SOURCE_IP_PORT")  # Hash maps to SOURCE_IP_PORT
        self.assertEqual(utils.map_loxilb_algorithm_to_octavia(3), "SOURCE_IP")  # Persistence maps to SOURCE_IP
        self.assertEqual(utils.map_loxilb_algorithm_to_octavia(4), "LEAST_CONNECTIONS")

    def test_status_mapping_comprehensive(self):
        """Test all status mapping scenarios."""
        # Test with all endpoints online
        lb_online = copy.deepcopy(self.sample_loxilb_lb)
        for endpoint in lb_online["endpoints"]:
            endpoint["state"] = "active"
        
        result = self.mapper.loxilb_to_octavia_loadbalancer(lb_online)
        self.assertEqual(result["operating_status"], "ONLINE")
        
        # Test with all endpoints offline
        lb_offline = copy.deepcopy(self.sample_loxilb_lb)
        for endpoint in lb_offline["endpoints"]:
            endpoint["state"] = "inactive"
        
        result = self.mapper.loxilb_to_octavia_loadbalancer(lb_offline)
        self.assertEqual(result["operating_status"], "OFFLINE")
        
        # Test with mixed endpoint states (degraded)
        lb_degraded = copy.deepcopy(self.sample_loxilb_lb)
        lb_degraded["endpoints"][0]["state"] = "active"
        lb_degraded["endpoints"][1]["state"] = "inactive"
        
        result = self.mapper.loxilb_to_octavia_loadbalancer(lb_degraded)
        self.assertEqual(result["operating_status"], "DEGRADED")

    def test_deterministic_id_generation(self):
        """Test deterministic ID generation and mapping."""
        # Test that same inputs generate same ID
        id1 = utils.generate_deterministic_id(
            "loadbalancer", 
            external_ip="192.168.1.100", 
            port=80, 
            protocol="tcp"
        )
        id2 = utils.generate_deterministic_id(
            "loadbalancer",
            external_ip="192.168.1.100",
            port=80,
            protocol="tcp"
        )
        self.assertEqual(id1, id2)
        
        # Test that different inputs generate different IDs
        id3 = utils.generate_deterministic_id(
            "loadbalancer",
            external_ip="192.168.1.101",
            port=80,
            protocol="tcp"
        )
        self.assertNotEqual(id1, id3)

    def test_id_mapping_cache_operations(self):
        """Test ID mapping cache functionality."""
        cache = utils.create_id_mapping_cache()
        
        # Test storing mapping
        utils.store_id_mapping(
            cache,
            "octavia-id-123",
            "192.168.1.100:80/tcp",
            "loadbalancer",
            {"test": "metadata"}
        )
        
        # Test retrieving mappings
        loxilb_key = utils.get_loxilb_key_from_octavia_id(cache, "octavia-id-123")
        self.assertEqual(loxilb_key, "192.168.1.100:80/tcp")
        
        octavia_id = utils.get_octavia_id_from_loxilb_key(cache, "192.168.1.100:80/tcp")
        self.assertEqual(octavia_id, "octavia-id-123")
        
        # Test metadata storage
        metadata = cache["resource_metadata"]["octavia-id-123"]
        self.assertEqual(metadata["resource_type"], "loadbalancer")
        self.assertEqual(metadata["test"], "metadata")

    def test_protocol_mapping(self):
        """Test protocol mapping between Octavia and LoxiLB."""
        # Test Octavia to LoxiLB
        self.assertEqual(utils.map_octavia_protocol_to_loxilb("HTTP"), "tcp")
        self.assertEqual(utils.map_octavia_protocol_to_loxilb("HTTPS"), "tcp")
        self.assertEqual(utils.map_octavia_protocol_to_loxilb("TCP"), "tcp")
        self.assertEqual(utils.map_octavia_protocol_to_loxilb("UDP"), "udp")
        
        # Test LoxiLB to Octavia
        self.assertEqual(utils.map_loxilb_protocol_to_octavia("tcp"), "HTTP")
        self.assertEqual(utils.map_loxilb_protocol_to_octavia("udp"), "UDP")

    def test_service_key_operations(self):
        """Test LoxiLB service key generation and parsing."""
        # Test service key generation
        service_key = utils.get_loxilb_service_key("192.168.1.100", 80, "tcp")
        self.assertEqual(service_key, "192.168.1.100:80/tcp")
        
        # Test service key parsing
        parsed = utils.parse_loxilb_service_key("192.168.1.100:80/tcp")
        self.assertEqual(parsed["external_ip"], "192.168.1.100")
        self.assertEqual(parsed["port"], 80)
        self.assertEqual(parsed["protocol"], "tcp")
        
        # Test invalid service key
        with self.assertRaises(ValueError):
            utils.parse_loxilb_service_key("invalid-key")

    def test_health_monitor_mapping(self):
        """Test health monitor configuration mapping."""
        # Test with HTTP health monitor
        pool_with_http_hm = copy.deepcopy(self.sample_pool)
        pool_with_http_hm["healthmonitor"] = {
            "type": "HTTP",
            "delay": 10,
            "timeout": 5,
            "max_retries": 3,
            "url_path": "/api/health",
            "expected_codes": "200,201"
        }
        
        result = self.mapper.loadbalancer_to_loxilb(
            self.sample_loadbalancer,
            self.sample_listener,
            pool_with_http_hm
        )
        
        service_args = result["serviceArguments"]
        self.assertTrue(service_args["monitor"])
        self.assertEqual(service_args["probetype"], "http")
        self.assertIn("GET /api/health", service_args["probereq"])
        
        # Test with TCP health monitor
        pool_with_tcp_hm = copy.deepcopy(self.sample_pool)
        pool_with_tcp_hm["healthmonitor"] = {
            "type": "TCP",
            "delay": 5,
            "timeout": 3,
            "max_retries": 2
        }
        
        result = self.mapper.loadbalancer_to_loxilb(
            self.sample_loadbalancer,
            self.sample_listener,
            pool_with_tcp_hm
        )
        
        service_args = result["serviceArguments"]
        self.assertTrue(service_args["monitor"])
        self.assertEqual(service_args["probetype"], "tcp")

    def test_secondary_ips_and_allowed_sources(self):
        """Test secondary IPs and allowed sources mapping."""
        # Test with secondary IPs in load balancer
        lb_with_secondary = copy.deepcopy(self.sample_loadbalancer)
        lb_with_secondary["additional_vips"] = [
            {"ip_address": "192.168.1.101"},
            {"ip_address": "192.168.1.102"}
        ]
        
        result = self.mapper.loadbalancer_to_loxilb(
            lb_with_secondary,
            self.sample_listener,
            self.sample_pool
        )
        
        self.assertIn("secondaryIPs", result)
        self.assertEqual(len(result["secondaryIPs"]), 2)
        
        # Test with allowed CIDRs in listener
        listener_with_cidrs = copy.deepcopy(self.sample_listener)
        listener_with_cidrs["allowed_cidrs"] = ["10.0.0.0/8", "192.168.0.0/16"]
        
        result = self.mapper.loadbalancer_to_loxilb(
            self.sample_loadbalancer,
            listener_with_cidrs,
            self.sample_pool
        )
        
        self.assertIn("allowedSources", result)
        self.assertEqual(len(result["allowedSources"]), 2)

    def test_resource_name_generation(self):
        """Test resource name generation for LoxiLB."""
        # Test normal case
        name = utils.generate_resource_name("lb", "test-id-123")
        self.assertTrue(name.startswith(constants.LOXILB_RESOURCE_PREFIX))
        self.assertIn("lb", name)
        self.assertIn("test-id-123", name)
        
        # Test with invalid characters
        name = utils.generate_resource_name("lb", "test@id#123!")
        self.assertTrue(utils.validate_resource_name(name))
        
        # Test long ID truncation
        long_id = "a" * 200
        name = utils.generate_resource_name("lb", long_id)
        self.assertLessEqual(len(name), constants.MAX_RESOURCE_NAME_LENGTH)


if __name__ == "__main__":
    unittest.main()