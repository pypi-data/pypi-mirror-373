"""Utility functions for LoxiLB Octavia Driver."""

import ipaddress
import json
import os
import pickle
import re
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Union
from urllib.parse import urlparse

from octavia_lib.common import constants as lib_consts
from oslo_log import log as logging

from octavia_loxilb_driver.common import constants, exceptions

LOG = logging.getLogger(__name__)


def generate_resource_name(
    resource_type: str, resource_id: str, prefix: str = None
) -> str:
    """Generate LoxiLB resource name from Octavia resource."""
    prefix = prefix or constants.LOXILB_RESOURCE_PREFIX

    # Sanitize resource_id to be LoxiLB compatible
    sanitized_id = re.sub(r"[^a-zA-Z0-9_-]", "-", resource_id)

    # Ensure name doesn't exceed maximum length
    max_length = (
        constants.MAX_RESOURCE_NAME_LENGTH - len(prefix) - len(resource_type) - 2
    )
    if len(sanitized_id) > max_length:
        sanitized_id = sanitized_id[: max_length - 8] + "-" + sanitized_id[-7:]

    name = f"{prefix}{resource_type}-{sanitized_id}"

    # Validate name pattern
    if not re.match(constants.RESOURCE_NAME_PATTERN, name):
        # Fallback to UUID-based name if pattern doesn't match
        name = f"{prefix}{resource_type}-{str(uuid.uuid4())[:8]}"

    return name


def validate_resource_name(name: str) -> bool:
    """Validate resource name against LoxiLB requirements."""
    if not name or len(name) > constants.MAX_RESOURCE_NAME_LENGTH:
        return False

    return bool(re.match(constants.RESOURCE_NAME_PATTERN, name))


def normalize_ip_address(ip_str: str) -> str:
    """Normalize IP address string."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return str(ip)
    except ValueError as e:
        raise exceptions.LoxiLBValidationException(
            resource_type="ip_address",
            validation_errors=[f"Invalid IP address: {ip_str}"],
        )


def validate_ip_address(ip_str: str, allow_ipv6: bool = True) -> bool:
    """Validate IP address format."""
    try:
        ip = ipaddress.ip_address(ip_str)
        if not allow_ipv6 and ip.version == 6:
            return False
        return True
    except ValueError:
        return False


def validate_port_range(port: int) -> bool:
    """Validate port number is in valid range."""
    return 1 <= port <= 65535


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def map_octavia_algorithm_to_loxilb(octavia_algorithm: str) -> str:
    """Map Octavia load balancing algorithm to LoxiLB algorithm."""
    return constants.LB_ALGORITHM_MAP.get(
        octavia_algorithm,
        constants.LB_ALGORITHM_MAP[lib_consts.LB_ALGORITHM_ROUND_ROBIN],
    )


def map_loxilb_algorithm_to_octavia(loxilb_sel_value: int) -> str:
    """Map LoxiLB selection algorithm to Octavia algorithm.

    Args:
        loxilb_sel_value: LoxiLB sel value (0-6)

    Returns:
        str: Octavia algorithm name
    """
    algorithm_map = {
        0: lib_consts.LB_ALGORITHM_ROUND_ROBIN,      # Round Robin
        1: lib_consts.LB_ALGORITHM_SOURCE_IP_PORT,        # Hash-based (source IP)
        2: lib_consts.LB_ALGORITHM_ROUND_ROBIN,      # Priority -> Round Robin fallback
        3: lib_consts.LB_ALGORITHM_SOURCE_IP,        # Persistence -> Source IP
        4: lib_consts.LB_ALGORITHM_LEAST_CONNECTIONS # Least connections
    }

    return algorithm_map.get(loxilb_sel_value, lib_consts.LB_ALGORITHM_ROUND_ROBIN)


def map_octavia_protocol_to_loxilb(octavia_protocol: str) -> str:
    """Map Octavia protocol to LoxiLB protocol."""
    return constants.PROTOCOL_MAP.get(octavia_protocol, octavia_protocol.lower())


def map_loxilb_protocol_to_octavia(loxilb_protocol: str) -> str:
    """Map LoxiLB protocol back to Octavia protocol.
    
    Since LoxiLB uses simple tcp/udp and Octavia has more specific protocols,
    we need to provide sensible defaults for the reverse mapping.
    """
    if not loxilb_protocol:
        return "HTTP"  # Default
    
    protocol_lower = loxilb_protocol.lower()
    
    # Direct mapping for LoxiLB protocols to Octavia protocols
    # Default TCP to HTTP for load balancing (most common case)
    protocol_map = {
        "tcp": "HTTP",
        "udp": "UDP", 
        "http": "HTTP",
        "https": "HTTPS",
        "proxy": "PROXY",
        "proxyv2": "PROXY"
    }
    
    return protocol_map.get(protocol_lower, "HTTP")


def map_octavia_session_persistence_to_loxilb(persistence_type: str) -> str:
    """Map Octavia session persistence to LoxiLB."""
    if not persistence_type:
        return "none"
    return constants.SESSION_PERSISTENCE_MAP.get(persistence_type, "none")


def map_octavia_health_monitor_to_loxilb(monitor_type: str) -> str:
    """Map Octavia health monitor type to LoxiLB."""
    return constants.HEALTH_MONITOR_TYPE_MAP.get(monitor_type, monitor_type.lower())


def map_loxilb_status_to_octavia(
    loxilb_status: str, status_type: str = "operating"
) -> str:
    """Map LoxiLB status to Octavia status."""
    if status_type == "operating":
        return constants.OPERATING_STATUS_MAP.get(
            loxilb_status.upper(), lib_consts.OFFLINE
        )
    elif status_type == "provisioning":
        return constants.PROVISIONING_STATUS_MAP.get(
            loxilb_status.upper(), lib_consts.ERROR
        )
    return loxilb_status


def create_timeout_context(timeout_seconds: int):
    """Create a timeout context for operations."""

    class TimeoutContext:
        def __init__(self, timeout):
            self.timeout = timeout
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def check_timeout(self):
            if self.start_time and time.time() - self.start_time > self.timeout:
                raise exceptions.LoxiLBTimeoutException(
                    endpoint="operation",
                    timeout_value=self.timeout,
                    operation="resource_operation",
                )

        def remaining_time(self) -> float:
            if not self.start_time:
                return self.timeout
            return max(0, self.timeout - (time.time() - self.start_time))

    return TimeoutContext(timeout_seconds)


def retry_operation(
    operation_func,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions_to_catch: tuple = None,
):
    """Retry an operation with exponential backoff."""
    if exceptions_to_catch is None:
        exceptions_to_catch = (Exception,)

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return operation_func()
        except exceptions_to_catch as e:
            last_exception = e
            if attempt < max_retries:
                sleep_time = delay * (backoff_factor**attempt)
                LOG.debug(
                    f"Operation failed (attempt {attempt + 1}/{max_retries + 1}), "
                    f"retrying in {sleep_time:.1f}s: {e}"
                )
                time.sleep(sleep_time)
            else:
                LOG.error(f"Operation failed after {max_retries + 1} attempts: {e}")

    raise last_exception


def sanitize_dict_for_logging(data: Dict, sensitive_keys: List[str] = None) -> Dict:
    """Sanitize dictionary for safe logging by masking sensitive values."""
    if sensitive_keys is None:
        sensitive_keys = ["password", "token", "key", "secret", "auth"]

    sanitized = {}
    for key, value in data.items():
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict_for_logging(value, sensitive_keys)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict_for_logging(item, sensitive_keys)
                if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def extract_resource_id_from_name(
    loxilb_name: str, resource_type: str, prefix: str = None
) -> str:
    """Extract Octavia resource ID from LoxiLB resource name."""
    prefix = prefix or constants.LOXILB_RESOURCE_PREFIX
    expected_prefix = f"{prefix}{resource_type}-"

    if not loxilb_name.startswith(expected_prefix):
        return loxilb_name  # Return as-is if format doesn't match

    return loxilb_name[len(expected_prefix) :]


def merge_dicts(base_dict: Dict, update_dict: Dict) -> Dict:
    """Merge two dictionaries recursively."""
    result = base_dict.copy()

    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def filter_none_values(data: Dict) -> Dict:
    """Remove keys with None values from dictionary."""
    return {k: v for k, v in data.items() if v is not None}


def convert_to_boolean(value: Any) -> bool:
    """Convert various value types to boolean."""
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "on", "enabled")
    elif isinstance(value, (int, float)):
        return value != 0
    else:
        return bool(value)


def format_timestamp(timestamp: Union[int, float, str] = None) -> str:
    """Format timestamp for API calls."""
    if timestamp is None:
        timestamp = time.time()
    elif isinstance(timestamp, str):
        # Assume ISO format string, convert to timestamp
        from datetime import datetime

        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        timestamp = dt.timestamp()

    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp))


def parse_expected_codes(codes_str: str) -> List[int]:
    """Parse expected HTTP codes string into list of integers."""
    if not codes_str:
        return [200]

    codes = []
    for code_part in codes_str.split(","):
        code_part = code_part.strip()
        if "-" in code_part:
            # Range of codes (e.g., "200-299")
            start, end = map(int, code_part.split("-", 1))
            codes.extend(range(start, end + 1))
        else:
            # Single code
            codes.append(int(code_part))

    return codes


def validate_health_check_config(config: Dict) -> List[str]:
    """Validate health check configuration."""
    errors = []

    # Required fields
    if "type" not in config:
        errors.append("Health check type is required")

    # Validate type-specific requirements
    check_type = config.get("type", "").upper()

    if check_type in ["HTTP", "HTTPS"]:
        if "url_path" not in config:
            config["url_path"] = "/"

        if "expected_codes" in config:
            try:
                parse_expected_codes(config["expected_codes"])
            except ValueError:
                errors.append("Invalid expected_codes format")

    # Validate timing parameters
    interval = config.get("delay", 5)
    timeout = config.get("timeout", 3)

    if timeout >= interval:
        errors.append("Health check timeout must be less than interval")

    if interval < 1:
        errors.append("Health check interval must be at least 1 second")

    if timeout < 1:
        errors.append("Health check timeout must be at least 1 second")

    # Validate retry parameters
    max_retries = config.get("max_retries", 3)
    if max_retries < 1:
        errors.append("Health check max_retries must be at least 1")

    return errors


def validate_ssl_certificate(cert_data: Dict) -> List[str]:
    """Validate SSL certificate data."""
    errors = []

    required_fields = ["certificate"]
    for field in required_fields:
        if field not in cert_data or not cert_data[field]:
            errors.append(f"SSL certificate field '{field}' is required")

    # Basic certificate format validation
    cert_content = cert_data.get("certificate", "")
    if cert_content:
        if not cert_content.startswith("-----BEGIN CERTIFICATE-----"):
            errors.append("Certificate must be in PEM format")
        if not cert_content.endswith("-----END CERTIFICATE-----"):
            errors.append("Certificate must be in PEM format")

    # Validate private key if provided
    private_key = cert_data.get("private_key", "")
    if private_key:
        if not private_key.startswith(
            "-----BEGIN PRIVATE KEY-----"
        ) and not private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
            errors.append("Private key must be in PEM format")

    return errors


def calculate_health_check_interval(
    pool_members_count: int, base_interval: int = 5
) -> int:
    """Calculate appropriate health check interval based on pool size."""
    # Increase interval for larger pools to reduce load
    if pool_members_count <= 10:
        return base_interval
    elif pool_members_count <= 50:
        return base_interval + 2
    elif pool_members_count <= 100:
        return base_interval + 5
    else:
        return base_interval + 10


def get_network_info_from_vip(vip_address: str, vip_network_id: str = None) -> Dict:
    """Extract network information from VIP configuration."""
    try:
        ip = ipaddress.ip_address(vip_address)
        return {
            "vip_address": str(ip),
            "ip_version": ip.version,
            "is_multicast": ip.is_multicast,
            "is_private": ip.is_private,
            "is_loopback": ip.is_loopback,
            "network_id": vip_network_id,
        }
    except ValueError:
        raise exceptions.LoxiLBValidationException(
            resource_type="vip_address",
            validation_errors=[f"Invalid VIP address: {vip_address}"],
        )


def generate_resource_tags(
    resource_type: str,
    tenant_id: str = None,
    project_id: str = None,
    additional_tags: Dict = None,
) -> Dict:
    """Generate standard tags for LoxiLB resources."""
    tags = {
        "created_by": "octavia-loxilb-driver",
        "resource_type": resource_type,
        "created_at": format_timestamp(),
        "driver_version": constants.DRIVER_VERSION,
    }

    if tenant_id:
        tags["tenant_id"] = tenant_id

    if project_id:
        tags["project_id"] = project_id

    if additional_tags:
        tags.update(additional_tags)

    return tags


def validate_loadbalancer_config(lb_config: Dict) -> List[str]:
    """Validate load balancer configuration."""
    errors = []

    # Required fields
    required_fields = ["vip_address", "vip_network_id"]
    for field in required_fields:
        if field not in lb_config or not lb_config[field]:
            errors.append(f"Load balancer field '{field}' is required")

    # Validate VIP address
    vip_address = lb_config.get("vip_address")
    if vip_address and not validate_ip_address(vip_address):
        errors.append(f"Invalid VIP address: {vip_address}")

    # Validate algorithm if specified
    algorithm = lb_config.get("lb_algorithm")
    if algorithm and algorithm not in constants.LB_ALGORITHM_MAP:
        errors.append(f"Unsupported load balancing algorithm: {algorithm}")

    return errors


def validate_listener_config(listener_config: Dict) -> List[str]:
    """Validate listener configuration."""
    errors = []

    # Required fields
    required_fields = ["protocol", "protocol_port"]
    for field in required_fields:
        if field not in listener_config:
            errors.append(f"Listener field '{field}' is required")

    # Validate protocol
    protocol = listener_config.get("protocol")
    if protocol and protocol not in constants.PROTOCOL_MAP:
        errors.append(f"Unsupported protocol: {protocol}")

    # Validate port
    port = listener_config.get("protocol_port")
    if port is not None and not validate_port_range(port):
        errors.append(f"Invalid protocol port: {port}")

    # Validate TLS configuration for HTTPS/TERMINATED_HTTPS
    if protocol in [lib_consts.PROTOCOL_HTTPS, lib_consts.PROTOCOL_TERMINATED_HTTPS]:
        if "default_tls_container_ref" not in listener_config:
            errors.append("TLS container reference required for HTTPS listeners")

    return errors


def validate_pool_config(pool_config: Dict) -> List[str]:
    """Validate pool configuration."""
    errors = []

    # Required fields
    required_fields = ["protocol", "lb_algorithm"]
    for field in required_fields:
        if field not in pool_config:
            errors.append(f"Pool field '{field}' is required")

    # Validate protocol
    protocol = pool_config.get("protocol")
    if protocol and protocol not in constants.PROTOCOL_MAP:
        errors.append(f"Unsupported protocol: {protocol}")

    # Validate algorithm
    algorithm = pool_config.get("lb_algorithm")
    if algorithm and algorithm not in constants.LB_ALGORITHM_MAP:
        errors.append(f"Unsupported load balancing algorithm: {algorithm}")

    # Validate session persistence
    persistence = pool_config.get("session_persistence")
    if persistence and isinstance(persistence, dict):
        persistence_type = persistence.get("type")
        if (
            persistence_type
            and persistence_type not in constants.SESSION_PERSISTENCE_MAP
        ):
            errors.append(f"Unsupported session persistence type: {persistence_type}")

    return errors


def validate_member_config(member_config: Dict) -> List[str]:
    """Validate member configuration."""
    errors = []

    # Required fields
    required_fields = ["address", "protocol_port"]
    for field in required_fields:
        if field not in member_config:
            errors.append(f"Member field '{field}' is required")

    # Validate address
    address = member_config.get("address")
    if address and not validate_ip_address(address):
        errors.append(f"Invalid member address: {address}")

    # Validate port
    port = member_config.get("protocol_port")
    if port is not None and not validate_port_range(port):
        errors.append(f"Invalid protocol port: {port}")

    # Validate weight
    weight = member_config.get("weight")
    if weight is not None and (weight < 0 or weight > 256):
        errors.append(f"Member weight must be between 0 and 256: {weight}")

    return errors


def create_loxilb_loadbalancer_config(octavia_lb: Dict, config: object) -> Dict:
    """Create LoxiLB load balancer configuration from Octavia data."""
    lb_config = {
        "id": octavia_lb["id"],
        "name": generate_resource_name("lb", octavia_lb["id"]),
        "description": octavia_lb.get("description", ""),
        "vip_address": octavia_lb["vip_address"],
        "vip_network_id": octavia_lb["vip_network_id"],
        "vip_subnet_id": octavia_lb.get("vip_subnet_id"),
        "admin_state_up": octavia_lb.get("admin_state_up", True),
        "tags": generate_resource_tags(
            "loadbalancer", octavia_lb.get("project_id"), octavia_lb.get("project_id")
        ),
    }

    # Add LoxiLB specific configuration
    lb_config.update(
        {
            "algorithm": map_octavia_algorithm_to_loxilb(
                octavia_lb.get("lb_algorithm", config.default_algorithm)
            ),
            "connection_limit": octavia_lb.get(
                "connection_limit", config.default_connection_limit
            ),
            "timeout_client": config.default_timeout_client,
            "timeout_server": config.default_timeout_server,
            "timeout_connect": config.default_timeout_connect,
        }
    )

    return filter_none_values(lb_config)


def create_loxilb_listener_config(octavia_listener: Dict, config: object) -> Dict:
    """Create LoxiLB listener configuration from Octavia data."""
    listener_config = {
        "id": octavia_listener["id"],
        "name": generate_resource_name("listener", octavia_listener["id"]),
        "description": octavia_listener.get("description", ""),
        "loadbalancer_id": octavia_listener["loadbalancer_id"],
        "protocol": map_octavia_protocol_to_loxilb(octavia_listener["protocol"]),
        "protocol_port": octavia_listener["protocol_port"],
        "admin_state_up": octavia_listener.get("admin_state_up", True),
        "connection_limit": octavia_listener.get(
            "connection_limit", config.default_connection_limit
        ),
        "tags": generate_resource_tags(
            "listener",
            octavia_listener.get("project_id"),
            octavia_listener.get("project_id"),
        ),
    }

    # Handle TLS configuration
    if octavia_listener.get("default_tls_container_ref"):
        listener_config["tls_container_ref"] = octavia_listener[
            "default_tls_container_ref"
        ]
        listener_config["tls_enabled"] = True

    # Handle SNI containers
    if octavia_listener.get("sni_container_refs"):
        listener_config["sni_container_refs"] = octavia_listener["sni_container_refs"]

    return filter_none_values(listener_config)


def create_loxilb_pool_config(octavia_pool: Dict, config: object) -> Dict:
    """Create LoxiLB pool configuration from Octavia data."""
    pool_config = {
        "id": octavia_pool["id"],
        "name": generate_resource_name("pool", octavia_pool["id"]),
        "description": octavia_pool.get("description", ""),
        "loadbalancer_id": octavia_pool.get("loadbalancer_id"),
        "listener_id": octavia_pool.get("listener_id"),
        "protocol": map_octavia_protocol_to_loxilb(octavia_pool["protocol"]),
        "lb_algorithm": map_octavia_algorithm_to_loxilb(octavia_pool["lb_algorithm"]),
        "admin_state_up": octavia_pool.get("admin_state_up", True),
        "tags": generate_resource_tags(
            "pool", octavia_pool.get("project_id"), octavia_pool.get("project_id")
        ),
    }

    # Handle session persistence
    session_persistence = octavia_pool.get("session_persistence")
    if session_persistence and session_persistence.get("type"):
        pool_config["session_persistence"] = {
            "type": map_octavia_session_persistence_to_loxilb(
                session_persistence["type"]
            ),
            "cookie_name": session_persistence.get("cookie_name"),
        }

    return filter_none_values(pool_config)


def create_loxilb_member_config(octavia_member: Dict, config: object) -> Dict:
    """Create LoxiLB member configuration from Octavia data."""
    member_config = {
        "id": octavia_member["id"],
        "name": generate_resource_name("member", octavia_member["id"]),
        "pool_id": octavia_member["pool_id"],
        "address": octavia_member["address"],
        "protocol_port": octavia_member["protocol_port"],
        "weight": octavia_member.get("weight", 1),
        "admin_state_up": octavia_member.get("admin_state_up", True),
        "subnet_id": octavia_member.get("subnet_id"),
        "tags": generate_resource_tags(
            "member", octavia_member.get("project_id"), octavia_member.get("project_id")
        ),
    }

    # Add backup configuration if specified
    if octavia_member.get("backup", False):
        member_config["backup"] = True

    return filter_none_values(member_config)


def create_loxilb_healthmonitor_config(octavia_hm: Dict, config: object) -> Dict:
    """Create LoxiLB health monitor configuration from Octavia data."""
    hm_config = {
        "id": octavia_hm["id"],
        "name": generate_resource_name("hm", octavia_hm["id"]),
        "pool_id": octavia_hm["pool_id"],
        "type": map_octavia_health_monitor_to_loxilb(octavia_hm["type"]),
        "delay": octavia_hm.get("delay", config.default_health_check_interval),
        "timeout": octavia_hm.get("timeout", config.default_health_check_timeout),
        "max_retries": octavia_hm.get(
            "max_retries", config.default_health_check_retries
        ),
        "max_retries_down": octavia_hm.get(
            "max_retries_down", config.default_health_check_fall_threshold
        ),
        "admin_state_up": octavia_hm.get("admin_state_up", True),
        "tags": generate_resource_tags(
            "healthmonitor", octavia_hm.get("project_id"), octavia_hm.get("project_id")
        ),
    }

    # Add HTTP/HTTPS specific configuration
    if octavia_hm["type"] in ["HTTP", "HTTPS"]:
        hm_config.update(
            {
                "url_path": octavia_hm.get("url_path", config.default_health_check_url),
                "http_method": octavia_hm.get("http_method", "GET"),
                "expected_codes": octavia_hm.get(
                    "expected_codes", config.default_health_check_expected_codes
                ),
                "http_version": octavia_hm.get("http_version", "1.1"),
            }
        )

    return filter_none_values(hm_config)


def get_driver_stats() -> Dict:
    """Get driver statistics for monitoring."""
    return {
        "driver_name": constants.DRIVER_NAME,
        "driver_version": constants.DRIVER_VERSION,
        "timestamp": format_timestamp(),
        "uptime": time.time(),  # This would need to be calculated from driver start time
    }


# ID mapping and service key utilities for LoxiLB integration

def get_loxilb_service_key(external_ip: str, port: int, protocol: str) -> str:
    """Get LoxiLB service key for API calls.

    Args:
        external_ip: External IP address
        port: Service port
        protocol: Protocol (tcp/udp)

    Returns:
        str: Service key in format "ip:port/protocol"
    """
    protocol = protocol.lower() if protocol else "tcp"
    return f"{external_ip}:{port}/{protocol}"


def generate_uuid() -> str:
    """Generate a new random UUID string.

    Returns:
        str: New UUID string
    """
    return str(uuid.uuid4())


def parse_loxilb_service_key(service_key: str) -> Dict[str, Any]:
    """Parse LoxiLB service key back to components.

    Args:
        service_key: Service key in format "ip:port/protocol"

    Returns:
        dict: Dictionary with external_ip, port, protocol

    Raises:
        ValueError: If service key format is invalid
    """
    try:
        # Split protocol first
        if "/" in service_key:
            ip_port, protocol = service_key.rsplit("/", 1)
        else:
            ip_port = service_key
            protocol = "tcp"

        # Split IP and port
        if ":" in ip_port:
            external_ip, port_str = ip_port.rsplit(":", 1)
            port = int(port_str)
        else:
            raise ValueError("Invalid service key format: missing port")

        return {
            "external_ip": external_ip,
            "port": port,
            "protocol": protocol,
        }
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid LoxiLB service key format '{service_key}': {e}")


def create_id_mapping_cache(storage_path: str = None) -> Dict[str, Dict[str, str]]:
    """Create in-memory cache for ID mappings with optional persistent storage.

    Args:
        storage_path: Optional path to persistent storage file

    Returns:
        dict: Cache structure for storing ID mappings
    """
    cache = {
        "octavia_to_loxilb": {},  # octavia_id -> loxilb_key
        "loxilb_to_octavia": {},  # loxilb_key -> octavia_id
        "resource_metadata": {},   # octavia_id -> resource metadata
        "_storage_path": storage_path,  # Path for persistence
        "_lock": threading.RLock(),     # Thread safety
    }
    
    # Load existing mappings if storage path is provided
    if storage_path:
        load_id_mappings_from_storage(cache)
    
    return cache


def save_id_mappings_to_storage(cache: Dict) -> bool:
    """Save ID mappings to persistent storage.
    
    Args:
        cache: ID mapping cache
        
    Returns:
        bool: True if successful, False otherwise
    """
    storage_path = cache.get("_storage_path")
    if not storage_path:
        return False
    
    try:
        with cache["_lock"]:
            # Prepare data for storage (exclude lock and storage_path)
            storage_data = {
                "octavia_to_loxilb": cache["octavia_to_loxilb"].copy(),
                "loxilb_to_octavia": cache["loxilb_to_octavia"].copy(), 
                "resource_metadata": cache["resource_metadata"].copy(),
                "last_saved": time.time(),
                "version": "1.0"
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            
            # Write to temporary file first, then atomic rename
            temp_path = f"{storage_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(storage_data, f, indent=2, default=str)
            
            # Atomic rename
            os.rename(temp_path, storage_path)
            
            LOG.debug(f"Saved ID mappings to {storage_path}")
            return True
            
    except Exception as e:
        LOG.error(f"Failed to save ID mappings to storage: {e}")
        return False


def load_id_mappings_from_storage(cache: Dict) -> bool:
    """Load ID mappings from persistent storage.
    
    Args:
        cache: ID mapping cache to populate
        
    Returns:
        bool: True if successful, False otherwise
    """
    storage_path = cache.get("_storage_path")
    if not storage_path or not os.path.exists(storage_path):
        return False
    
    try:
        with cache["_lock"]:
            with open(storage_path, 'r') as f:
                storage_data = json.load(f)
            
            # Validate data structure
            if not isinstance(storage_data, dict):
                raise ValueError("Invalid storage data format")
            
            # Load mappings
            cache["octavia_to_loxilb"].update(
                storage_data.get("octavia_to_loxilb", {})
            )
            cache["loxilb_to_octavia"].update(
                storage_data.get("loxilb_to_octavia", {})
            )
            cache["resource_metadata"].update(
                storage_data.get("resource_metadata", {})
            )
            
            loaded_count = len(cache["octavia_to_loxilb"])
            LOG.info(f"Loaded {loaded_count} ID mappings from {storage_path}")
            
            # Migrate loadbalancer metadata to support multiple listeners
            migrated_count = migrate_loadbalancer_metadata(cache)
            if migrated_count > 0:
                LOG.info(f"Migrated {migrated_count} loadbalancer entries to support multiple listeners")
            
            return True
            
    except Exception as e:
        LOG.error(f"Failed to load ID mappings from storage: {e}")
        return False


def store_id_mapping(
    cache: Dict[str, Dict[str, str]], 
    octavia_id: str, 
    loxilb_key: str, 
    resource_type: str,
    metadata: Dict = None
) -> None:
    """Store ID mapping with automatic persistence.

    Args:
        cache: ID mapping cache
        octavia_id: Octavia resource ID
        loxilb_key: LoxiLB resource key
        resource_type: Type of resource (loadbalancer, listener, etc.)
        metadata: Additional metadata to store
    """
    with cache.get("_lock", threading.RLock()):
        # Store bidirectional mappings
        cache["octavia_to_loxilb"][octavia_id] = loxilb_key
        cache["loxilb_to_octavia"][loxilb_key] = octavia_id
        
        # Prepare metadata
        metadata_dict = {
            "resource_type": resource_type,
            "loxilb_key": loxilb_key,
            "created_at": time.time(),
            **(metadata or {})
        }
        
        # Special handling for listeners - update loadbalancer metadata to track multiple listeners
        if resource_type == "listener" and metadata and "lb_id" in metadata:
            lb_id = metadata["lb_id"]
            lb_metadata = cache["resource_metadata"].get(lb_id, {})
            
            if lb_metadata and lb_metadata.get("resource_type") == "loadbalancer":
                # Initialize listeners list if it doesn't exist
                if "listeners" not in lb_metadata:
                    lb_metadata["listeners"] = []
                
                # Add this listener to the loadbalancer's listeners list if not already present
                if octavia_id not in lb_metadata["listeners"]:
                    lb_metadata["listeners"].append(octavia_id)
                    LOG.info("Added listener %s to loadbalancer %s listeners list", octavia_id, lb_id)
                
                # For backward compatibility, also set the single listener_id field
                lb_metadata["listener_id"] = octavia_id
                
                # Update the loadbalancer metadata in the cache
                cache["resource_metadata"][lb_id] = lb_metadata
        
        # Store metadata for this resource
        cache["resource_metadata"][octavia_id] = metadata_dict
        
        # Auto-save to persistent storage if configured
        if cache.get("_storage_path"):
            save_id_mappings_to_storage(cache)


def remove_id_mapping(cache: Dict[str, Dict[str, str]], octavia_id: str) -> None:
    """Remove ID mapping with automatic persistence.

    Args:
        cache: ID mapping cache
        octavia_id: Octavia resource ID to remove
    """
    with cache.get("_lock", threading.RLock()):
        # Get loxilb_key before removing
        loxilb_key = cache["octavia_to_loxilb"].get(octavia_id)
        
        # Get resource metadata before removing
        resource_metadata = cache["resource_metadata"].get(octavia_id, {})
        resource_type = resource_metadata.get("resource_type") if resource_metadata else None
        
        # Remove all mappings
        cache["octavia_to_loxilb"].pop(octavia_id, None)
        if loxilb_key:
            cache["loxilb_to_octavia"].pop(loxilb_key, None)
        cache["resource_metadata"].pop(octavia_id, None)
        
        # Clean up references to this resource in other resources' metadata
        if resource_type == "listener":
            # Find loadbalancers that reference this listener
            for other_id, other_metadata in list(cache["resource_metadata"].items()):
                if other_metadata.get("resource_type") == "loadbalancer":
                    # Check if this listener is in the listeners list
                    listeners_list = other_metadata.get("listeners", [])
                    if octavia_id in listeners_list:
                        listeners_list.remove(octavia_id)
                        LOG.info("Removed listener %s from loadbalancer %s listeners list", octavia_id, other_id)
                    
                    # Also check the legacy single listener_id field
                    if other_metadata.get("listener_id") == octavia_id:
                        other_metadata.pop("listener_id", None)
                        LOG.info("Removed listener reference %s from loadbalancer %s metadata", octavia_id, other_id)
        
        elif resource_type == "pool":
            # Find listeners that reference this pool
            for other_id, other_metadata in list(cache["resource_metadata"].items()):
                if other_metadata.get("resource_type") == "listener" and other_metadata.get("pool_id") == octavia_id:
                    # Remove the pool reference from the listener metadata
                    other_metadata.pop("pool_id", None)
                    LOG.info("Removed pool reference %s from listener %s metadata", octavia_id, other_id)
        
        elif resource_type == "member":
            # Find pools that reference this member in their members list
            for other_id, other_metadata in list(cache["resource_metadata"].items()):
                if other_metadata.get("resource_type") == "pool" and other_metadata.get("members"):
                    members = other_metadata.get("members", [])
                    if octavia_id in members:
                        members.remove(octavia_id)
                        LOG.info("Removed member reference %s from pool %s metadata", octavia_id, other_id)
        
        elif resource_type == "healthmonitor":
            # Find pools that reference this health monitor
            for other_id, other_metadata in list(cache["resource_metadata"].items()):
                if other_metadata.get("resource_type") == "pool" and other_metadata.get("healthmonitor_id") == octavia_id:
                    # Remove the healthmonitor reference from the pool metadata
                    other_metadata.pop("healthmonitor_id", None)
                    LOG.info("Removed healthmonitor reference %s from pool %s metadata", octavia_id, other_id)
        
        # Auto-save to persistent storage if configured
        if cache.get("_storage_path"):
            save_id_mappings_to_storage(cache)


def get_loxilb_key_from_octavia_id(cache: Dict[str, Dict[str, str]], octavia_id: str) -> str:
    """Get LoxiLB key from Octavia ID.
    
    Args:
        cache: ID mapping cache
        octavia_id: Octavia resource ID
        
    Returns:
        str: LoxiLB key or None if not found
    """
    return cache["octavia_to_loxilb"].get(octavia_id)


def get_octavia_id_from_loxilb_key(cache: Dict[str, Dict[str, str]], loxilb_key: str) -> str:
    """Get Octavia ID from LoxiLB key.
    
    Args:
        cache: ID mapping cache
        loxilb_key: LoxiLB resource key
        
    Returns:
        str: Octavia ID or None if not found
    """
    return cache["loxilb_to_octavia"].get(loxilb_key)


def get_id_mapping_metadata(cache: Dict[str, Dict[str, str]], octavia_id: str) -> Dict:
    """Get metadata for an ID mapping.
    
    Args:
        cache: ID mapping cache
        octavia_id: Octavia resource ID
        
    Returns:
        dict: Metadata dictionary or empty dict if not found
    """
    return cache["resource_metadata"].get(octavia_id, {})


def migrate_loadbalancer_metadata(cache: Dict[str, Dict[str, str]]) -> int:
    """Migrate existing loadbalancer metadata to support multiple listeners.
    
    This function scans all loadbalancer metadata entries and converts them to use
    the new 'listeners' list format while maintaining backward compatibility with
    the single 'listener_id' field.
    
    Args:
        cache: ID mapping cache
        
    Returns:
        int: Number of loadbalancer entries migrated
    """
    migrated_count = 0
    
    with cache.get("_lock", threading.RLock()):
        # Find all loadbalancer entries
        for lb_id, lb_metadata in list(cache["resource_metadata"].items()):
            if lb_metadata.get("resource_type") == "loadbalancer":
                # Check if this loadbalancer already has a listeners list
                if "listeners" not in lb_metadata:
                    # Initialize the listeners list
                    lb_metadata["listeners"] = []
                    
                    # If there's a single listener_id, add it to the list
                    listener_id = lb_metadata.get("listener_id")
                    if listener_id:
                        lb_metadata["listeners"].append(listener_id)
                        LOG.info("Migrated loadbalancer %s: added listener %s to listeners list", 
                                lb_id, listener_id)
                    
                    # Update the loadbalancer metadata in the cache
                    cache["resource_metadata"][lb_id] = lb_metadata
                    migrated_count += 1
    
    # Save changes if any loadbalancers were migrated
    if migrated_count > 0 and cache.get("_storage_path"):
        save_id_mappings_to_storage(cache)
        LOG.info("Migrated %d loadbalancer entries to support multiple listeners", migrated_count)
    
    return migrated_count


def recover_id_mappings_from_loxilb(
    cache: Dict, 
    api_client, 
    resource_mapper
) -> int:
    """Recover ID mappings by scanning LoxiLB and generating deterministic IDs.
    
    This is the fallback recovery method when persistent storage is not available
    or corrupted. It scans all LoxiLB services and rebuilds mappings using
    deterministic ID generation.
    
    Args:
        cache: ID mapping cache
        api_client: LoxiLB API client
        resource_mapper: Resource mapper instance
        
    Returns:
        int: Number of mappings recovered
    """
    LOG.info("Starting ID mapping recovery from LoxiLB...")
    
    try:
        with cache.get("_lock", threading.RLock()):
            # Get all services from LoxiLB
            loxilb_services = api_client.list_loadbalancers()
            
            recovered_count = 0
            
            for service in loxilb_services:
                try:
                    service_args = service.get("serviceArguments", {})
                    
                    # Generate deterministic Octavia ID
                    octavia_id = generate_deterministic_id(
                        "loadbalancer",
                        external_ip=service_args.get("externalIP"),
                        port=service_args.get("port"),
                        protocol=service_args.get("protocol")
                    )
                    
                    # Generate LoxiLB service key
                    loxilb_service_key = get_loxilb_service_key(
                        service_args["externalIP"],
                        service_args["port"],
                        service_args["protocol"]
                    )
                    
                    # Store the recovered mapping
                    store_id_mapping(
                        cache,
                        octavia_id,
                        loxilb_service_key,
                        "loadbalancer",
                        {
                            "recovered_from_loxilb": True,
                            "recovery_time": time.time(),
                            "external_ip": service_args["externalIP"],
                            "port": service_args["port"],
                            "protocol": service_args["protocol"],
                            "service_name": service_args.get("name", "")
                        }
                    )
                    
                    recovered_count += 1
                    
                except Exception as e:
                    LOG.warning(f"Failed to recover mapping for service: {e}")
                    continue
            
            LOG.info(f"Recovered {recovered_count} ID mappings from LoxiLB")
            return recovered_count
            
    except Exception as e:
        LOG.error(f"Failed to recover ID mappings from LoxiLB: {e}")
        return 0


def generate_deterministic_id(resource_type: str, **kwargs) -> str:
    """Generate deterministic UUID from resource properties.

    This function creates consistent UUIDs for LoxiLB resources that don't have
    native IDs, allowing Octavia to track them reliably.

    Args:
        resource_type: Type of resource (loadbalancer, listener, pool, member, healthmonitor)
        **kwargs: Properties used to generate the unique identifier

    Returns:
        str: Deterministic UUID string

    Examples:
        >>> generate_deterministic_id("loadbalancer", external_ip="192.168.1.100", port=80, protocol="tcp")
        '550e8400-e29b-41d4-a716-446655440000'
    """
    import hashlib

    # Create stable key from resource type and properties
    key_parts = [resource_type]

    # Sort kwargs to ensure consistent ordering
    for k, v in sorted(kwargs.items()):
        if v is not None:
            # Convert to string and normalize
            if isinstance(v, str):
                v = v.lower().strip()
            key_parts.append(f"{k}={v}")

    # Create the key string
    key = "|".join(key_parts)

    # Generate UUID5 from DNS namespace and key
    # Using DNS namespace for consistency across driver instances
    namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
    deterministic_uuid = uuid.uuid5(namespace, key)

    LOG.debug(
        f"Generated deterministic ID for {resource_type}: {deterministic_uuid} (key: {key})"
    )

    return str(deterministic_uuid)


def get_current_timestamp():
    """Get current timestamp in ISO format.
    
    Returns:
        str: Current timestamp in ISO format
    """
    from datetime import datetime
    return datetime.utcnow().isoformat() + 'Z'
