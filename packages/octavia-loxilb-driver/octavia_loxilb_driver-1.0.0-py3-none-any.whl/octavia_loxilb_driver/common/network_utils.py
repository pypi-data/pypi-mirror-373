"""Network utilities for LoxiLB Octavia Driver."""

import logging
import requests
import socket
import time
from oslo_config import cfg

from octavia_loxilb_driver.common import exceptions

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

def check_port_connectivity(ip_address, port, timeout=5, max_retries=3, retry_interval=2):
    """Check TCP connectivity to a specific port.
    
    Args:
        ip_address: IP address to check
        port: Port number to check
        timeout: Connection timeout in seconds
        max_retries: Maximum number of retries
        retry_interval: Interval between retries in seconds
        
    Returns:
        True if connection successful, False otherwise
    """
    LOG.info(f"Checking connectivity to {ip_address}:{port}")
    
    for attempt in range(max_retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip_address, port))
            sock.close()
            
            if result == 0:
                LOG.info(f"Successfully connected to {ip_address}:{port}")
                return True
            else:
                LOG.warning(f"Failed to connect to {ip_address}:{port} (attempt {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
        except Exception as e:
            LOG.warning(f"Error checking connectivity to {ip_address}:{port}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
    
    LOG.error(f"Failed to establish connectivity to {ip_address}:{port} after {max_retries} attempts")
    return False


def verify_interface_operational(conn, server_id, network_id, port=22, timeout=5, max_retries=3):
    """Verify that a network interface is operational by checking connectivity.
    
    Args:
        conn: OpenStack connection object
        server_id: ID of the server
        network_id: ID of the network to check
        port: Port to check for connectivity (default: 22 for SSH)
        timeout: Connection timeout in seconds
        max_retries: Maximum number of retries
        
    Returns:
        True if the interface is operational, False otherwise
    """
    try:
        # Get the server details
        server = conn.compute.get_server(server_id)
        if not server:
            LOG.warning(f"Server {server_id} not found")
            return False
            
        # Find the IP address for the specified network
        for network_name, addresses in server.addresses.items():
            # Check if this is the network we're looking for
            network = conn.network.find_network(network_name)
            if network and network.id == network_id:
                # Use the first IP address in this network
                if addresses and len(addresses) > 0:
                    ip_address = addresses[0]['addr']
                    LOG.info(f"Found IP address {ip_address} for server {server_id} on network {network_id}")
                    
                    # Check connectivity to the IP address
                    return check_port_connectivity(ip_address, port, timeout, max_retries)
        
        LOG.warning(f"No IP address found for server {server_id} on network {network_id}")
        return False
    except Exception as e:
        LOG.error(f"Error verifying interface operational status: {e}")
        return False


def verify_loxilb_api_accessible(ip_address, port=8080, timeout=5, max_retries=3, retry_interval=2):
    """Verify that the LoxiLB API is accessible through an interface.
    
    Args:
        ip_address: IP address of the LoxiLB server
        port: LoxiLB API port (default: 8080)
        timeout: Connection timeout in seconds
        max_retries: Maximum number of retries
        retry_interval: Interval between retries in seconds
        
    Returns:
        True if the LoxiLB API is accessible, False otherwise
    """
    LOG.info(f"Verifying LoxiLB API accessibility at {ip_address}:{port}")
    
    endpoint = f"http://{ip_address}:{port}/loxilb/v1/config/lb"
    headers = {'Content-Type': 'application/json'}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(endpoint, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                LOG.info(f"Successfully accessed LoxiLB API at {endpoint}")
                return True
            else:
                LOG.warning(f"LoxiLB API returned status code {response.status_code} at {endpoint} "
                           f"(attempt {attempt+1}/{max_retries})")
        except requests.exceptions.RequestException as e:
            LOG.warning(f"Error accessing LoxiLB API at {endpoint}: {e} (attempt {attempt+1}/{max_retries})")
        
        if attempt < max_retries - 1:
            time.sleep(retry_interval)
    
    LOG.error(f"Failed to access LoxiLB API at {endpoint} after {max_retries} attempts")
    return False


def verify_loxilb_interface_operational(conn, server_id, network_id, lb_id=None, 
                                       api_port=8080, timeout=5, max_retries=3):
    """Verify that a LoxiLB interface is operational by checking API accessibility.
    
    Args:
        conn: OpenStack connection object
        server_id: ID of the server
        network_id: ID of the network to check
        lb_id: Load balancer ID (for logging purposes)
        api_port: LoxiLB API port
        timeout: Connection timeout in seconds
        max_retries: Maximum number of retries
        
    Returns:
        True if the interface is operational and LoxiLB API is accessible, False otherwise
    """
    try:
        # Get the server details
        server = conn.compute.get_server(server_id)
        if not server:
            LOG.warning(f"Server {server_id} not found")
            return False
            
        # Find the IP address for the specified network
        for network_name, addresses in server.addresses.items():
            # Check if this is the network we're looking for
            network = conn.network.find_network(network_name)
            if network and network.id == network_id:
                # Use the first IP address in this network
                if addresses and len(addresses) > 0:
                    ip_address = addresses[0]['addr']
                    LOG.info(f"Found IP address {ip_address} for LoxiLB server {server_id} "
                           f"on network {network_id} for load balancer {lb_id or 'unknown'}")
                    
                    # Check LoxiLB API accessibility
                    return verify_loxilb_api_accessible(ip_address, api_port, timeout, max_retries)
        
        LOG.warning(f"No IP address found for LoxiLB server {server_id} on network {network_id}")
        return False
    except Exception as e:
        LOG.error(f"Error verifying LoxiLB interface operational status: {e}")
        return False
