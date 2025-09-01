"""Clean configuration handling for LoxiLB Octavia Driver."""

from oslo_config import cfg
from oslo_log import log as logging

from octavia_loxilb_driver.common import constants
from keystoneauth1 import loading as ks_loading
from octavia.common import constants as octavia_constants

LOG = logging.getLogger(__name__)

# LoxiLB driver configuration group
loxilb_group = cfg.OptGroup(name="loxilb", title="LoxiLB Driver Configuration")

# Service Auth configuration group (do not register options, let keystoneauth1/oslo_config handle it)
service_auth_group = cfg.OptGroup(name="service_auth", title="OpenStack Service Authentication")

# Essential LoxiLB driver configuration options (only what's actually used)
loxilb_opts = [
    # API Configuration
    cfg.ListOpt(
        "api_endpoints",
        default=["http://localhost:8080"],
        help="List of LoxiLB API endpoints (comma-separated). "
        "Format: http://host:port or https://host:port",
    ),
    cfg.IntOpt(
        "api_timeout",
        default=constants.DEFAULT_API_TIMEOUT,
        min=1,
        max=300,
        help="Timeout for LoxiLB API calls in seconds",
    ),
    cfg.IntOpt(
        "api_retries",
        default=constants.DEFAULT_API_RETRIES,
        min=0,
        max=10,
        help="Number of retries for failed API calls",
    ),
    cfg.IntOpt(
        "api_retry_interval",
        default=constants.DEFAULT_API_RETRY_INTERVAL,
        min=1,
        max=60,
        help="Interval between API retry attempts in seconds",
    ),

    # LoxiLB Authentication (for LoxiLB API, not OpenStack)
    cfg.StrOpt(
        "loxilb_auth_type",
        default=constants.AUTH_TYPE_NONE,
        choices=[
            constants.AUTH_TYPE_NONE,
            constants.AUTH_TYPE_BASIC,
            constants.AUTH_TYPE_TOKEN,
            constants.AUTH_TYPE_TLS,
        ],
        help="Authentication type for LoxiLB API. Valid values: none, basic, token, tls.",
    ),
    cfg.StrOpt(
        "loxilb_username", 
        default="", 
        secret=True, 
        help="Username for LoxiLB basic authentication"
    ),
    cfg.StrOpt(
        "loxilb_password", 
        default="", 
        secret=True, 
        help="Password for LoxiLB basic authentication"
    ),
    cfg.StrOpt(
        "api_token",
        default="",
        secret=True,
        help="API token for LoxiLB token-based authentication",
    ),

    # Load Balancer Configuration
    cfg.StrOpt(
        "default_topology",
        default="SINGLE",
        choices=["SINGLE", "ACTIVE_STANDBY", "ACTIVE_ACTIVE"],
        help="Default topology for load balancer deployment",
    ),

    # Worker Configuration
    cfg.IntOpt(
        "worker_threads",
        default=4,
        min=1,
        max=32,
        help="Number of worker threads for processing requests",
    ),

    # Network Configuration
    cfg.StrOpt(
        "mgmt_network_id",
        default="",
        help="ID of the Octavia management network for LoxiLB VMs",
    ),
    cfg.BoolOpt(
        "use_mgmt_network",
        default=True,
        help="Whether to attach LoxiLB VMs to the management network",
    ),
    cfg.StrOpt(
        "mgmt_subnet_id",
        default="",
        help="ID of the management subnet to use for LoxiLB VMs",
    ),

    # VM Configuration (Essential for VM creation)
    cfg.StrOpt(
        "image_id",
        default="",
        help="LoxiLB VM image ID (required)",
    ),
    cfg.StrOpt(
        "flavor_id",
        default="",
        help="OpenStack flavor for LoxiLB VMs (required)",
    ),
    cfg.ListOpt(
        "security_group_ids",
        default=[],
        help="Security group IDs for LoxiLB VMs (required)",
    ),
    cfg.StrOpt(
        "network_id",
        default="",
        help="Management network ID for LoxiLB VMs (required)",
    ),
    cfg.StrOpt(
        "key_name",
        default="",
        help="SSH key name for LoxiLB VM instances (leave empty to create VMs without SSH key)",
    ),

    # OpenStack Authentication (moved from service_auth for backward compatibility)
    # NOTE: These should eventually be moved to [service_auth] group
    cfg.StrOpt(
        "auth_url",
        default="http://localhost:5000",
        help="OpenStack Keystone authentication URL",
    ),
    cfg.StrOpt(
        "auth_type",
        default="password",
        help="OpenStack authentication type",
    ),
    cfg.StrOpt(
        "username",
        default="octavia",
        help="OpenStack authentication username",
    ),
    cfg.StrOpt(
        "password",
        default="",
        secret=True,
        help="OpenStack authentication password",
    ),
    cfg.StrOpt(
        "project_name",
        default="service",
        help="OpenStack project name",
    ),
    cfg.StrOpt(
        "user_domain_name",
        default="Default",
        help="OpenStack user domain name",
    ),
    cfg.StrOpt(
        "project_domain_name",
        default="Default",
        help="OpenStack project domain name",
    ),
]

def register_opts(conf):
    """Register configuration options."""
    conf.register_group(loxilb_group)
    conf.register_opts(loxilb_opts, group=loxilb_group)
    
    # Register service_auth group for keystoneauth1
    conf.register_group(service_auth_group)
    ks_loading.register_auth_conf_options(conf, service_auth_group.name)
    ks_loading.register_session_conf_options(conf, service_auth_group.name)

def validate_config(conf):
    """Validate configuration options."""
    if not conf.loxilb.api_endpoints:
        raise cfg.RequiredOptError("api_endpoints")
    
    # Validate required VM options
    required_vm_opts = ['image_id', 'flavor_id', 'network_id']
    for opt in required_vm_opts:
        if not getattr(conf.loxilb, opt):
            LOG.warning(f"Required option 'loxilb.{opt}' is not set. VM creation may fail.")
    
    if not conf.loxilb.security_group_ids:
        LOG.warning("security_group_ids is not set. VM creation may fail.")
    
    # Validate API endpoints format
    for endpoint in conf.loxilb.api_endpoints:
        if not (endpoint.startswith('http://') or endpoint.startswith('https://')):
            raise cfg.ConfigFileValueError(
                f"Invalid API endpoint format: {endpoint}. "
                "Must start with http:// or https://"
            )

def list_opts():
    """Return a list of oslo_config options available in the library."""
    return [(loxilb_group, loxilb_opts)]
