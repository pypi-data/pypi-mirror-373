"""Constants for LoxiLB Octavia Driver."""

from octavia_lib.common import constants as lib_consts

# Driver identification
PROVIDER_NAME = "loxilb"
PROVIDER_DESCRIPTION = "LoxiLB Load Balancer Provider"

# LoxiLB API endpoints
DEFAULT_API_PORT = 11111
DEFAULT_API_TIMEOUT = 30
DEFAULT_API_RETRIES = 3
DEFAULT_API_RETRY_INTERVAL = 5

# LoxiLB API paths
API_PATHS = {
    # Status endpoints
    "status": "/netlox/v1/version",
    # Load balancer endpoints
    "loadbalancer": "/netlox/v1/config/loadbalancer",
    "loadbalancer_all": "/netlox/v1/config/loadbalancer/all",
    "loadbalancer_by_name": "/netlox/v1/config/loadbalancer/name",
    "loadbalancer_by_service": "/netlox/v1/config/loadbalancer/externalipaddress",
    # Endpoint endpoints (for health monitoring)
    "endpoint": "/netlox/v1/config/endpoint",
    "endpoint_all": "/netlox/v1/config/endpoint/all",
    "endpoint_by_ip": "/netlox/v1/config/endpoint/epipaddress",  # Add /{ip_address} for specific endpoint
    "endpoint_host_state": "/netlox/v1/config/endpointhoststate",
    # Metrics endpoints (from swagger.yml)
    "metrics": "/netlox/v1/metrics",
    "metrics_config": "/netlox/v1/config/metrics",
    "metrics_flowcount": "/netlox/v1/metrics/flowcount",
    "metrics_hostcount": "/netlox/v1/metrics/hostcount",
    "metrics_lbrulecount": "/netlox/v1/metrics/lbrulecount",
    "metrics_newflowcount": "/netlox/v1/metrics/newflowcount",
    "metrics_requestcount": "/netlox/v1/metrics/requestcount",
    "metrics_errorcount": "/netlox/v1/metrics/errorcount",
    "metrics_processedtraffic": "/netlox/v1/metrics/processedtraffic",
    "metrics_lbprocessedtraffic": "/netlox/v1/metrics/lbprocessedtraffic",
    "metrics_epdisttraffic": "/netlox/v1/metrics/epdisttraffic",
    "metrics_servicedisttraffic": "/netlox/v1/metrics/servicedisttraffic",
    # Connection tracking endpoints
    "conntrack": "/netlox/v1/config/conntrack",
    "conntrack_all": "/netlox/v1/config/conntrack/all",
}

# Authentication types
AUTH_TYPE_NONE = "none"
AUTH_TYPE_BASIC = "password"
AUTH_TYPE_TOKEN = "token"
AUTH_TYPE_TLS = "tls"

# LoxiLB Load Balancing Algorithm values from swagger.yml
LB_ALGORITHM_ROUND_ROBIN = 0  # Round Robin
LB_ALGORITHM_HASH = 1  # Hash-based 
LB_ALGORITHM_PRIORITY = 2  # Priority-based
LB_ALGORITHM_PERSISTENCE = 3  # Session persistence (source IP)
LB_ALGORITHM_LEAST_CONNECTIONS = 4  # Least connections

# Load balancer algorithms (mapping Octavia to LoxiLB)
LB_ALGORITHM_MAP = {
    lib_consts.LB_ALGORITHM_ROUND_ROBIN: LB_ALGORITHM_ROUND_ROBIN,
    lib_consts.LB_ALGORITHM_LEAST_CONNECTIONS: LB_ALGORITHM_LEAST_CONNECTIONS,
    lib_consts.LB_ALGORITHM_SOURCE_IP: LB_ALGORITHM_PERSISTENCE,
    lib_consts.LB_ALGORITHM_SOURCE_IP_PORT: LB_ALGORITHM_HASH,
    # Default to round robin if not specified
    None: LB_ALGORITHM_ROUND_ROBIN,
}

# Session persistence types
SESSION_PERSISTENCE_MAP = {
    lib_consts.SESSION_PERSISTENCE_SOURCE_IP: "source_ip",
    lib_consts.SESSION_PERSISTENCE_HTTP_COOKIE: "http_cookie",
    lib_consts.SESSION_PERSISTENCE_APP_COOKIE: "app_cookie",
}

# Protocol mapping
PROTOCOL_MAP = {
    lib_consts.PROTOCOL_TCP: "tcp",
    lib_consts.PROTOCOL_UDP: "udp",
    lib_consts.PROTOCOL_SCTP: "sctp",
    lib_consts.PROTOCOL_HTTP: "tcp",  # HTTP over TCP  
    lib_consts.PROTOCOL_HTTPS: "tcp",  # HTTPS over TCP
    lib_consts.PROTOCOL_TERMINATED_HTTPS: "tcp",  # Terminated HTTPS over TCP
    lib_consts.PROTOCOL_PROXY: "tcp",  # Proxy protocol over TCP
    lib_consts.PROTOCOL_PROXYV2: "tcp",  # Proxy v2 protocol over TCP
}

# Health monitor types
HEALTH_MONITOR_TYPE_MAP = {
    lib_consts.HEALTH_MONITOR_HTTP: "http",
    lib_consts.HEALTH_MONITOR_HTTPS: "https",
    lib_consts.HEALTH_MONITOR_TCP: "tcp",
    lib_consts.HEALTH_MONITOR_SCTP: "sctp",
    lib_consts.HEALTH_MONITOR_UDP_CONNECT: "udp",
    lib_consts.HEALTH_MONITOR_PING: "ping",
}

# Operating status mapping (Octavia to LoxiLB)
OPERATING_STATUS_MAP = {
    "ONLINE": lib_consts.ONLINE,
    "OFFLINE": lib_consts.OFFLINE,
    "DEGRADED": lib_consts.DEGRADED,
    "ERROR": lib_consts.ERROR,
    "NO_MONITOR": lib_consts.NO_MONITOR,
}

# LoxiLB endpoint state mapping (for health monitoring)
ENDPOINT_STATE_MAP = {
    # LoxiLB endpoint states to Octavia member operating status
    "green": lib_consts.ONLINE,
    "yellow": lib_consts.DEGRADED,
    "red": lib_consts.ERROR,
}

# Octavia member operating status to LoxiLB endpoint state
MEMBER_STATUS_TO_ENDPOINT_STATE = {
    lib_consts.ONLINE: "green",
    lib_consts.DEGRADED: "yellow", 
    lib_consts.ERROR: "red",
    lib_consts.OFFLINE: "red",
    lib_consts.NO_MONITOR: "green",  # Default to green if no monitoring
}

# LoxiLB endpoint probe types
ENDPOINT_PROBE_TYPE_MAP = {
    lib_consts.HEALTH_MONITOR_HTTP: "http",
    lib_consts.HEALTH_MONITOR_HTTPS: "https", 
    lib_consts.HEALTH_MONITOR_TCP: "tcp",
    lib_consts.HEALTH_MONITOR_UDP_CONNECT: "udp",
    lib_consts.HEALTH_MONITOR_PING: "ping",
}

# Provisioning status mapping
PROVISIONING_STATUS_MAP = {
    "ACTIVE": lib_consts.ACTIVE,
    "PENDING_CREATE": lib_consts.PENDING_CREATE,
    "PENDING_UPDATE": lib_consts.PENDING_UPDATE,
    "PENDING_DELETE": lib_consts.PENDING_DELETE,
    "DELETED": lib_consts.DELETED,
    "ERROR": lib_consts.ERROR,
}

# Resource types
RESOURCE_TYPE_LOADBALANCER = "loadbalancer"
RESOURCE_TYPE_LISTENER = "listener"
RESOURCE_TYPE_POOL = "pool"
RESOURCE_TYPE_MEMBER = "member"
RESOURCE_TYPE_HEALTHMONITOR = "healthmonitor"
RESOURCE_TYPE_L7POLICY = "l7policy"
RESOURCE_TYPE_L7RULE = "l7rule"

# LoxiLB Load Balancer Modes from swagger.yml
LB_MODE_DNAT = 0  # Destination NAT
LB_MODE_ONE_ARM = 1  # One-arm load balancing
LB_MODE_FULL_NAT = 2  # Full NAT
LB_MODE_DSR = 3  # Direct Server Return
LB_MODE_FULL_PROXY = 4  # Full Proxy
LB_MODE_HOST_ONE_ARM = 5  # Host One-arm

# LoxiLB Security Modes from swagger.yml
LB_SECURITY_PLAIN = 0  # Plain (no security)
LB_SECURITY_HTTPS = 1  # HTTPS/TLS
LB_SECURITY_E2E_HTTPS = 2  # End-to-end HTTPS

# LoxiLB specific constants
LOXILB_RESOURCE_PREFIX = "octavia-"
LOXILB_NAMESPACE_PREFIX = "lb-ns-"
DRIVER_VERSION = "0.1.0"

# Default configuration values
DEFAULT_CONFIG = {
    "api_timeout": DEFAULT_API_TIMEOUT,
    "api_retries": DEFAULT_API_RETRIES,
    "api_retry_interval": DEFAULT_API_RETRY_INTERVAL,
    "auth_type": AUTH_TYPE_NONE,
    "default_algorithm": lib_consts.LB_ALGORITHM_ROUND_ROBIN,
    "enable_health_monitor": True,
    "default_health_check_interval": 5,
    "default_health_check_timeout": 3,
    "default_health_check_retries": 3,
    "worker_threads": 4,
    "enable_resource_caching": True,
    "cache_timeout": 300,
    "log_level": "INFO",
    "metrics_enabled": False,
    "enable_failover": True,
    "cluster_health_check_interval": 60,
}


# Error codes
class ErrorCodes:
    """LoxiLB specific error codes."""

    API_CONNECTION_ERROR = "LOXILB_API_CONNECTION_ERROR"
    API_TIMEOUT_ERROR = "LOXILB_API_TIMEOUT_ERROR"
    API_AUTH_ERROR = "LOXILB_API_AUTH_ERROR"
    RESOURCE_NOT_FOUND = "LOXILB_RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "LOXILB_RESOURCE_CONFLICT"
    INVALID_CONFIGURATION = "LOXILB_INVALID_CONFIGURATION"
    CLUSTER_UNAVAILABLE = "LOXILB_CLUSTER_UNAVAILABLE"


# HTTP status codes for LoxiLB API
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_SERVICE_UNAVAILABLE = 503

# Retry configuration
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2
RETRY_EXCEPTIONS = (
    "requests.exceptions.ConnectionError",
    "requests.exceptions.Timeout",
    "requests.exceptions.HTTPError",
)

# Logging format
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Resource naming
MAX_RESOURCE_NAME_LENGTH = 255
RESOURCE_NAME_PATTERN = r"^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$"

# Network configuration
DEFAULT_VIP_NETWORK = "provider"
DEFAULT_MGMT_NETWORK = "octavia-mgmt"

# SSL/TLS configuration
DEFAULT_TLS_VERSIONS = ["TLSv1.2", "TLSv1.3"]
DEFAULT_SSL_CIPHERS = "HIGH:!aNULL:!MD5:!3DES:!RC4"

# Performance limits
MAX_CONNECTIONS_PER_LB = 100000
MAX_LISTENERS_PER_LB = 10
MAX_POOLS_PER_LB = 10
MAX_MEMBERS_PER_POOL = 1000
MAX_HEALTH_MONITORS_PER_POOL = 5

# Cluster configuration
CLUSTER_MODE_ACTIVE_STANDBY = "active_standby"
CLUSTER_MODE_ACTIVE_ACTIVE = "active_active"
DEFAULT_CLUSTER_MODE = CLUSTER_MODE_ACTIVE_STANDBY

# Metrics and monitoring
METRICS_UPDATE_INTERVAL = 30
HEALTH_CHECK_INTERVAL = 60
RESOURCE_CLEANUP_INTERVAL = 3600

# Additional operating status constants not in octavia_lib
DISABLED = "DISABLED"

# Status constants for compatibility when octavia_lib is not available
PROVISIONING_STATUS_ACTIVE = "ACTIVE"
PROVISIONING_STATUS_DELETED = "DELETED"
PROVISIONING_STATUS_ERROR = "ERROR"
PROVISIONING_STATUS_PENDING_CREATE = "PENDING_CREATE"
PROVISIONING_STATUS_PENDING_UPDATE = "PENDING_UPDATE"
PROVISIONING_STATUS_PENDING_DELETE = "PENDING_DELETE"

OPERATING_STATUS_ONLINE = "ONLINE"
OPERATING_STATUS_OFFLINE = "OFFLINE"
OPERATING_STATUS_ERROR = "ERROR"
OPERATING_STATUS_NO_MONITOR = "NO_MONITOR"
