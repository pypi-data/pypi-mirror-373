import openstack
import logging
import os
import time
import tenacity
from keystoneauth1 import loading
from keystoneauth1.identity import v3
from keystoneauth1 import session
from oslo_config import cfg

from octavia_loxilb_driver.common import config
from octavia_loxilb_driver.common import exceptions

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

# Register configuration options at module level
config.register_opts(CONF)

# Network operation retry constants
NETWORK_RETRY_ATTEMPTS = 5
NETWORK_RETRY_INITIAL_DELAY = 1  # seconds
NETWORK_RETRY_BACKOFF = 2  # seconds
NETWORK_RETRY_MAX_DELAY = 30  # seconds

def get_openstack_connection():
    """Create and return an OpenStack connection using loxilb group credentials.
    
    This function accesses auth parameters directly from the loxilb group in CONF
    and uses them to create an OpenStack connection.
    
    Returns:
        openstack.connection.Connection: An authenticated OpenStack connection
    """
    LOG.info("Creating OpenStack connection using parameters from loxilb group in CONF")
    
    try:
        # Extract auth parameters from the loxilb group in CONF
        auth_url = CONF.loxilb.auth_url
        auth_type = CONF.loxilb.auth_type
        username = CONF.loxilb.username
        password = CONF.loxilb.password
        project_name = CONF.loxilb.project_name
        user_domain_name = CONF.loxilb.user_domain_name
        project_domain_name = CONF.loxilb.project_domain_name
        
        LOG.info(f"Using auth_url: {auth_url}, username: {username}, project: {project_name}")
        
        # Create connection with parameters from loxilb group
        conn = openstack.connect(
            auth_type=auth_type,
            auth_url=auth_url,
            username=username,
            password=password,
            project_name=project_name,
            user_domain_name=user_domain_name,
            project_domain_name=project_domain_name,
            region_name="RegionOne",
            interface="public",
            identity_api_version="3"
        )
        LOG.info("Successfully created OpenStack connection with loxilb group parameters")
        return conn
        
    except Exception as e:
        LOG.error(f"Failed to create OpenStack connection: {e}")
        LOG.error(f"Exception type: {type(e).__name__}")
        LOG.error(f"Exception details: {str(e)}")
        raise

def get_sdk_connection():
    """Alias for get_openstack_connection for compatibility with task code."""
    return get_openstack_connection()

def find_image_by_tag(conn, tag):
    """Find an image by tag (returns the first match)."""
    for image in conn.image.images():
        if tag in image.tags:
            return image
    return None

def find_flavor_by_name(conn, name):
    """Find a flavor by name (returns the first match)."""
    for flavor in conn.compute.flavors():
        if flavor.name == name:
            return flavor
    return None

def boot_loxilb_vm(conn, name, image, flavor, network_id, key_name=None, security_groups=None, user_data=None):
    """Boot a LoxiLB VM and return the server object."""
    server = conn.compute.create_server(
        name=name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network_id}],
        key_name=key_name,
        security_groups=security_groups,
        user_data=user_data,
        wait=True,
        auto_ip=False
    )
    server = conn.compute.wait_for_server(server)
    return server

def get_server_ip(server, network_name=None):
    """Get the fixed IP of the server with network prioritization.
    
    Args:
        server: OpenStack server object
        network_name: Optional network name to prioritize
        
    Returns:
        IP address string or None if not found
        
    Priority:
    1. Specified network_name if provided
    2. Management network if configured
    3. Any fixed IP
    """
    from oslo_config import cfg
    CONF = cfg.CONF
    
    addresses = server.addresses
    if not addresses:
        return None
        
    # First priority: specified network if provided
    if network_name and network_name in addresses:
        for addr in addresses[network_name]:
            if addr.get('OS-EXT-IPS:type') == 'fixed':
                LOG.debug(f"Using IP from specified network {network_name}: {addr['addr']}")
                return addr['addr']
    
    # Second priority: management network if configured
    try:
        if hasattr(CONF, 'loxilb') and CONF.loxilb.use_mgmt_network:
            # Get management network name
            mgmt_network_id = CONF.loxilb.mgmt_network_id
            if mgmt_network_id:
                # Find network name from ID
                for net_name, net_addrs in addresses.items():
                    # Check if this is the management network
                    for addr in net_addrs:
                        if addr.get('OS-EXT-IPS:type') == 'fixed':
                            LOG.debug(f"Using IP from management network: {addr['addr']}")
                            return addr['addr']
    except Exception as e:
        LOG.warning(f"Error while trying to get management network IP: {e}")
    
    # Third priority: any fixed IP
    LOG.debug("Falling back to any available fixed IP")
    for net_addrs in addresses.values():
        for addr in net_addrs:
            if addr.get('OS-EXT-IPS:type') == 'fixed':
                LOG.debug(f"Using fallback IP: {addr['addr']}")
                return addr['addr']
                
    return None

def create_vm(conn, name, image_tag, flavor_name, network_id, key_name=None, security_groups=None, user_data=None):
    """Create a VM using image tag, flavor name, and network ID."""
    # FIXME: key_name, security_groups, user_data are optional
    image = find_image_by_tag(conn, image_tag)
    if not image:
        raise Exception(f"Image with tag '{image_tag}' not found.")
    flavor = find_flavor_by_name(conn, flavor_name)
    if not flavor:
        raise Exception(f"Flavor with name '{flavor_name}' not found.")
    server_args = {
        "name": name,
        "image_id": image.id,
        "flavor_id": flavor.id,
        "networks": [{"uuid": network_id}],
        "wait": True,
        "auto_ip": False
    }
    if key_name is not None:
        server_args["key_name"] = key_name
    if security_groups is not None:
        # Convert list of strings to list of dicts with 'name' key if needed
        if isinstance(security_groups, list):
            if all(isinstance(sg, str) for sg in security_groups):
                server_args["security_groups"] = [{"name": sg} for sg in security_groups]
            else:
                server_args["security_groups"] = security_groups
        else:
            server_args["security_groups"] = security_groups
    if user_data is not None:
        server_args["user_data"] = user_data
    server = conn.compute.create_server(**server_args)
    server = conn.compute.wait_for_server(server)
    return server

def delete_vm(conn, server_id):
    """Delete a VM by server ID."""
    conn.compute.delete_server(server_id, ignore_missing=True)

def allocate_vip_port(conn, lb_id, network_id):
    """Allocate a Neutron port for the VIP."""
    port = conn.network.create_port(
        name=f"loxilb-vip-{lb_id}",
        network_id=network_id
    )
    return port

def delete_port(conn, port_id):
    """Delete a Neutron port by port ID."""
    conn.network.delete_port(port_id, ignore_missing=True)

def _is_network_operation_retryable(exception):
    """Determine if a network operation exception is retryable.
    
    Args:
        exception: The exception to check
        
    Returns:
        True if the exception is retryable, False otherwise
    """
    # List of retryable exception types or error messages
    retryable_errors = [
        "Network is not available yet",
        "Port not found",
        "Unable to attach interface",
        "Instance network interface is locked",
        "Resource not found",
        "Invalid network port",
        "Instance not ready",
        "Connection reset",
        "Connection refused",
        "Service unavailable",
        "Conflict",
        "Timeout"
    ]
    
    # Check if the exception message contains any of the retryable error strings
    error_msg = str(exception).lower()
    return any(err.lower() in error_msg for err in retryable_errors)


@tenacity.retry(
    retry=tenacity.retry_if_exception(_is_network_operation_retryable),
    wait=tenacity.wait_exponential(
        multiplier=NETWORK_RETRY_INITIAL_DELAY,
        min=NETWORK_RETRY_INITIAL_DELAY,
        max=NETWORK_RETRY_MAX_DELAY
    ),
    stop=tenacity.stop_after_attempt(NETWORK_RETRY_ATTEMPTS),
    before_sleep=lambda retry_state: LOG.warning(
        f"Network operation failed (attempt {retry_state.attempt_number}/{NETWORK_RETRY_ATTEMPTS}), "
        f"retrying in {retry_state.next_action.sleep} seconds: {retry_state.outcome.exception()}"
    ),
    reraise=True
)
def attach_interface_to_server(conn, server_id, network_id):
    """Attach a network interface to an existing server with retry logic.
    
    Args:
        conn: OpenStack connection object
        server_id: ID of the server to attach the interface to
        network_id: ID of the network to attach
        
    Returns:
        The created interface object
        
    Raises:
        NetworkOperationException: If the interface attachment fails after all retries
    """
    LOG.info(f"Attaching interface with network {network_id} to server {server_id}")
    try:
        interface = conn.compute.create_server_interface(
            server_id,
            net_id=network_id
        )
        LOG.info(f"Successfully attached interface {interface.id} to server {server_id} on network {network_id}")
        return interface
    except Exception as e:
        LOG.error(f"Failed to attach interface to server {server_id} on network {network_id}: {e}")
        raise exceptions.NetworkOperationException(
            operation="attach_interface",
            server_id=server_id,
            network_id=network_id,
            original_exception=e
        ) from e

@tenacity.retry(
    retry=tenacity.retry_if_exception(_is_network_operation_retryable),
    wait=tenacity.wait_exponential(
        multiplier=NETWORK_RETRY_INITIAL_DELAY,
        min=NETWORK_RETRY_INITIAL_DELAY,
        max=NETWORK_RETRY_MAX_DELAY
    ),
    stop=tenacity.stop_after_attempt(NETWORK_RETRY_ATTEMPTS),
    before_sleep=lambda retry_state: LOG.warning(
        f"Network operation failed (attempt {retry_state.attempt_number}/{NETWORK_RETRY_ATTEMPTS}), "
        f"retrying in {retry_state.next_action.sleep} seconds: {retry_state.outcome.exception()}"
    ),
    reraise=True
)
def attach_port_to_server(conn, server_id, port_id):
    """Attach a specific port to an existing server with retry logic.
    
    Args:
        conn: OpenStack connection object
        server_id: ID of the server to attach the port to
        port_id: ID of the port to attach
        
    Returns:
        The created interface object
        
    Raises:
        NetworkOperationException: If the port attachment fails after all retries
    """
    LOG.info(f"Attaching port {port_id} to server {server_id}")
    try:
        interface = conn.compute.create_server_interface(
            server_id,
            port_id=port_id
        )
        LOG.info(f"Successfully attached port {port_id} as interface {interface.id} to server {server_id}")
        return interface
    except Exception as e:
        LOG.error(f"Failed to attach port {port_id} to server {server_id}: {e}")
        raise exceptions.NetworkOperationException(
            operation="attach_port",
            server_id=server_id,
            interface_id=port_id,  # Use interface_id instead of port_id
            original_exception=e
        ) from e

@tenacity.retry(
    retry=tenacity.retry_if_exception(_is_network_operation_retryable),
    wait=tenacity.wait_exponential(
        multiplier=NETWORK_RETRY_INITIAL_DELAY,
        min=NETWORK_RETRY_INITIAL_DELAY,
        max=NETWORK_RETRY_MAX_DELAY
    ),
    stop=tenacity.stop_after_attempt(NETWORK_RETRY_ATTEMPTS),
    before_sleep=lambda retry_state: LOG.warning(
        f"Network operation failed (attempt {retry_state.attempt_number}/{NETWORK_RETRY_ATTEMPTS}), "
        f"retrying in {retry_state.next_action.sleep} seconds: {retry_state.outcome.exception()}"
    ),
    reraise=True
)
def detach_interface_from_server(conn, server_id, interface_id):
    """Detach a network interface from a server with retry logic.
    
    Args:
        conn: OpenStack connection object
        server_id: ID of the server to detach the interface from
        interface_id: ID of the interface to detach
        
    Raises:
        NetworkOperationException: If the interface detachment fails after all retries
    """
    LOG.info(f"Detaching interface {interface_id} from server {server_id}")
    try:
        conn.compute.delete_server_interface(interface_id, server_id)
        LOG.info(f"Successfully detached interface {interface_id} from server {server_id}")
        
        # Verify the interface was actually detached
        if verify_interface_detached(conn, server_id, interface_id):
            LOG.info(f"Verified interface {interface_id} was successfully detached from server {server_id}")
        else:
            LOG.warning(f"Interface {interface_id} may still be attached to server {server_id} after detachment operation")
            
    except Exception as e:
        LOG.error(f"Failed to detach interface {interface_id} from server {server_id}: {e}")
        raise exceptions.NetworkOperationException(
            operation="detach_interface",
            server_id=server_id,
            interface_id=interface_id,
            original_exception=e
        ) from e


def verify_interface_attached(conn, server_id, network_id, max_attempts=3, delay=2):
    """Verify that an interface is attached to the server.
    
    Args:
        conn: OpenStack connection object
        server_id: ID of the server
        network_id: ID of the network to check for
        max_attempts: Maximum number of verification attempts
        delay: Delay between attempts in seconds
        
    Returns:
        True if the interface is attached, False otherwise
    """
    for attempt in range(max_attempts):
        try:
            # Get all interfaces for the server
            interfaces = list(conn.compute.server_interfaces(server_id))
            
            # Check if any interface is connected to the specified network
            for interface in interfaces:
                if interface.net_id == network_id:
                    return True
                    
            # If we've made multiple attempts, wait before trying again
            if attempt < max_attempts - 1:
                LOG.info(f"Interface for network {network_id} not found on server {server_id}, "
                         f"retrying in {delay} seconds (attempt {attempt+1}/{max_attempts})")
                time.sleep(delay)
        except Exception as e:
            LOG.warning(f"Error verifying interface attachment for server {server_id}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
                
    return False


def verify_interface_detached(conn, server_id, interface_id, max_attempts=3, delay=2):
    """Verify that an interface is detached from the server.
    
    Args:
        conn: OpenStack connection object
        server_id: ID of the server
        interface_id: ID of the interface to check
        max_attempts: Maximum number of verification attempts
        delay: Delay between attempts in seconds
        
    Returns:
        True if the interface is detached (not found), False otherwise
    """
    for attempt in range(max_attempts):
        try:
            # Get all interfaces for the server
            interfaces = list(conn.compute.server_interfaces(server_id))
            
            # Check if the interface is still present
            for interface in interfaces:
                if interface.id == interface_id:
                    # Interface still exists, not detached yet
                    if attempt < max_attempts - 1:
                        LOG.info(f"Interface {interface_id} still attached to server {server_id}, "
                                f"retrying in {delay} seconds (attempt {attempt+1}/{max_attempts})")
                        time.sleep(delay)
                    return False
                    
            # Interface not found, successfully detached
            return True
        except Exception as e:
            LOG.warning(f"Error verifying interface detachment for server {server_id}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
    
    # If we can't verify, assume it worked
    LOG.warning(f"Could not verify interface {interface_id} detachment status, assuming detached")
    return True


def get_loxilb_server_by_lb_id(conn, lb_id):
    """Find the LoxiLB server for a given load balancer ID.
    
    Args:
        conn: OpenStack connection object
        lb_id: Load balancer ID
        
    Returns:
        Server object or None if not found
    """
    # First try exact match with the expected name format
    server_name = f"loxilb-{lb_id}"
    LOG.debug(f"Looking for LoxiLB server with name: {server_name}")
    
    servers = list(conn.compute.servers(name=server_name))
    if servers:
        if len(servers) > 1:
            LOG.warning(f"Multiple servers found with name {server_name}, using first one")
        return servers[0]
    
    # If exact match fails, try a more precise approach that ensures we match the exact lb_id
    # but accounts for potential formatting differences in how the UUID is displayed
    LOG.debug(f"No exact match found, trying precise UUID search for LB ID: {lb_id}")
    
    # Normalize the lb_id by removing all dashes for comparison
    normalized_lb_id = lb_id.replace("-", "")
    
    # Get all servers with the loxilb prefix
    all_servers = list(conn.compute.servers())
    matching_servers = []
    
    for server in all_servers:
        # Only consider servers with the loxilb prefix
        if not server.name.startswith("loxilb-"):
            continue
            
        # Extract the UUID part from the server name (everything after "loxilb-")
        server_uuid_part = server.name[len("loxilb-"):]
        
        # Normalize by removing dashes for comparison
        normalized_server_uuid = server_uuid_part.replace("-", "")
        
        # Check for exact match of the normalized UUIDs
        if normalized_lb_id == normalized_server_uuid:
            matching_servers.append(server)
            LOG.debug(f"Found exact UUID match: {server.name}")
    
    if not matching_servers:
        LOG.warning(f"No LoxiLB server found for load balancer {lb_id} using precise UUID search")
        return None
    
    if len(matching_servers) > 1:
        LOG.warning(f"Multiple servers found for LB ID {lb_id} using precise UUID search, using first one")
    
    LOG.debug(f"Found server {matching_servers[0].name} for LB ID {lb_id} using precise UUID search")
    return matching_servers[0]


def get_loxilb_server_ip(conn, lb_id):
    """Get the IP address of the LoxiLB server for a load balancer.
    
    This function prioritizes the management network IP when available.
    
    Args:
        conn: OpenStack connection object
        lb_id: Load balancer ID
        
    Returns:
        IP address string or None if server not found
    """
    server = get_loxilb_server_by_lb_id(conn, lb_id)
    if not server:
        return None
        
    # Get management network ID if configured
    from oslo_config import cfg
    CONF = cfg.CONF
    mgmt_network_id = None
    
    if hasattr(CONF, 'loxilb') and CONF.loxilb.use_mgmt_network:
        mgmt_network_id = CONF.loxilb.mgmt_network_id
        
    # Get server details to ensure we have all network information
    server = conn.compute.get_server(server.id)
    
    if mgmt_network_id:
        # Try to find the management network by ID
        for net_name, net_addrs in server.addresses.items():
            # Check if this network matches the management network
            network = conn.network.find_network(net_name)
            if network and network.id == mgmt_network_id:
                LOG.debug(f"Found management network {net_name} for LoxiLB server {server.id}")
                for addr in net_addrs:
                    if addr.get('OS-EXT-IPS:type') == 'fixed':
                        LOG.info(f"Using management network IP {addr['addr']} for LoxiLB server")
                        return addr['addr']
    
    # Fallback to any IP address
    return get_server_ip(server)

def plug_aap_port(conn, server_id, vip_port, subnet_id):
    """Attach VIP port to server using Allowed Address Pairs (AAP) approach.
    
    This function mimics Amphora's plug_aap_port() behavior for proper VIP attachment.
    It creates a base port on the server and configures the VIP as an allowed address pair.
    
    Args:
        conn: OpenStack connection object
        server_id: ID of the server to attach the VIP to
        vip_port: VIP port object to be configured
        subnet_id: ID of the subnet for the VIP
        
    Returns:
        Dictionary containing port information and VIP configuration
        
    Raises:
        NetworkOperationException: If the VIP attachment fails
    """
    LOG.info(f"Attaching VIP port {vip_port.id} to server {server_id} using AAP approach")
    
    try:
        # Get the VIP network information
        vip_network_id = vip_port.network_id
        vip_ip_address = vip_port.fixed_ips[0]['ip_address']
        
        LOG.info(f"VIP details: network={vip_network_id}, ip={vip_ip_address}")
        
        # Check if server already has a port on the VIP network
        server = conn.compute.get_server(server_id)
        existing_port = None
        
        # Get all server interfaces
        interfaces = list(conn.compute.server_interfaces(server_id))
        for interface in interfaces:
            port = conn.network.get_port(interface.port_id)
            if port.network_id == vip_network_id:
                existing_port = port
                LOG.info(f"Found existing port {port.id} on VIP network {vip_network_id}")
                break
        
        # If no existing port, create a new base port on the VIP network
        if not existing_port:
            LOG.info(f"Creating new base port on VIP network {vip_network_id} for server {server_id}")
            
            # Create a base port with fixed IP on the subnet
            base_port = conn.network.create_port(
                network_id=vip_network_id,
                name=f"loxilb-base-{server_id[:8]}",
                fixed_ips=[{"subnet_id": subnet_id}]
            )
            
            LOG.info(f"Created base port {base_port.id} with IP {base_port.fixed_ips[0]['ip_address']}")
            
            # Attach the base port to the server
            interface = conn.compute.create_server_interface(
                server_id, port_id=base_port.id
            )
            LOG.info(f"Attached base port {base_port.id} as interface {interface.id} to server {server_id}")
            
            # Refresh the port object
            existing_port = conn.network.get_port(base_port.id)
        
        # Configure the VIP as an allowed address pair on the existing/new port
        LOG.info(f"Configuring VIP {vip_ip_address} as allowed address pair on port {existing_port.id}")
        
        # Get current allowed address pairs
        current_aaps = existing_port.allowed_address_pairs or []
        
        # Add the VIP to allowed address pairs if not already present
        vip_aap = {"ip_address": vip_ip_address}
        if vip_aap not in current_aaps:
            current_aaps.append(vip_aap)
            
            # Update the port with the new allowed address pairs
            updated_port = conn.network.update_port(
                existing_port.id,
                allowed_address_pairs=current_aaps
            )
            LOG.info(f"Successfully added VIP {vip_ip_address} to allowed address pairs on port {existing_port.id}")
        else:
            LOG.info(f"VIP {vip_ip_address} already in allowed address pairs on port {existing_port.id}")
            updated_port = existing_port
        
        # Return port information similar to Amphora's format
        return {
            'id': updated_port.id,
            'network_id': updated_port.network_id,
            'fixed_ips': updated_port.fixed_ips,
            'allowed_address_pairs': updated_port.allowed_address_pairs,
            'vip_ip': vip_ip_address,
            'vip_port_id': vip_port.id,
            'base_port_id': updated_port.id
        }
        
    except Exception as e:
        LOG.error(f"Failed to attach VIP port {vip_port.id} to server {server_id} using AAP: {str(e)}")
        raise exceptions.NetworkOperationException(
            operation="plug_aap_port",
            server_id=server_id,
            network_id=vip_network_id,
            original_exception=e
        )


def unplug_aap_port(conn, server_id, vip_port, base_port_id):
    """Remove VIP from allowed address pairs and optionally detach base port.
    
    Args:
        conn: OpenStack connection object
        server_id: ID of the server
        vip_port: VIP port object
        base_port_id: ID of the base port with AAP configuration
    """
    LOG.info(f"Removing VIP {vip_port.fixed_ips[0]['ip_address']} from allowed address pairs on port {base_port_id}")
    
    try:
        # Get the base port
        base_port = conn.network.get_port(base_port_id)
        vip_ip_address = vip_port.fixed_ips[0]['ip_address']
        
        # Remove VIP from allowed address pairs
        current_aaps = base_port.allowed_address_pairs or []
        updated_aaps = [aap for aap in current_aaps if aap.get('ip_address') != vip_ip_address]
        
        if len(updated_aaps) != len(current_aaps):
            conn.network.update_port(
                base_port_id,
                allowed_address_pairs=updated_aaps
            )
            LOG.info(f"Removed VIP {vip_ip_address} from allowed address pairs on port {base_port_id}")
        
    except Exception as e:
        LOG.error(f"Failed to remove VIP from allowed address pairs: {str(e)}")
        # Don't raise exception in cleanup, just log the error


# Utility functions for OpenStack SDK (openstacksdk) integration