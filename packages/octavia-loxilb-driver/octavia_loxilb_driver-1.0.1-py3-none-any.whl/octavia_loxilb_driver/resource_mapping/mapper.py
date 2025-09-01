# octavia_loxilb_driver/resource_mapping/mapper.py
"""Resource mapping between Octavia and LoxiLB formats."""

import json
import os
import re
from typing import Dict, List

from octavia_lib.common import constants as lib_consts
from oslo_config import cfg
from oslo_log import log as logging

from octavia_loxilb_driver.common import constants, exceptions, utils

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


def extract_member_attr(member, key, default=None):
    if isinstance(member, dict):
        return member.get(key, default)
    return getattr(member, key, default)


class ResourceMapper:
    """Maps Octavia data models to LoxiLB API models."""

    def __init__(self, config):
        self.config = config
        # Initialize ID mapping cache for handling LoxiLB's lack of unique IDs
        storage_path = None
        if getattr(self.config, 'id_mapping_persistence_enabled', True):
            storage_path = getattr(self.config, 'id_mapping_storage_path', '/var/lib/octavia/loxilb_id_mappings.json')
            LOG.info("ID mapping persistence enabled with storage path: %s", storage_path)
            
            # Ensure the directory exists
            storage_dir = os.path.dirname(storage_path)
            if not os.path.exists(storage_dir):
                try:
                    os.makedirs(storage_dir, exist_ok=True)
                    LOG.info("Created directory for ID mapping storage: %s", storage_dir)
                except Exception as e:
                    LOG.warning("Failed to create directory for ID mapping storage: %s. Error: %s", storage_dir, e)
                    storage_path = None
        else:
            LOG.warning("ID mapping persistence is disabled. Mappings will be lost on service restart.")
            
        self.id_mapping_cache = utils.create_id_mapping_cache(storage_path)
        
    def store_mapping(self, resource_type, octavia_id, loxilb_id, metadata=None):
        """Store mapping between Octavia and LoxiLB resources.
        
        Args:
            resource_type (str): Type of resource (loadbalancer, listener, pool, etc.)
            octavia_id (str): Octavia resource ID
            loxilb_id (str): LoxiLB resource ID or service key
            metadata (dict, optional): Additional metadata to store with the mapping
            
        Returns:
            None
        """
        LOG.info("ResourceMapper.store_mapping called for %s: octavia_id=%s, loxilb_id=%s",
                resource_type, octavia_id, loxilb_id)
        
        # Check if mapping already exists
        existing_mapping = utils.get_loxilb_key_from_octavia_id(self.id_mapping_cache, octavia_id)
        if existing_mapping:
            LOG.warning("Mapping already exists for %s %s: %s. Overwriting with %s", 
                      resource_type, octavia_id, existing_mapping, loxilb_id)
        
        # Store the mapping
        utils.store_id_mapping(
            self.id_mapping_cache,
            octavia_id,
            loxilb_id,
            resource_type,
            metadata
        )
        
        # Verify mapping was stored correctly
        stored_mapping = utils.get_loxilb_key_from_octavia_id(self.id_mapping_cache, octavia_id)
        LOG.info("Verified mapping for %s %s: stored as %s", 
                resource_type, octavia_id, stored_mapping)
        
        # Force save to disk if persistence is enabled
        storage_path = self.id_mapping_cache.get("_storage_path")
        if storage_path:
            success = utils.save_id_mappings_to_storage(self.id_mapping_cache)
            if success:
                LOG.info("Successfully saved ID mappings to %s", storage_path)
            else:
                LOG.error("Failed to save ID mappings to %s", storage_path)

    def _get_lb_algorithm(self, octavia_algorithm):
        """Maps Octavia LB algorithm to LoxiLB selection value.
        
        LoxiLB Algorithm Mapping:
        - 0: Round Robin (rr) - Default
        - 1: Hash-based (hash) - Used for SOURCE_IP_PORT
        - 2: Priority-based (priority) - LoxiLB extended
        - 3: Session persistence (persist) - Used for SOURCE_IP
        - 4: Least connections (lc)
        """
        mapping = {
            # Octavia standard algorithms
            lib_consts.LB_ALGORITHM_ROUND_ROBIN: 0,
            lib_consts.LB_ALGORITHM_LEAST_CONNECTIONS: 4,
            lib_consts.LB_ALGORITHM_SOURCE_IP: 3,
            lib_consts.LB_ALGORITHM_SOURCE_IP_PORT: 1,  # Added missing algorithm
            
            # LoxiLB extended algorithms (for advanced use cases)
            "PRIORITY": 2,
        }
        # Default to round-robin if algorithm is not specified or not supported
        return mapping.get(octavia_algorithm, 0)
        
    @staticmethod
    def get_vip_address(loadbalancer):
        """Extract VIP address from loadbalancer object or dict.
        
        Args:
            loadbalancer: Loadbalancer object or dict
            
        Returns:
            str: VIP address or None if not found
        """
        vip = None
        
        if isinstance(loadbalancer, dict):
            # Try to get VIP from vip.ip_address first
            vip_dict = loadbalancer.get("vip", {})
            if isinstance(vip_dict, dict):
                vip = vip_dict.get("ip_address")
            # If not found, try vip_address directly
            if not vip:
                vip = loadbalancer.get("vip_address")
        else:
            # Try to get VIP from vip.ip_address first
            vip_obj = getattr(loadbalancer, 'vip', None)
            if vip_obj:
                vip = getattr(vip_obj, 'ip_address', None)
            # If not found, try vip_address directly
            if not vip:
                vip = getattr(loadbalancer, 'vip_address', None)
                
        return vip

    def loadbalancer_to_loxilb(self, loadbalancer, listener, pool=None):
        """Maps an Octavia Load Balancer and Listener to a LoxiLB API object.

        This method creates a LoxiLB LoadbalanceEntry object from Octavia resources.
        According to the LoxiLB API specification, a load balancer is defined by:
        - serviceArguments: Contains VIP, port, protocol, and other service settings
        - endpoints: Array of backend servers with IP, port, and weight

        Args:
            loadbalancer (dict): Octavia load balancer object
            listener (dict): Octavia listener object
            pool (dict, optional): Octavia pool object (overrides listener.default_pool)

        Returns:
            dict: LoxiLB LoadbalanceEntry object compliant with the API spec

        Raises:
            LoxiLBMappingException: If required fields are missing or invalid
            LoxiLBValidationException: If configuration validation fails
        """
        try:
            # Input validation
            self._validate_loadbalancer_input(loadbalancer, listener)
            
            # Get the pool associated with this listener
            if pool is None:
                if isinstance(listener, dict):
                    pool = listener.get("default_pool")
                    listener_id = listener.get('id')
                else:
                    pool = getattr(listener, "default_pool", None)
                    listener_id = getattr(listener, 'id', None)
                    
                if not pool:
                    # Create a placeholder pool configuration for listeners without a default pool
                    # This allows the listener to be created without a real backend pool
                    LOG.warning(f"Listener {listener_id} has no default_pool. Creating a placeholder pool configuration.")
                    
                    # Create a minimal pool object that will satisfy the mapping requirements
                    # but won't actually route traffic (will be updated later when a real pool is added)
                    if isinstance(listener, dict):
                        protocol = listener.get('protocol', 'TCP')
                    else:
                        protocol = getattr(listener, 'protocol', 'TCP')
                        
                    pool = {
                        'id': f"placeholder-{listener_id}",
                        'protocol': protocol,
                        'lb_algorithm': 'ROUND_ROBIN',
                        'members': [],
                        'is_placeholder': True,  # Mark as placeholder for special handling
                        'session_persistence': None,
                        'healthmonitor': None
                    }

            # Extract basic information
            if isinstance(loadbalancer, dict):
                lb_id = loadbalancer.get("id") or loadbalancer.get("loadbalancer_id")
            else:
                lb_id = getattr(loadbalancer, "id", None) or getattr(loadbalancer, "loadbalancer_id", None)
                
            # Get VIP information using helper function
            external_ip = self.get_vip_address(loadbalancer)
                    
            if isinstance(listener, dict):
                listener_id = listener.get("id") or listener.get("listener_id")
            else:
                listener_id = getattr(listener, "id", None) or getattr(listener, "listener_id", None)
            
            if not external_ip:
                raise exceptions.LoxiLBMappingException(
                    f"Load balancer {lb_id} has no VIP address configured."
                )

            # Build the serviceArguments object according to LoxiLB API spec
            service_args = self._build_service_arguments(
                loadbalancer, listener, pool, external_ip
            )

            # Build the endpoints array
            endpoints = self._build_endpoints(pool)

            # Build optional arrays
            secondary_ips = self._build_secondary_ips(loadbalancer)
            allowed_sources = self._build_allowed_sources(listener, pool)

            # Create the complete LoadbalanceEntry object
            lb_entry = {
                "serviceArguments": service_args,
                "endpoints": endpoints
            }

            # Add optional arrays if they have content
            if secondary_ips:
                lb_entry["secondaryIPs"] = secondary_ips
            
            if allowed_sources:
                lb_entry["allowedSources"] = allowed_sources

            # Validate the final configuration
            self._validate_loxilb_loadbalancer_config(lb_entry)

            # Store ID mapping for tracking between Octavia and LoxiLB
            loxilb_service_key = utils.get_loxilb_service_key(
                external_ip, 
                service_args["port"], 
                service_args["protocol"]
            )
            
            utils.store_id_mapping(
                self.id_mapping_cache,
                lb_id,
                loxilb_service_key,
                "loadbalancer",
                {
                    "external_ip": external_ip,
                    "port": service_args["port"],
                    "protocol": service_args["protocol"],
                    "listener_id": listener_id,
                    "pool_id": pool.get("id") if pool else None
                }
            )

            if getattr(self.config, 'debug_resource_mapping', False):
                LOG.debug(
                    f"Mapped Octavia LB to LoxiLB: {utils.sanitize_dict_for_logging(lb_entry)}"
                )

            return lb_entry

        except exceptions.LoxiLBMappingException:
            raise
        except Exception as e:
            LOG.error(f"Failed to map Octavia load balancer to LoxiLB: {e}")
            raise exceptions.LoxiLBMappingException(
                f"Unexpected error during load balancer mapping: {str(e)}"
            )

    def _validate_loadbalancer_input(self, loadbalancer, listener):
        """Validate input parameters for load balancer mapping.
        
        Args:
            loadbalancer: Loadbalancer object or dict
            listener: Listener object or dict
        
        Raises:
            LoxiLBMappingException: If required fields are missing
        """
        if not loadbalancer:
            raise exceptions.LoxiLBMappingException(
                "Load balancer object is required."
            )
        
        if not listener:
            raise exceptions.LoxiLBMappingException(
                "Listener object is required."
            )
        
        # Check for required fields in loadbalancer
        # Load balancer can have 'id' or 'loadbalancer_id'
        lb_id = None
        if isinstance(loadbalancer, dict):
            lb_id = loadbalancer.get("id") or loadbalancer.get("loadbalancer_id")
        else:
            lb_id = getattr(loadbalancer, "id", None) or getattr(loadbalancer, "loadbalancer_id", None)
        
        if not lb_id:
            raise exceptions.LoxiLBMappingException(
                "Load balancer missing required field: id or loadbalancer_id"
            )
        
        # Check for required fields in listener
        required_listener_fields = ["protocol", "protocol_port"]
        for field in required_listener_fields:
            field_value = None
            if isinstance(listener, dict):
                field_value = listener.get(field)
            else:
                field_value = getattr(listener, field, None)
                
            if not field_value:
                raise exceptions.LoxiLBMappingException(
                    f"Listener missing required field: {field}"
                )

    def _build_service_arguments(self, loadbalancer, listener, pool, external_ip):
        """Build the serviceArguments section of the LoxiLB LoadbalanceEntry."""
        # Extract attributes from listener based on type
        if isinstance(listener, dict):
            protocol_port = listener.get("protocol_port")
            protocol = listener.get("protocol")
        else:
            protocol_port = getattr(listener, "protocol_port", None)
            protocol = getattr(listener, "protocol", None)
            
        # Extract attributes from pool based on type
        if isinstance(pool, dict):
            lb_algorithm = pool.get("lb_algorithm")
        else:
            lb_algorithm = getattr(pool, "lb_algorithm", None)
            
        # Start with required fields
        service_args = {
            "externalIP": external_ip,
            "port": protocol_port,
            "protocol": self._map_protocol(protocol),
            "sel": self._get_lb_algorithm(lb_algorithm),
            "monitor": False,  # Default to False, will be overridden if health monitor exists
            "name": self._generate_service_name(loadbalancer, listener),
        }

        # Add optional fields based on configuration
        self._add_protocol_specific_config(service_args, listener)
        self._add_session_persistence_config(service_args, pool)
        self._add_health_monitor_config(service_args, pool)
        self._add_security_config(service_args, listener)
        self._add_advanced_config(service_args, loadbalancer, listener, pool)

        return service_args

    def _map_protocol(self, octavia_protocol):
        """Map Octavia protocol to LoxiLB protocol."""
        if not octavia_protocol:
            return "tcp"  # Default
        
        protocol_upper = octavia_protocol.upper()
        
        # Protocol mapping based on LoxiLB requirements
        # FIXME: This mapping may need to be adjusted based on LoxiLB's actual protocol handling
        protocol_map = {
            "HTTP": "tcp",
            "HTTPS": "tcp", 
            "TERMINATED_HTTPS": "tcp",
            "TCP": "tcp",
            "UDP": "udp",
            "SCTP": "sctp",
            "PROXY": "tcp"  # PROXY protocol over TCP
        }
        
        return protocol_map.get(protocol_upper, "tcp").lower()

    def _generate_service_name(self, loadbalancer, listener):
        """Generate a service name for LoxiLB.
        
        Args:
            loadbalancer: Loadbalancer object or dict
            listener: Listener object or dict
            
        Returns:
            str: Generated service name for LoxiLB
        """
        # Extract loadbalancer attributes based on type
        if isinstance(loadbalancer, dict):
            lb_name = loadbalancer.get("name")
            lb_id = loadbalancer.get("id") or loadbalancer.get("loadbalancer_id")
        else:
            lb_name = getattr(loadbalancer, "name", None)
            lb_id = getattr(loadbalancer, "id", None) or getattr(loadbalancer, "loadbalancer_id", None)
        
        # Extract listener attributes based on type
        if isinstance(listener, dict):
            listener_id = listener.get("id") or listener.get("listener_id")
        else:
            listener_id = getattr(listener, "id", None) or getattr(listener, "listener_id", None)
        
        if lb_name:
            # Use provided name, but make it LoxiLB-compatible
            return utils.generate_resource_name("lb", lb_name)
        else:
            # Generate name from IDs
            return utils.generate_resource_name("lb", f"{lb_id}-{listener_id}"[:8])

    def _add_protocol_specific_config(self, service_args, listener):
        """Add protocol-specific configuration.
        
        Args:
            service_args: Service arguments dictionary to update
            listener: Listener object or dict
        """
        # Extract listener attributes based on type
        if isinstance(listener, dict):
            protocol = listener.get("protocol", "").upper()
            protocol_port_max = listener.get("protocol_port_max")
        else:
            protocol = getattr(listener, "protocol", "").upper() if getattr(listener, "protocol", None) else ""
            protocol_port_max = getattr(listener, "protocol_port_max", None)
        
        # Add port range if configured
        if protocol_port_max:
            service_args["portMax"] = protocol_port_max
        
        # Add proxy protocol configuration
        if protocol in ["PROXY", "PROXYV2"]:
            service_args["proxyprotocolv2"] = (protocol == "PROXYV2")

    def _add_session_persistence_config(self, service_args, pool):
        """Add session persistence configuration."""
        # Handle both dictionary and object types
        if isinstance(pool, dict):
            session_persistence = pool.get("session_persistence")
        else:
            session_persistence = getattr(pool, "session_persistence", None)
            
        if not session_persistence:
            return
        
        # Handle both dictionary and object types for session_persistence
        if isinstance(session_persistence, dict):
            persistence_type = session_persistence.get("type")
        else:
            persistence_type = getattr(session_persistence, "type", None)
            
        if persistence_type:
            if persistence_type == "SOURCE_IP":
                # For SOURCE_IP persistence, use the hash algorithm (1)
                # This is more appropriate than the persistence flag (3)
                service_args["sel"] = constants.LB_ALGORITHM_HASH
            elif persistence_type in ["HTTP_COOKIE", "APP_COOKIE"]:
                # LoxiLB doesn't support cookie-based persistence directly
                # Fall back to source IP persistence using hash algorithm
                service_args["sel"] = constants.LB_ALGORITHM_HASH
                LOG.warning(
                    f"Cookie-based session persistence ({persistence_type}) "
                    "not supported by LoxiLB, using source IP persistence instead"
                )

    def _add_health_monitor_config(self, service_args, pool):
        """Add health monitor configuration."""
        # Handle both dictionary and object types
        if isinstance(pool, dict):
            healthmonitor = pool.get("healthmonitor")
        else:
            healthmonitor = getattr(pool, "healthmonitor", None)
            
        if not healthmonitor:
            return
            
        # Handle both dictionary and object types for healthmonitor
        if isinstance(healthmonitor, dict):
            admin_state_up = healthmonitor.get("admin_state_up", True)
            monitor_type = healthmonitor.get("type", "").upper()
            probe_port = healthmonitor.get("port")
            timeout = healthmonitor.get("timeout")
            max_retries = healthmonitor.get("max_retries")
        else:
            admin_state_up = getattr(healthmonitor, "admin_state_up", True)
            monitor_type_raw = getattr(healthmonitor, "type", "")
            monitor_type = monitor_type_raw.upper() if monitor_type_raw else ""
            probe_port = getattr(healthmonitor, "port", None)
            timeout = getattr(healthmonitor, "timeout", None)
            max_retries = getattr(healthmonitor, "max_retries", None)
            
        if not admin_state_up:
            return
        
        service_args["monitor"] = True
        probe_type_map = {
            "HTTP": "http",
            "HTTPS": "https", 
            "TCP": "tcp",
            "UDP_CONNECT": "udp",
            "PING": "ping"
        }
        
        if monitor_type in probe_type_map:
            service_args["probetype"] = probe_type_map[monitor_type]
        
        # Add probe port if specified and different from service port
        if probe_port and probe_port != service_args["port"]:
            service_args["probeport"] = probe_port
        
        # Add timeouts and retries
        if timeout:
            service_args["probeTimeout"] = timeout
        
        if max_retries:
            service_args["probeRetries"] = max_retries
        
        # Add HTTP-specific probe configuration
        if monitor_type in ["HTTP", "HTTPS"]:
            self._add_http_probe_config(service_args, healthmonitor)
        
        # Add UDP-specific probe configuration
        elif monitor_type == "UDP_CONNECT":
            self._add_udp_probe_config(service_args, healthmonitor)

    def _add_http_probe_config(self, service_args, healthmonitor):
        """Add HTTP-specific health probe configuration.
        
        Args:
            service_args: Service arguments dictionary to update
            healthmonitor: Health monitor object or dict
        """
        # Extract attributes based on type
        if isinstance(healthmonitor, dict):
            url_path = healthmonitor.get("url_path", "/")
            http_method = healthmonitor.get("http_method", "GET")
            host_header = healthmonitor.get("domain_name", "localhost")
            http_headers = healthmonitor.get("http_headers")
            expected_codes = healthmonitor.get("expected_codes", "200")
        else:
            url_path = getattr(healthmonitor, "url_path", "/")
            http_method = getattr(healthmonitor, "http_method", "GET")
            host_header = getattr(healthmonitor, "domain_name", "localhost")
            http_headers = getattr(healthmonitor, "http_headers", None)
            expected_codes = getattr(healthmonitor, "expected_codes", "200")
        
        # Build HTTP request
        probe_req = f"{http_method} {url_path} HTTP/1.1\r\nHost: {host_header}\r\n"
        
        # Add custom headers if configured
        if http_headers:
            if isinstance(http_headers, dict):
                for header_name, header_value in http_headers.items():
                    probe_req += f"{header_name}: {header_value}\r\n"
        
        probe_req += "\r\n"
        service_args["probereq"] = probe_req
        
        # Build expected response - take the first code if multiple codes are specified
        service_args["probeexpect"] = expected_codes.split(",")[0].strip() if "," in expected_codes else expected_codes
        
        service_args["proberesp"] = f"HTTP/1.1 {expected_codes}"

    def _add_udp_probe_config(self, service_args, healthmonitor):
        """Add UDP-specific health probe configuration.
        
        Args:
            service_args: Service arguments dictionary to update
            healthmonitor: Health monitor object or dict
        """
        # Extract attributes based on type
        if isinstance(healthmonitor, dict):
            udp_request = healthmonitor.get("udp_request")
            udp_response = healthmonitor.get("udp_response")
        else:
            udp_request = getattr(healthmonitor, "udp_request", None)
            udp_response = getattr(healthmonitor, "udp_response", None)
        
        if udp_request:
            service_args["probereq"] = udp_request
        
        if udp_response:
            service_args["proberesp"] = udp_response

    def _add_security_config(self, service_args, listener):
        """Add security configuration.
        
        Args:
            service_args: Service arguments dictionary to update
            listener: Listener object or dict
        """
        # Extract attributes based on type
        if isinstance(listener, dict):
            protocol = listener.get("protocol", "").upper()
            tls_container = listener.get("default_tls_container_ref")
        else:
            protocol_raw = getattr(listener, "protocol", "")
            protocol = protocol_raw.upper() if protocol_raw else ""
            tls_container = getattr(listener, "default_tls_container_ref", None)
        
        if protocol in ["HTTPS", "TERMINATED_HTTPS"]:
            service_args["security"] = 1  # HTTPS mode
            
            # Add TLS container information if available
            if tls_container:
                # Store TLS container reference for later use
                service_args["_tls_container"] = tls_container
        
        elif protocol == "TLS":
            service_args["security"] = 1  # TLS mode

    def _add_advanced_config(self, service_args, loadbalancer, listener, pool):
        """Add advanced LoxiLB configuration options.
        
        Args:
            service_args: Service arguments dictionary to update
            loadbalancer: Loadbalancer object or dict
            listener: Listener object or dict
            pool: Pool object or dict
        """
        # Add NAT mode configuration
        nat_mode = self._determine_nat_mode(loadbalancer, listener)
        if nat_mode is not None:
            service_args["mode"] = nat_mode
        
        # Add BGP configuration if enabled
        if getattr(self.config, 'bgp_enabled', False):
            service_args["bgp"] = True
        
        # Add SNAT configuration
        if getattr(self.config, 'snat_enabled', False):
            service_args["snat"] = True
        
        # Extract pool attributes based on type
        if isinstance(pool, dict):
            timeout_client = pool.get("timeout_client_data")
            timeout_member = pool.get("timeout_member_data")
        else:
            timeout_client = getattr(pool, "timeout_client_data", None)
            timeout_member = getattr(pool, "timeout_member_data", None)
        
        # Add inactivity timeout
        timeout = timeout_client or timeout_member
        if timeout:
            service_args["inactiveTimeOut"] = timeout
        
        # Extract listener attributes based on type
        if isinstance(listener, dict):
            ingress_rules = listener.get("ingress_rules")
            default_host = listener.get("default_host", "")
        else:
            ingress_rules = getattr(listener, "ingress_rules", None)
            default_host = getattr(listener, "default_host", "")
        
        # Add ingress configuration
        if ingress_rules:
            service_args["host"] = default_host

    def _determine_nat_mode(self, loadbalancer, listener):
        """Determine NAT mode based on configuration."""
        # NAT mode mapping: 0-DNAT, 1-onearm, 2-fullnat, 3-dsr, 4-fullproxy, 5-hostonearm
        
        # Default to DNAT
        nat_mode = 1
        
        # Check for specific configurations that require different modes
        if hasattr(self.config, 'nat_mode') and self.config.nat_mode:
            mode_map = {
                "dnat": 0,
                "onearm": 1,
                "fullnat": 2,
                "dsr": 3,
                "fullproxy": 4,
                "hostonearm": 5
            }
            nat_mode = mode_map.get(self.config.nat_mode.lower(), 1)
        
        return nat_mode

    def _build_endpoints(self, pool):
        """Build the endpoints array from pool members."""
        endpoints = []
        if isinstance(pool, dict):
            members = pool.get("members", [])
        else:
            members = getattr(pool, "members", []) or []
        for member in members:
            # Print all keys/attrs and values
            if isinstance(member, dict):
                for k, v in member.items():
                    LOG.debug(f"Member dict key: {k}, value: {v}")
            else:
                for k, v in vars(member).items():
                    LOG.debug(f"Member object attr: {k}, value: {v}")
            admin_state_up = extract_member_attr(member, "admin_state_up", True)
            # Robust address extraction: check both 'ip_address' and 'address'
            address = extract_member_attr(member, "ip_address") or extract_member_attr(member, "address")
            protocol_port = extract_member_attr(member, "protocol_port")
            member_id = extract_member_attr(member, "id")
            weight = extract_member_attr(member, "weight", 1)
            operating_status = extract_member_attr(member, "operating_status")
            # Only include enabled and healthy members
            if not admin_state_up:
                LOG.debug(f"Skipping member {member_id}: admin_state_up={admin_state_up}")
                continue
            # Robustly check both 'ip_address' and 'address' for member address
            if not address:
                address = extract_member_attr(member, "address")
                LOG.debug(f"Member {member_id} fallback address: {address}")
            if not address or not protocol_port:
                LOG.warning(f"Skipping member {member_id} due to missing address or port")
                LOG.debug(f"Member {member_id} address: {address}, port: {protocol_port}")
                continue
            endpoint = {
                "endpointIP": address,
                "targetPort": protocol_port,
                "weight": weight,
            }
            if operating_status:
                state_map = {
                    "ONLINE": "active",
                    "OFFLINE": "inactive", 
                    "ERROR": "error",
                    "NO_MONITOR": "active",
                    "DEGRADED": "active"
                }
                endpoint["state"] = state_map.get(operating_status, "active")
            endpoints.append(endpoint)
        if not endpoints:
            LOG.warning("No valid endpoints found for load balancer")
        return endpoints

    def _build_secondary_ips(self, loadbalancer):
        """Build secondary IPs array if configured."""
        secondary_ips = []
        
        # Check for additional VIPs
        if isinstance(loadbalancer, dict):
            additional_vips = loadbalancer.get("additional_vips", [])
        else:
            additional_vips = getattr(loadbalancer, "additional_vips", [])
        
        for vip in additional_vips:
            if isinstance(vip, dict):
                ip_address = vip.get("ip_address")
            else:
                ip_address = getattr(vip, "ip_address", None)
                
            if ip_address:
                secondary_ips.append({
                    "secondaryIP": ip_address
                })
        
        return secondary_ips

    def _build_allowed_sources(self, listener, pool):
        """Build allowed sources array if configured."""
        allowed_sources = []
        
        # Check for allowed CIDRs in listener
        if isinstance(listener, dict):
            allowed_cidrs = listener.get("allowed_cidrs", [])
        else:
            allowed_cidrs = getattr(listener, "allowed_cidrs", [])
            
        for cidr in allowed_cidrs:
            if cidr:
                allowed_sources.append({
                    "prefix": cidr
                })
        
        # Check for L7 policies that might define allowed sources
        if isinstance(listener, dict):
            l7_policies = listener.get("l7_policies", [])
        else:
            l7_policies = getattr(listener, "l7_policies", [])
            
        for policy in l7_policies:
            if isinstance(policy, dict):
                l7_rules = policy.get("l7_rules", [])
            else:
                l7_rules = getattr(policy, "l7_rules", [])
                
            for rule in l7_rules:
                if isinstance(rule, dict):
                    rule_type = rule.get("type")
                    compare_type = rule.get("compare_type")
                else:
                    rule_type = getattr(rule, "type", None)
                    compare_type = getattr(rule, "compare_type", None)
                    
                if rule_type == "HOST_NAME" and compare_type == "EQUAL_TO":
                    # This could be used for host-based routing
                    pass
        
        return allowed_sources

    def _validate_loxilb_loadbalancer_config(self, lb_entry):
        """Validate the final LoxiLB load balancer configuration."""
        service_args = lb_entry.get("serviceArguments", {})
        
        # Validate required fields
        required_fields = ["externalIP", "port", "protocol"]
        for field in required_fields:
            if not service_args.get(field):
                raise exceptions.LoxiLBValidationException(
                    resource_type="mapper",
                    reason=f"Missing required serviceArguments field: {field}"
                )
        
        # Validate IP address
        try:
            import ipaddress
            ipaddress.ip_address(service_args["externalIP"])
        except ValueError:
            raise exceptions.LoxiLBValidationException(
                resource_type="mapper",
                reason=f"Invalid IP address: {service_args['externalIP']}"
            )
        
        # Validate port range
        port = service_args["port"]
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise exceptions.LoxiLBValidationException(
                f"Invalid port number: {port}"
            )
        
        # Validate protocol
        valid_protocols = ["tcp", "udp", "sctp", "http", "https", "ping"]
        if service_args["protocol"] not in valid_protocols:
            raise exceptions.LoxiLBValidationException(
                resource_type="mapper",
                reason=f"Invalid protocol: {service_args['protocol']}, must be one of {valid_protocols}"
            )
        
        # Validate algorithm selection
        if "sel" in service_args:
            if not isinstance(service_args["sel"], int) or service_args["sel"] < 0 or service_args["sel"] > 6:
                raise exceptions.LoxiLBValidationException(
                    resource_type="mapper",
                    reason=f"Invalid algorithm selection: {service_args['sel']}, must be 0-6"
                )
        
        # Validate endpoints
        endpoints = lb_entry.get("endpoints", [])
        if not endpoints:
            LOG.warning("Load balancer has no endpoints configured")
        
        for i, endpoint in enumerate(endpoints):
            # Validate endpoint IP
            try:
                import ipaddress
                ipaddress.ip_address(endpoint["endpointIP"])
            except ValueError:
                raise exceptions.LoxiLBValidationException(
                    resource_type="mapper",
                    reason=f"Invalid endpoint IP at index {i}: {endpoint['endpointIP']}"
                )
            
            # Validate endpoint port
            target_port = endpoint["targetPort"]
            if not isinstance(target_port, int) or target_port < 1 or target_port > 65535:
                raise exceptions.LoxiLBValidationException(
                    f"Invalid endpoint port at index {i}: {target_port}"
                )
            
            # Validate weight
            weight = endpoint.get("weight", 1)
            if not isinstance(weight, int) or weight < 0:
                raise exceptions.LoxiLBValidationException(
                    resource_type="mapper",
                    reason=f"Invalid endpoint weight at index {i}: {weight}"
                )

    def loxilb_to_octavia_loadbalancer(self, loxilb_lb: Dict) -> Dict:
        """Convert LoxiLB load balancer to Octavia format.

        This method translates a LoxiLB LoadbalanceEntry response into an Octavia
        load balancer object. According to the LoxiLB API specification, a load balancer
        response contains serviceArguments and endpoints which need to be mapped to
        Octavia's model.

        Args:
            loxilb_lb (dict): LoxiLB load balancer response from API

        Returns:
            dict: Octavia-formatted load balancer dictionary

        Raises:
            LoxiLBMappingException: If mapping fails due to invalid data
            LoxiLBOperationException: If operation fails
        """
        try:
            # Input validation
            self._validate_loxilb_loadbalancer_input(loxilb_lb)
            
            # Extract service arguments
            service_args = loxilb_lb.get("serviceArguments", {})
            endpoints = loxilb_lb.get("endpoints", [])
            
            # Extract basic information with enhanced validation
            lb_id = self._extract_lb_id(loxilb_lb, service_args)
            external_ip = service_args.get("externalIP")
            port = service_args.get("port")
            protocol = self._map_loxilb_protocol_to_octavia(service_args.get("protocol", "tcp"))
            # Use the full UUID without any prefix for service names
            # This ensures consistency with OpenStack server naming conventions
            name = service_args.get("name", "") or f"{lb_id}"

            # Build VIP information
            vip_info = self._build_vip_info(external_ip, service_args, loxilb_lb)
            
            # Determine status information
            status_info = self._determine_loadbalancer_status(service_args, endpoints)

            # Build the main Octavia load balancer object
            octavia_config = {
                "id": lb_id,
                "name": name,
                "description": self._generate_lb_description(service_args, protocol),
                "vip_address": external_ip,
                "vip": vip_info,
                "admin_state_up": True,  # LoxiLB doesn't have admin state, assume enabled
                "operating_status": status_info["operating_status"],
                "provisioning_status": status_info["provisioning_status"],
                "provider": constants.PROVIDER_NAME,
                "created_at": loxilb_lb.get("created_at"),
                "updated_at": loxilb_lb.get("updated_at"),
                "project_id": loxilb_lb.get("project_id", "default"),
                "tags": loxilb_lb.get("tags", []),
            }

            # Build listener information
            listener = self._build_listener_from_loxilb(service_args, port, protocol)
            
            # Build pool information
            pool = self._build_pool_from_loxilb(service_args, endpoints, protocol)
            
            # Add health monitor if configured
            if service_args.get("monitor", False):
                health_monitor = self._build_health_monitor_from_loxilb(service_args)
                if health_monitor:
                    pool["healthmonitor"] = health_monitor

            # Add members from endpoints
            pool["members"] = self._build_members_from_endpoints(endpoints)

            # Link components together
            listener["default_pool_id"] = pool["id"]
            listener["default_pool"] = pool
            octavia_config["listeners"] = [listener]

            # Add secondary IPs if available
            secondary_ips = self._extract_secondary_ips(loxilb_lb)
            if secondary_ips:
                octavia_config["additional_vips"] = secondary_ips

            # Add allowed CIDRs if available
            allowed_sources = self._extract_allowed_sources(loxilb_lb)
            if allowed_sources:
                listener["allowed_cidrs"] = allowed_sources

            # Add statistics if available
            stats = self._extract_and_combine_statistics(loxilb_lb, endpoints)
            if stats:
                octavia_config["stats"] = stats

            # Add flavor and availability zone info if available
            self._add_flavor_and_az_info(octavia_config, loxilb_lb)

            # Final validation and cleanup
            octavia_config = self._validate_and_cleanup_octavia_config(octavia_config)

            if getattr(self.config, 'debug_resource_mapping', False):
                LOG.debug(
                    f"Mapped LoxiLB LB to Octavia: {utils.sanitize_dict_for_logging(octavia_config)}"
                )

            return octavia_config

        except exceptions.LoxiLBMappingException:
            raise
        except Exception as e:
            LOG.error(f"Failed to map LoxiLB load balancer to Octavia: {e}")
            raise exceptions.LoxiLBOperationException(
                operation="map_loadbalancer",
                resource_type="loadbalancer",
                resource_id=loxilb_lb.get("id", "unknown"),
                reason=str(e),
            )

    def _validate_loxilb_loadbalancer_input(self, loxilb_lb):
        """Validate input from LoxiLB load balancer response."""
        if not loxilb_lb or not isinstance(loxilb_lb, dict):
            raise exceptions.LoxiLBMappingException(
                "LoxiLB load balancer object is required and must be a dictionary."
            )
        
        service_args = loxilb_lb.get("serviceArguments", {})
        if not service_args:
            raise exceptions.LoxiLBMappingException(
                "LoxiLB response missing serviceArguments"
            )
        
        # Validate required service arguments
        required_fields = ["externalIP", "port"]
        for field in required_fields:
            if not service_args.get(field):
                raise exceptions.LoxiLBMappingException(
                    f"LoxiLB serviceArguments missing required field: {field}"
                )

    def _extract_lb_id(self, loxilb_lb, service_args):
        """Extract or generate load balancer ID using deterministic ID generation."""
        # Try to get ID from various sources first
        lb_id = (
            loxilb_lb.get("id") or 
            service_args.get("id") or 
            service_args.get("name")
        )
        
        if not lb_id:
            # Check if we have an existing mapping based on service key
            external_ip = service_args.get("externalIP")
            port = service_args.get("port")
            protocol = service_args.get("protocol", "tcp")
            
            if external_ip and port:
                loxilb_service_key = utils.get_loxilb_service_key(external_ip, port, protocol)
                existing_lb_id = utils.get_octavia_id_from_loxilb_key(
                    self.id_mapping_cache, loxilb_service_key
                )
                
                if existing_lb_id:
                    lb_id = existing_lb_id
                else:
                    # Generate deterministic ID from service properties
                    lb_id = utils.generate_deterministic_id(
                        "loadbalancer",
                        external_ip=external_ip,
                        port=port,
                        protocol=protocol
                    )
                    
                    # Store the new mapping
                    utils.store_id_mapping(
                        self.id_mapping_cache,
                        lb_id,
                        loxilb_service_key,
                        "loadbalancer",
                        {
                            "external_ip": external_ip,
                            "port": port,
                            "protocol": protocol
                        }
                    )
            else:
                # Fallback to simple UUID if not enough info
                lb_id = utils.generate_uuid()
        
        return lb_id

    def _map_loxilb_protocol_to_octavia(self, loxilb_protocol):
        """Map LoxiLB protocol to Octavia protocol using utility function."""
        return utils.map_loxilb_protocol_to_octavia(loxilb_protocol or "tcp")

    def _build_vip_info(self, external_ip, service_args, loxilb_lb):
        """Build VIP information for Octavia load balancer."""
        vip_info = {
            "ip_address": external_ip,
            "port_id": loxilb_lb.get("vip_port_id"),
            "subnet_id": loxilb_lb.get("vip_subnet_id"),
            "network_id": loxilb_lb.get("vip_network_id"),
        }
        
        # Determine IP version
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(external_ip)
            vip_info["ip_version"] = ip_obj.version
        except ValueError:
            vip_info["ip_version"] = 4  # Default to IPv4
        
        return vip_info

    def _determine_loadbalancer_status(self, service_args, endpoints):
        """Determine load balancer operating and provisioning status."""
        # Count healthy endpoints
        healthy_endpoints = 0
        total_endpoints = len(endpoints)
        
        for endpoint in endpoints:
            state = endpoint.get("state", "").lower()
            if state in ["active", "online"]:
                healthy_endpoints += 1
        
        # Determine operating status
        if total_endpoints == 0:
            operating_status = "NO_MONITOR"
        elif healthy_endpoints == 0:
            operating_status = "OFFLINE"
        elif healthy_endpoints == total_endpoints:
            operating_status = "ONLINE"
        else:
            operating_status = "DEGRADED"
        
        # LoxiLB doesn't have provisioning states, assume ACTIVE
        provisioning_status = "ACTIVE"
        
        return {
            "operating_status": operating_status,
            "provisioning_status": provisioning_status
        }

    def _generate_lb_description(self, service_args, protocol):
        """Generate description for Octavia load balancer."""
        external_ip = service_args.get("externalIP", "unknown")
        port = service_args.get("port", "unknown")
        name = service_args.get("name", "")
        
        if name:
            return f"LoxiLB load balancer '{name}' ({external_ip}:{port}/{protocol.lower()})"
        else:
            return f"LoxiLB load balancer {external_ip}:{port}/{protocol.lower()}"

    def _build_listener_from_loxilb(self, service_args, port, protocol):
        """Build Octavia listener from LoxiLB service arguments."""
        listener = {
            "id": utils.generate_uuid(),
            "name": f"listener-{service_args.get('name', 'auto')}",
            "protocol": protocol,
            "protocol_port": port,
            "admin_state_up": True,
            "connection_limit": -1,  # No limit by default
        }
        
        # Add port range if configured
        if service_args.get("portMax") and service_args.get("portMax") != port:
            listener["protocol_port_max"] = service_args.get("portMax")
        
        # Add SSL/TLS configuration
        security_mode = service_args.get("security", 0)
        if security_mode == 1:  # HTTPS/TLS
            listener["protocol"] = "HTTPS"
            if service_args.get("_tls_container"):
                listener["default_tls_container_ref"] = service_args.get("_tls_container")
        elif security_mode == 2:  # End-to-end HTTPS
            listener["protocol"] = "TERMINATED_HTTPS"
        
        # Add proxy protocol configuration
        if service_args.get("proxyprotocolv2"):
            listener["insert_headers"] = {
                "X-Forwarded-Proto": "https" if security_mode > 0 else "http",
                "X-Forwarded-Port": str(port)
            }
        
        # Add ingress host configuration
        if service_args.get("host"):
            listener["default_host"] = service_args.get("host")
        
        return listener

    def _build_pool_from_loxilb(self, service_args, endpoints, protocol):
        """Build Octavia pool from LoxiLB service arguments."""
        # Map LoxiLB algorithm to Octavia
        sel_value = service_args.get("sel", 0)
        lb_algorithm = self._map_loxilb_sel_to_octavia_algorithm(sel_value)
        
        pool = {
            "id": utils.generate_uuid(),
            "name": f"pool-{service_args.get('name', 'auto')}",
            "protocol": protocol,
            "lb_algorithm": lb_algorithm,
            "admin_state_up": True,
        }
        
        # Add session persistence if configured
        if sel_value == constants.LB_ALGORITHM_PERSISTENCE:
            pool["session_persistence"] = {
                "type": "SOURCE_IP",
                "cookie_name": None
            }
        
        # Add timeout configurations if available
        if service_args.get("inactiveTimeOut"):
            pool["timeout_client_data"] = service_args.get("inactiveTimeOut")
            pool["timeout_member_data"] = service_args.get("inactiveTimeOut")
        
        return pool

    def _map_loxilb_sel_to_octavia_algorithm(self, sel_value):
        """Map LoxiLB selection algorithm to Octavia algorithm using utility function."""
        return utils.map_loxilb_algorithm_to_octavia(sel_value)

    def _build_health_monitor_from_loxilb(self, service_args):
        """Build Octavia health monitor from LoxiLB service arguments."""
        if not service_args.get("monitor", False):
            return None
        
        # Determine monitor type
        probe_type = service_args.get("probetype", "tcp").lower()
        monitor_type_map = {
            "http": "HTTP",
            "https": "HTTPS",
            "tcp": "TCP",
            "udp": "UDP_CONNECT",
            "ping": "PING"
        }
        
        monitor_type = monitor_type_map.get(probe_type, "TCP")
        
        health_monitor = {
            "id": utils.generate_uuid(),
            "name": f"healthmonitor-{service_args.get('name', 'auto')}",
            "type": monitor_type,
            "delay": service_args.get("probeTimeout", 5),
            "timeout": service_args.get("probeTimeout", 5),
            "max_retries": service_args.get("probeRetries", 3),
            "admin_state_up": True,
        }
        
        # Add probe port if specified and different from service port
        probe_port = service_args.get("probeport")
        if probe_port and probe_port != service_args.get("port"):
            health_monitor["port"] = probe_port
        
        # Add HTTP-specific configuration
        if monitor_type in ["HTTP", "HTTPS"]:
            self._add_http_health_monitor_config(health_monitor, service_args)
        
        # Add UDP-specific configuration
        elif monitor_type == "UDP_CONNECT":
            self._add_udp_health_monitor_config(health_monitor, service_args)
        
        return health_monitor

    def _add_http_health_monitor_config(self, health_monitor, service_args):
        """Add HTTP-specific health monitor configuration."""
        # Parse HTTP request if available
        probe_req = service_args.get("probereq", "")
        if probe_req:
            # Extract method and path
            method_match = re.search(r"^(\w+)\s+([^\s]+)", probe_req)
            if method_match:
                health_monitor["http_method"] = method_match.group(1)
                health_monitor["url_path"] = method_match.group(2)
            else:
                health_monitor["http_method"] = "GET"
                health_monitor["url_path"] = "/"
            
            # Extract host header
            host_match = re.search(r"Host:\s*([^\r\n]+)", probe_req, re.IGNORECASE)
            if host_match:
                health_monitor["domain_name"] = host_match.group(1).strip()
        else:
            health_monitor["http_method"] = "GET"
            health_monitor["url_path"] = "/"
        
        # Parse expected response
        probe_resp = service_args.get("proberesp", "")
        if probe_resp:
            # Extract status code
            code_match = re.search(r"HTTP/\d\.\d\s+(\d+)", probe_resp)
            if code_match:
                health_monitor["expected_codes"] = code_match.group(1)
            else:
                health_monitor["expected_codes"] = "200"
        else:
            health_monitor["expected_codes"] = "200"

    def _add_udp_health_monitor_config(self, health_monitor, service_args):
        """Add UDP-specific health monitor configuration."""
        health_monitor["udp_request"] = service_args.get("probereq", "")
        health_monitor["udp_response"] = service_args.get("proberesp", "")

    def _build_members_from_endpoints(self, endpoints):
        """Build Octavia members from LoxiLB endpoints."""
        members = []
        
        for endpoint in endpoints:
            # Skip endpoints without required fields
            if not endpoint.get("endpointIP") or not endpoint.get("targetPort"):
                LOG.warning(f"Skipping endpoint due to missing IP or port: {endpoint}")
                continue
            
            member = {
                "id": utils.generate_uuid(),
                "name": f"member-{endpoint.get('endpointIP')}-{endpoint.get('targetPort')}",
                "address": endpoint.get("endpointIP"),
                "protocol_port": endpoint.get("targetPort"),
                "weight": endpoint.get("weight", 1),
                "admin_state_up": True,
                "backup": False, # LoxiLB doesn't have backup concept
            }
            
            # Map endpoint state to Octavia operating status
            state = endpoint.get("state", "").lower()
            state_map = {
                "active": "ONLINE",
                "inactive": "OFFLINE",
                "error": "ERROR",
                "": "ONLINE"  # Default if not specified
            }
            member["operating_status"] = state_map.get(state, "ONLINE")
            
            # Add statistics if available
            if endpoint.get("counter"):
                try:
                    counter_data = json.loads(endpoint["counter"])
                    member["stats"] = {
                        "bytes_in": counter_data.get("bytes_in", 0),
                        "bytes_out": counter_data.get("bytes_out", 0),
                        "total_connections": counter_data.get("total_connections", 0),
                        "active_connections": counter_data.get("active_connections", 0),
                        "request_errors": counter_data.get("request_errors", 0)
                    }
                except (json.JSONDecodeError, ValueError) as e:
                    LOG.warning(f"Failed to parse endpoint counter: {e}")
            
            members.append(member)
        
        return members

    def _extract_secondary_ips(self, loxilb_lb):
        """Extract secondary IPs from LoxiLB load balancer."""
        secondary_ips = []
        
        # Extract from secondaryIPs array if available
        loxilb_secondary_ips = loxilb_lb.get("secondaryIPs", [])
        for secondary_ip in loxilb_secondary_ips:
            if secondary_ip.get("secondaryIP"):
                secondary_ips.append({
                    "ip_address": secondary_ip["secondaryIP"]
                })
        
        return secondary_ips

    def _extract_allowed_sources(self, loxilb_lb):
        """Extract allowed source CIDRs from LoxiLB load balancer."""
        allowed_cidrs = []
        
        # Extract from allowedSources array if available
        allowed_sources = loxilb_lb.get("allowedSources", [])
        for source in allowed_sources:
            if source.get("prefix"):
                allowed_cidrs.append(source["prefix"])
        
        return allowed_cidrs

    def _extract_and_combine_statistics(self, loxilb_lb, endpoints):
        """Extract and combine statistics from LoxiLB load balancer and endpoints."""
        stats = {}
        
        # Process service-level stats if available
        if loxilb_lb.get("stats"):
            for key, value in loxilb_lb["stats"].items():
                try:
                    stats[key] = int(value)
                except (ValueError, TypeError):
                    LOG.warning(f"Invalid stat value for {key}: {value}")
        
        # Process endpoint counters and aggregate
        endpoint_stats = {
            "bytes_in": 0,
            "bytes_out": 0,
            "total_connections": 0,
            "active_connections": 0,
            "request_errors": 0,
            "connection_errors": 0
        }
        
        for endpoint in endpoints:
            if endpoint.get("counter"):
                try:
                    counter_data = json.loads(endpoint["counter"])
                    for key, value in counter_data.items():
                        if key in endpoint_stats:
                            endpoint_stats[key] += int(value)
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    LOG.warning(f"Failed to parse endpoint counter: {e}")
        
        # Combine service and endpoint stats
        combined_stats = {**stats, **endpoint_stats}
        
        # Return mapped stats if any data is available
        if any(combined_stats.values()):
            return self._map_stats_to_octavia(combined_stats)
        
        return None

    def _add_flavor_and_az_info(self, octavia_config, loxilb_lb):
        """Add flavor and availability zone information if available."""
        if loxilb_lb.get("flavor_id"):
            octavia_config["flavor_id"] = loxilb_lb["flavor_id"]
        
        if loxilb_lb.get("availability_zone"):
            octavia_config["availability_zone"] = loxilb_lb["availability_zone"]

    def _validate_and_cleanup_octavia_config(self, octavia_config):
        """Validate and cleanup the final Octavia configuration."""
        # Remove None values
        octavia_config = utils.filter_none_values(octavia_config)
        
        # Validate required fields
        required_fields = ["id", "vip_address", "operating_status", "provisioning_status"]
        for field in required_fields:
            if not octavia_config.get(field):
                LOG.warning(f"Missing required field in Octavia config: {field}")
        
        # Ensure listeners array exists
        if "listeners" not in octavia_config:
            octavia_config["listeners"] = []
        
        # Validate listener configuration
        for listener in octavia_config["listeners"]:
            if not listener.get("id"):
                listener["id"] = utils.generate_uuid()
            
            # Ensure pool exists and is properly linked
            if "default_pool" in listener and listener["default_pool"]:
                pool = listener["default_pool"]
                if not pool.get("id"):
                    pool["id"] = utils.generate_uuid()
                
                listener["default_pool_id"] = pool["id"]
        
        return octavia_config

    def octavia_to_loxilb_listener(self, octavia_listener: Dict) -> Dict:
        """Convert Octavia listener to LoxiLB format."""
        try:
            # Validate input
            errors = utils.validate_listener_config(octavia_listener)
            if errors:
                raise exceptions.LoxiLBValidationException(
                    resource_type="listener", validation_errors=errors
                )

            # Create base LoxiLB configuration
            loxilb_config = utils.create_loxilb_listener_config(
                octavia_listener, self.config
            )

            # Add LoxiLB specific listener configuration
            protocol = octavia_listener["protocol"]

            # Handle SSL/TLS configuration
            if protocol in ["HTTPS", "TERMINATED_HTTPS"]:
                loxilb_config.update(
                    {
                        "ssl_enabled": True,
                        "ssl_certificate_id": octavia_listener.get(
                            "default_tls_container_ref"
                        ),
                        "ssl_protocols": self.config.get(
                            "ssl_protocols", ["TLSv1.2", "TLSv1.3"]
                        ),
                        "ssl_ciphers": self.config.get(
                            "ssl_ciphers", constants.DEFAULT_SSL_CIPHERS
                        ),
                    }
                )

                # Handle SNI
                if octavia_listener.get("sni_container_refs"):
                    loxilb_config["sni_certificates"] = [
                        {"certificate_id": ref}
                        for ref in octavia_listener["sni_container_refs"]
                    ]

            # Handle HTTP redirect configuration
            if octavia_listener.get("redirect_pool_id"):
                loxilb_config["redirect_pool_id"] = octavia_listener["redirect_pool_id"]

            # Handle insert headers
            if octavia_listener.get("insert_headers"):
                loxilb_config["insert_headers"] = octavia_listener["insert_headers"]

            if self.config.debug_resource_mapping:
                LOG.debug(
                    f"Mapped Octavia listener to LoxiLB: {utils.sanitize_dict_for_logging(loxilb_config)}"
                )

            return loxilb_config

        except Exception as e:
            LOG.error(f"Failed to map Octavia listener to LoxiLB: {e}")
            raise exceptions.LoxiLBOperationException(
                operation="map_listener",
                resource_type="listener",
                resource_id=octavia_listener.get("id", "unknown"),
                reason=str(e),
            )

    def loxilb_to_octavia_listener(self, loxilb_listener: Dict) -> Dict:
        """Convert LoxiLB listener to Octavia format."""
        try:
            octavia_config = {
                "id": loxilb_listener["id"],
                "name": loxilb_listener.get("name", ""),
                "description": loxilb_listener.get("description", ""),
                "loadbalancer_id": loxilb_listener["loadbalancer_id"],
                "protocol": utils.map_loxilb_protocol_to_octavia(
                    loxilb_listener["protocol"]
                ),
                "protocol_port": loxilb_listener["protocol_port"],
                "connection_limit": loxilb_listener.get("connection_limit", -1),
                "admin_state_up": loxilb_listener.get("admin_state_up", True),
                "operating_status": utils.map_loxilb_status_to_octavia(
                    loxilb_listener.get("operating_status", "OFFLINE"), "operating"
                ),
                "provisioning_status": utils.map_loxilb_status_to_octavia(
                    loxilb_listener.get("provisioning_status", "ACTIVE"), "provisioning"
                ),
                "created_at": loxilb_listener.get("created_at"),
                "updated_at": loxilb_listener.get("updated_at"),
                "project_id": loxilb_listener.get("project_id"),
            }

            # Handle SSL configuration
            if loxilb_listener.get("ssl_enabled"):
                octavia_config["default_tls_container_ref"] = loxilb_listener.get(
                    "ssl_certificate_id"
                )

                if loxilb_listener.get("sni_certificates"):
                    octavia_config["sni_container_refs"] = [
                        cert["certificate_id"]
                        for cert in loxilb_listener["sni_certificates"]
                    ]

            # Handle insert headers
            if loxilb_listener.get("insert_headers"):
                octavia_config["insert_headers"] = loxilb_listener["insert_headers"]

            if self.config.debug_resource_mapping:
                LOG.debug(
                    f"Mapped LoxiLB listener to Octavia: {utils.sanitize_dict_for_logging(octavia_config)}"
                )

            return utils.filter_none_values(octavia_config)

        except Exception as e:
            LOG.error(f"Failed to map LoxiLB listener to Octavia: {e}")
            raise exceptions.LoxiLBOperationException(
                operation="map_listener",
                resource_type="listener",
                resource_id=loxilb_listener.get("id", "unknown"),
                reason=str(e),
            )

    def octavia_to_loxilb_pool(self, octavia_pool: Dict) -> Dict:
        """Convert Octavia pool to LoxiLB format."""
        try:
            # Validate input
            errors = utils.validate_pool_config(octavia_pool)
            if errors:
                raise exceptions.LoxiLBValidationException(
                    resource_type="pool", validation_errors=errors
                )

            # Create base LoxiLB configuration
            loxilb_config = utils.create_loxilb_pool_config(octavia_pool, self.config)

            # Add LoxiLB specific pool configuration
            algorithm = octavia_pool["lb_algorithm"]

            # Handle weighted algorithms
            if algorithm in ["WEIGHTED_ROUND_ROBIN", "WEIGHTED_LEAST_CONNECTIONS"]:
                loxilb_config["enable_weight"] = True

            # Handle session persistence configuration
            session_persistence = octavia_pool.get("session_persistence")
            if session_persistence and session_persistence.get("type"):
                persistence_config = {
                    "type": utils.map_octavia_session_persistence_to_loxilb(
                        session_persistence["type"]
                    )
                }

                # Add cookie configuration for cookie-based persistence
                if session_persistence["type"] in ["HTTP_COOKIE", "APP_COOKIE"]:
                    if session_persistence.get("cookie_name"):
                        persistence_config["cookie_name"] = session_persistence[
                            "cookie_name"
                        ]
                    if session_persistence.get("persistence_timeout"):
                        persistence_config["timeout"] = session_persistence[
                            "persistence_timeout"
                        ]
                    if session_persistence.get("persistence_granularity"):
                        persistence_config["granularity"] = session_persistence[
                            "persistence_granularity"
                        ]

                loxilb_config["session_persistence"] = persistence_config

            # Handle TLS pool configuration
            if octavia_pool.get("tls_enabled"):
                loxilb_config.update(
                    {
                        "tls_enabled": True,
                        "tls_container_ref": octavia_pool.get("tls_container_ref"),
                        "ca_tls_container_ref": octavia_pool.get(
                            "ca_tls_container_ref"
                        ),
                        "crl_container_ref": octavia_pool.get("crl_container_ref"),
                        "tls_ciphers": octavia_pool.get("tls_ciphers"),
                        "tls_versions": octavia_pool.get("tls_versions"),
                    }
                )

            if self.config.debug_resource_mapping:
                LOG.debug(
                    f"Mapped Octavia pool to LoxiLB: {utils.sanitize_dict_for_logging(loxilb_config)}"
                )

            return loxilb_config

        except Exception as e:
            LOG.error(f"Failed to map Octavia pool to LoxiLB: {e}")
            raise exceptions.LoxiLBOperationException(
                operation="map_pool",
                resource_type="pool",
                resource_id=octavia_pool.get("id", "unknown"),
                reason=str(e),
            )

    def loxilb_to_octavia_pool(self, loxilb_pool: Dict) -> Dict:
        """Convert LoxiLB pool to Octavia format."""
        try:
            octavia_config = {
                "id": loxilb_pool["id"],
                "name": loxilb_pool.get("name", ""),
                "description": loxilb_pool.get("description", ""),
                "loadbalancer_id": loxilb_pool.get("loadbalancer_id"),
                "listener_id": loxilb_pool.get("listener_id"),
                "protocol": utils.map_loxilb_protocol_to_octavia(
                    loxilb_pool["protocol"]
                ),
                "lb_algorithm": utils.map_loxilb_algorithm_to_octavia(
                    loxilb_pool["lb_algorithm"]
                ),
                "admin_state_up": loxilb_pool.get("admin_state_up", True),
                "operating_status": utils.map_loxilb_status_to_octavia(
                    loxilb_pool.get("operating_status", "OFFLINE"), "operating"
                ),
                "provisioning_status": utils.map_loxilb_status_to_octavia(
                    loxilb_pool.get("provisioning_status", "ACTIVE"), "provisioning"
                ),
                "created_at": loxilb_pool.get("created_at"),
                "updated_at": loxilb_pool.get("updated_at"),
                "project_id": loxilb_pool.get("project_id"),
            }

            # Handle session persistence
            if loxilb_pool.get("session_persistence"):
                persistence = loxilb_pool["session_persistence"]
                octavia_persistence = {
                    "type": utils.map_loxilb_session_persistence_to_octavia(
                        persistence["type"]
                    )
                }

                if persistence.get("cookie_name"):
                    octavia_persistence["cookie_name"] = persistence["cookie_name"]
                if persistence.get("timeout"):
                    octavia_persistence["persistence_timeout"] = persistence["timeout"]
                if persistence.get("granularity"):
                    octavia_persistence["persistence_granularity"] = persistence[
                        "granularity"
                    ]

                octavia_config["session_persistence"] = octavia_persistence

            # Handle TLS configuration
            if loxilb_pool.get("tls_enabled"):
                octavia_config.update(
                    {
                        "tls_enabled": True,
                        "tls_container_ref": loxilb_pool.get("tls_container_ref"),
                        "ca_tls_container_ref": loxilb_pool.get("ca_tls_container_ref"),
                        "crl_container_ref": loxilb_pool.get("crl_container_ref"),
                        "tls_ciphers": loxilb_pool.get("tls_ciphers"),
                        "tls_versions": loxilb_pool.get("tls_versions"),
                    }
                )

            if self.config.debug_resource_mapping:
                LOG.debug(
                    f"Mapped LoxiLB pool to Octavia: {utils.sanitize_dict_for_logging(octavia_config)}"
                )

            return utils.filter_none_values(octavia_config)

        except Exception as e:
            LOG.error(f"Failed to map LoxiLB pool to Octavia: {e}")
            raise exceptions.LoxiLBOperationException(
                operation="map_pool",
                resource_type="pool",
                resource_id=loxilb_pool.get("id", "unknown"),
                reason=str(e),
            )

    def octavia_to_loxilb_member(self, octavia_member: Dict) -> Dict:
        """Convert Octavia member to LoxiLB format."""
        try:
            # Validate input
            errors = utils.validate_member_config(octavia_member)
            if errors:
                raise exceptions.LoxiLBValidationException(
                    resource_type="member", validation_errors=errors
                )

            # Create base LoxiLB configuration
            loxilb_config = utils.create_loxilb_member_config(
                octavia_member, self.config
            )

            # Add LoxiLB specific member configuration
            loxilb_config.update(
                {
                    "health_check_enabled": True,
                    "connection_limit": octavia_member.get("connection_limit", 0),
                    "backup": octavia_member.get("backup", False),
                    "monitor_address": octavia_member.get("monitor_address"),
                    "monitor_port": octavia_member.get("monitor_port"),
                }
            )

            # Handle member network information
            if octavia_member.get("subnet_id"):
                loxilb_config["network_info"] = {
                    "subnet_id": octavia_member["subnet_id"],
                    "ip_version": 6 if ":" in octavia_member["address"] else 4,
                }

            if self.config.debug_resource_mapping:
                LOG.debug(
                    f"Mapped Octavia member to LoxiLB: {utils.sanitize_dict_for_logging(loxilb_config)}"
                )

            return loxilb_config

        except Exception as e:
            LOG.error(f"Failed to map Octavia member to LoxiLB: {e}")
            raise exceptions.LoxiLBOperationException(
                operation="map_member",
                resource_type="member",
                resource_id=octavia_member.get("id", "unknown"),
                reason=str(e),
            )

    def loxilb_to_octavia_member(self, loxilb_member: Dict) -> Dict:
        """Convert LoxiLB member to Octavia format."""
        try:
            octavia_config = {
                "id": loxilb_member["id"],
                "name": loxilb_member.get("name", ""),
                "pool_id": loxilb_member["pool_id"],
                "address": loxilb_member["address"],
                "protocol_port": loxilb_member["protocol_port"],
                "weight": loxilb_member.get("weight", 1),
                "admin_state_up": loxilb_member.get("admin_state_up", True),
                "subnet_id": loxilb_member.get("subnet_id"),
                "operating_status": utils.map_loxilb_status_to_octavia(
                    loxilb_member.get("operating_status", "OFFLINE"), "operating"
                ),
                "provisioning_status": utils.map_loxilb_status_to_octavia(
                    loxilb_member.get("provisioning_status", "ACTIVE"), "provisioning"
                ),
                "created_at": loxilb_member.get("created_at"),
                "updated_at": loxilb_member.get("updated_at"),
                "project_id": loxilb_member.get("project_id"),
                "backup": loxilb_member.get("backup", False),
            }

            # Handle monitor configuration
            if loxilb_member.get("monitor_address"):
                octavia_config["monitor_address"] = loxilb_member["monitor_address"]
            if loxilb_member.get("monitor_port"):
                octavia_config["monitor_port"] = loxilb_member["monitor_port"]

            if self.config.debug_resource_mapping:
                LOG.debug(
                    f"Mapped LoxiLB member to Octavia: {utils.sanitize_dict_for_logging(octavia_config)}"
                )

            return utils.filter_none_values(octavia_config)

        except Exception as e:
            LOG.error(f"Failed to map LoxiLB member to Octavia: {e}")
            raise exceptions.LoxiLBOperationException(
                operation="map_member",
                resource_type="member",
                resource_id=loxilb_member.get("id", "unknown"),
                reason=str(e),
            )

    def octavia_to_loxilb_healthmonitor(self, octavia_hm: Dict) -> Dict:
        """Convert Octavia health monitor to LoxiLB format."""
        try:
            # Validate input
            errors = utils.validate_health_check_config(octavia_hm)
            if errors:
                raise exceptions.LoxiLBValidationException(
                    resource_type="healthmonitor", validation_errors=errors
                )

            # Create base LoxiLB configuration
            loxilb_config = utils.create_loxilb_healthmonitor_config(
                octavia_hm, self.config
            )

            # Add LoxiLB specific health monitor configuration
            monitor_type = octavia_hm["type"]

            # Configure type-specific settings
            if monitor_type in ["HTTP", "HTTPS"]:
                loxilb_config.update(
                    {
                        "check_method": "HTTP",
                        "check_ssl": monitor_type == "HTTPS",
                        "http_method": octavia_hm.get("http_method", "GET"),
                        "url_path": octavia_hm.get("url_path", "/"),
                        "expected_codes": utils.parse_expected_codes(
                            octavia_hm.get("expected_codes", "200")
                        ),
                        "http_version": octavia_hm.get("http_version", "1.1"),
                    }
                )

                # Handle domain name for Host header
                if octavia_hm.get("domain_name"):
                    loxilb_config["domain_name"] = octavia_hm["domain_name"]

            elif monitor_type == "TCP":
                loxilb_config.update(
                    {
                        "check_method": "TCP",
                        "tcp_half_open": octavia_hm.get("tcp_half_open", False),
                    }
                )

            elif monitor_type == "UDP_CONNECT":
                loxilb_config.update(
                    {
                        "check_method": "UDP",
                        "udp_request": octavia_hm.get("udp_request", ""),
                        "udp_response": octavia_hm.get("udp_response", ""),
                    }
                )

            elif monitor_type == "PING":
                loxilb_config.update(
                    {
                        "check_method": "PING",
                        "ping_count": octavia_hm.get("ping_count", 3),
                    }
                )

            # Add advanced configuration
            loxilb_config.update(
                {
                    "rise_threshold": octavia_hm.get(
                        "rise_threshold",
                        self.config.default_health_check_rise_threshold,
                    ),
                    "fall_threshold": octavia_hm.get(
                        "fall_threshold",
                        self.config.default_health_check_fall_threshold,
                    ),
                    "check_interval": utils.calculate_health_check_interval(
                        octavia_hm.get("pool_member_count", 1),
                        octavia_hm.get(
                            "delay", self.config.default_health_check_interval
                        ),
                    ),
                }
            )

            if self.config.debug_resource_mapping:
                LOG.debug(
                    f"Mapped Octavia health monitor to LoxiLB: {utils.sanitize_dict_for_logging(loxilb_config)}"
                )

            return loxilb_config

        except Exception as e:
            LOG.error(f"Failed to map Octavia health monitor to LoxiLB: {e}")
            raise exceptions.LoxiLBOperationException(
                operation="map_healthmonitor",
                resource_type="healthmonitor",
                resource_id=octavia_hm.get("id", "unknown"),
                reason=str(e),
            )

    def loxilb_to_octavia_healthmonitor(self, loxilb_hm: Dict) -> Dict:
        """Convert LoxiLB health monitor to Octavia format."""
        try:
            # Map check method back to Octavia type
            check_method = loxilb_hm.get("check_method", "HTTP")
            if check_method == "HTTP":
                monitor_type = "HTTPS" if loxilb_hm.get("check_ssl") else "HTTP"
            elif check_method == "TCP":
                monitor_type = "TCP"
            elif check_method == "UDP":
                monitor_type = "UDP_CONNECT"
            elif check_method == "PING":
                monitor_type = "PING"
            else:
                monitor_type = "HTTP"  # Default fallback

            octavia_config = {
                "id": loxilb_hm["id"],
                "name": loxilb_hm.get("name", ""),
                "pool_id": loxilb_hm["pool_id"],
                "type": monitor_type,
                "delay": loxilb_hm.get(
                    "delay", self.config.default_health_check_interval
                ),
                "timeout": loxilb_hm.get(
                    "timeout", self.config.default_health_check_timeout
                ),
                "max_retries": loxilb_hm.get(
                    "max_retries", self.config.default_health_check_retries
                ),
                "max_retries_down": loxilb_hm.get(
                    "max_retries_down", self.config.default_health_check_fall_threshold
                ),
                "admin_state_up": loxilb_hm.get("admin_state_up", True),
                "operating_status": utils.map_loxilb_status_to_octavia(
                    loxilb_hm.get("operating_status", "OFFLINE"), "operating"
                ),
                "provisioning_status": utils.map_loxilb_status_to_octavia(
                    loxilb_hm.get("provisioning_status", "ACTIVE"), "provisioning"
                ),
                "created_at": loxilb_hm.get("created_at"),
                "updated_at": loxilb_hm.get("updated_at"),
                "project_id": loxilb_hm.get("project_id"),
            }

            # Add type-specific configuration
            if monitor_type in ["HTTP", "HTTPS"]:
                octavia_config.update(
                    {
                        "url_path": loxilb_hm.get("url_path", "/"),
                        "http_method": loxilb_hm.get("http_method", "GET"),
                        "expected_codes": ",".join(
                            map(str, loxilb_hm.get("expected_codes", [200]))
                        ),
                        "http_version": loxilb_hm.get("http_version", "1.1"),
                        "domain_name": loxilb_hm.get("domain_name"),
                    }
                )

            elif monitor_type == "UDP_CONNECT":
                octavia_config.update(
                    {
                        "udp_request": loxilb_hm.get("udp_request", ""),
                        "udp_response": loxilb_hm.get("udp_response", ""),
                    }
                )

            if self.config.debug_resource_mapping:
                LOG.debug(
                    f"Mapped LoxiLB health monitor to Octavia: {utils.sanitize_dict_for_logging(octavia_config)}"
                )

            return utils.filter_none_values(octavia_config)

        except Exception as e:
            LOG.error(f"Failed to map LoxiLB health monitor to Octavia: {e}")
            raise exceptions.LoxiLBOperationException(
                operation="map_healthmonitor",
                resource_type="healthmonitor",
                resource_id=loxilb_hm.get("id", "unknown"),
                reason=str(e),
            )

    def _map_stats_to_octavia(self, loxilb_stats: Dict) -> Dict:
        """Map LoxiLB statistics to Octavia format."""
        return {
            "bytes_in": loxilb_stats.get("bytes_in", 0),
            "bytes_out": loxilb_stats.get("bytes_out", 0),
            "active_connections": loxilb_stats.get("active_connections", 0),
            "total_connections": loxilb_stats.get("total_connections", 0),
            "request_errors": loxilb_stats.get("request_errors", 0),
            "connection_errors": loxilb_stats.get("connection_errors", 0),
            "response_errors": loxilb_stats.get("response_errors", 0),
            "requests_per_second": loxilb_stats.get("requests_per_second", 0),
            "connections_per_second": loxilb_stats.get("connections_per_second", 0),
        }

    def _map_octavia_stats_to_loxilb(self, octavia_stats: Dict) -> Dict:
        """Map Octavia statistics to LoxiLB format."""
        return {
            "bytes_in": octavia_stats.get("bytes_in", 0),
            "bytes_out": octavia_stats.get("bytes_out", 0),
            "active_connections": octavia_stats.get("active_connections", 0),
            "total_connections": octavia_stats.get("total_connections", 0),
            "request_errors": octavia_stats.get("request_errors", 0),
            "connection_errors": octavia_stats.get("connection_errors", 0),
            "response_errors": octavia_stats.get("response_errors", 0),
            "requests_per_second": octavia_stats.get("requests_per_second", 0),
            "connections_per_second": octavia_stats.get("connections_per_second", 0),
        }

    def batch_octavia_to_loxilb(
        self, resources: List[Dict], resource_type: str
    ) -> List[Dict]:
        """Convert multiple Octavia resources to LoxiLB format."""
        mapped_resources = []
        mapping_method = getattr(self, f"octavia_to_loxilb_{resource_type}")

        for resource in resources:
            try:
                mapped_resource = mapping_method(resource)
                mapped_resources.append(mapped_resource)
            except Exception as e:
                LOG.error(
                    f"Failed to map {resource_type} {resource.get('id', 'unknown')}: {e}"
                )
                # Continue with other resources, but track failures
                continue

        LOG.info(
            f"Successfully mapped {len(mapped_resources)}/{len(resources)} {resource_type} resources"
        )
        return mapped_resources

    def batch_loxilb_to_octavia(
        self, resources: List[Dict], resource_type: str
    ) -> List[Dict]:
        """Convert multiple LoxiLB resources to Octavia format."""
        mapped_resources = []
        mapping_method = getattr(self, f"loxilb_to_octavia_{resource_type}")

        for resource in resources:
            try:
                mapped_resource = mapping_method(resource)
                mapped_resources.append(mapped_resource)
            except Exception as e:
                LOG.error(
                    f"Failed to map {resource_type} {resource.get('id', 'unknown')}: {e}"
                )
                # Continue with other resources, but track failures
                continue

        LOG.info(
            f"Successfully mapped {len(mapped_resources)}/{len(resources)} {resource_type} resources"
        )
        return mapped_resources

    def _get_octavia_algorithm(self, loxilb_sel_value):
        """Maps LoxiLB selection value back to Octavia LB algorithm.
        
        Args:
            loxilb_sel_value (int): LoxiLB selection algorithm value (0-6)
            
        Returns:
            str: Octavia algorithm name
        """
        reverse_mapping = {
            0: lib_consts.LB_ALGORITHM_ROUND_ROBIN,
            1: lib_consts.LB_ALGORITHM_SOURCE_IP_PORT,
            2: "PRIORITY",  # LoxiLB extended (not in Octavia lib_consts)
            3: lib_consts.LB_ALGORITHM_SOURCE_IP,
            4: lib_consts.LB_ALGORITHM_LEAST_CONNECTIONS,
        }
        return reverse_mapping.get(loxilb_sel_value, lib_consts.LB_ALGORITHM_ROUND_ROBIN)
