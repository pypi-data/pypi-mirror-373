"""LoxiLB network configuration utilities using LoxiLB API."""

import logging
import time
import requests
from oslo_config import cfg

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

class LoxiLBNetworkConfigurator:
    """Configure network interfaces on LoxiLB using its REST API."""
    
    def __init__(self, loxilb_ip, api_port=8080):
        """Initialize the configurator.
        
        Args:
            loxilb_ip: IP address of the LoxiLB instance
            api_port: Port for LoxiLB API (default: 8080)
        """
        self.loxilb_ip = loxilb_ip
        self.api_port = api_port
        self.base_url = f"http://{loxilb_ip}:{api_port}/netlox/v1"
        
    def get_all_ports(self):
        """Get all port interfaces from LoxiLB.
        
        Returns:
            list: List of port entries with interface names and MAC addresses
        """
        try:
            url = f"{self.base_url}/config/port/all"
            LOG.info(f"Getting all ports from LoxiLB: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            ports = data.get('portAttr', [])
            
            LOG.info(f"Retrieved {len(ports)} ports from LoxiLB")
            for port in ports:
                LOG.debug(f"Port: {port.get('portName')} - MAC: {port.get('portHardwareInformation', {}).get('macAddress')}")
            
            return ports
            
        except Exception as e:
            LOG.error(f"Failed to get ports from LoxiLB {self.loxilb_ip}: {e}")
            return []
    
    def find_interface_by_mac(self, target_mac):
        """Find interface name by MAC address.
        
        Args:
            target_mac: MAC address to search for
            
        Returns:
            str: Interface name if found, None otherwise
        """
        try:
            # Normalize MAC address format (remove colons, convert to lowercase)
            target_mac_normalized = target_mac.replace(':', '').lower()
            
            ports = self.get_all_ports()
            
            # Collect all matching interfaces (there might be multiple with same MAC)
            matching_interfaces = []
            
            for port in ports:
                port_hw_info = port.get('portHardwareInformation', {})
                port_mac = port_hw_info.get('macAddress', '')
                
                if port_mac:
                    # Normalize port MAC address
                    port_mac_normalized = port_mac.replace(':', '').lower()
                    
                    if port_mac_normalized == target_mac_normalized:
                        interface_name = port.get('portName')
                        
                        # Skip eth0 interfaces as they are typically legacy/virtual
                        if interface_name == 'eth0':
                            LOG.debug(f"Skipping eth0 interface for MAC {target_mac} (legacy interface)")
                            continue
                            
                        matching_interfaces.append(interface_name)
                        LOG.debug(f"Found matching interface {interface_name} for MAC {target_mac}")
            
            if matching_interfaces:
                # Return the last matching interface (most recently attached)
                selected_interface = matching_interfaces[-1]
                LOG.info(f"Selected interface {selected_interface} for MAC {target_mac} (from {len(matching_interfaces)} matches: {matching_interfaces})")
                return selected_interface
            else:
                LOG.warning(f"No interface found for MAC address {target_mac}")
                return None
            
        except Exception as e:
            LOG.error(f"Error finding interface by MAC {target_mac}: {e}")
            return None
    
    def configure_ip_address(self, interface_name, ip_address, subnet_mask):
        """Configure IP address on an interface using LoxiLB API.
        
        Args:
            interface_name: Name of the interface (e.g., "ens8")
            ip_address: IP address to assign
            subnet_mask: Subnet mask (e.g., "24" or "255.255.255.0")
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert subnet mask to CIDR notation if needed
            if '.' in subnet_mask:
                # Convert dotted decimal to CIDR
                cidr = self._netmask_to_cidr(subnet_mask)
            else:
                cidr = int(subnet_mask)
            
            url = f"{self.base_url}/config/ipv4address"
            
            payload = {
                "dev": interface_name,
                "ipAddress": f"{ip_address}/{cidr}"
            }
            
            LOG.info(f"Configuring IP {ip_address}/{cidr} on interface {interface_name}")
            LOG.debug(f"POST {url} with payload: {payload}")
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                LOG.info(f"Successfully configured IP {ip_address}/{cidr} on {interface_name}")
                return True
            else:
                LOG.error(f"Failed to configure IP address. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            LOG.error(f"Error configuring IP {ip_address} on {interface_name}: {e}")
            return False
    
    def remove_ip_address(self, interface_name, ip_address, subnet_mask):
        """Remove IP address from an interface using LoxiLB API.
        
        Args:
            interface_name: Name of the interface
            ip_address: IP address to remove
            subnet_mask: Subnet mask
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert subnet mask to CIDR notation if needed
            if '.' in subnet_mask:
                cidr = self._netmask_to_cidr(subnet_mask)
            else:
                cidr = int(subnet_mask)
            
            url = f"{self.base_url}/config/ipv4address/{ip_address}/{cidr}/dev/{interface_name}"
            
            LOG.info(f"Removing IP {ip_address}/{cidr} from interface {interface_name}")
            
            response = requests.delete(url, timeout=10)
            
            if response.status_code == 200:
                LOG.info(f"Successfully removed IP {ip_address}/{cidr} from {interface_name}")
                return True
            else:
                LOG.error(f"Failed to remove IP address. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            LOG.error(f"Error removing IP {ip_address} from {interface_name}: {e}")
            return False
    
    def get_interface_ip_addresses(self, interface_name=None):
        """Get IP addresses configured on interfaces.
        
        Args:
            interface_name: Specific interface to query (optional)
            
        Returns:
            dict: Interface name to IP addresses mapping
        """
        try:
            url = f"{self.base_url}/config/ipv4address"
            if interface_name:
                url += f"/{interface_name}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            ip_attrs = data.get('ipAttr', [])
            
            result = {}
            for ip_attr in ip_attrs:
                dev = ip_attr.get('dev')
                ip_address = ip_attr.get('ipAddress')
                mask = ip_attr.get('mask')
                
                if dev not in result:
                    result[dev] = []
                result[dev].append(f"{ip_address}/{mask}")
            
            return result
            
        except Exception as e:
            LOG.error(f"Error getting IP addresses: {e}")
            return {}
    
    def wait_for_interface_discovery(self, target_mac, max_attempts=10, delay=5):
        """Wait for a new interface to be discovered by LoxiLB.
        
        Args:
            target_mac: MAC address of the interface to wait for
            max_attempts: Maximum number of attempts
            delay: Delay between attempts in seconds
            
        Returns:
            str: Interface name if found, None if timeout
        """
        LOG.info(f"Waiting for interface with MAC {target_mac} to be discovered")
        
        for attempt in range(max_attempts):
            interface_name = self.find_interface_by_mac(target_mac)
            if interface_name:
                LOG.info(f"Interface {interface_name} discovered after {attempt + 1} attempts")
                return interface_name
            
            LOG.debug(f"Interface not yet discovered (attempt {attempt + 1}/{max_attempts})")
            if attempt < max_attempts - 1:
                time.sleep(delay)
        
        LOG.warning(f"Interface with MAC {target_mac} was not discovered after {max_attempts} attempts")
        return None
    
    def configure_interface_from_port(self, openstack_port, subnet_info):
        """Configure interface from OpenStack port information.
        
        Args:
            openstack_port: OpenStack port object with MAC address and fixed IPs
            subnet_info: Subnet information with CIDR
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get MAC address from port
            mac_address = openstack_port.mac_address
            LOG.info(f"Configuring interface for port {openstack_port.id} with MAC {mac_address}")
            
            # Wait for interface to be discovered
            interface_name = self.wait_for_interface_discovery(mac_address)
            if not interface_name:
                LOG.error(f"Interface with MAC {mac_address} was not discovered")
                return False
            
            # Get IP address from port's fixed IPs
            if not openstack_port.fixed_ips:
                LOG.error(f"Port {openstack_port.id} has no fixed IPs")
                return False
            
            ip_address = openstack_port.fixed_ips[0]['ip_address']
            
            # Extract subnet mask from subnet info
            subnet_cidr = subnet_info.cidr  # e.g., "172.16.2.0/24"
            subnet_mask = subnet_cidr.split('/')[1]  # e.g., "24"
            
            # Configure the IP address
            success = self.configure_ip_address(interface_name, ip_address, subnet_mask)
            
            if success:
                LOG.info(f"Successfully configured {ip_address}/{subnet_mask} on {interface_name}")
            else:
                LOG.error(f"Failed to configure {ip_address}/{subnet_mask} on {interface_name}")
            
            return success
            
        except Exception as e:
            LOG.error(f"Error configuring interface from port {openstack_port.id}: {e}")
            return False
    
    def _netmask_to_cidr(self, netmask):
        """Convert dotted decimal netmask to CIDR notation.
        
        Args:
            netmask: Dotted decimal netmask (e.g., "255.255.255.0")
            
        Returns:
            int: CIDR notation (e.g., 24)
        """
        try:
            # Convert netmask to binary and count 1s
            octets = netmask.split('.')
            binary = ''.join([bin(int(octet))[2:].zfill(8) for octet in octets])
            return binary.count('1')
        except:
            # Default to /24 if conversion fails
            return 24


def configure_loxilb_interface(loxilb_ip, openstack_port, subnet_info, api_port=11111):
    """Convenience function to configure a LoxiLB interface.
    
    Args:
        loxilb_ip: IP address of the LoxiLB instance
        openstack_port: OpenStack port object
        subnet_info: Subnet information
        api_port: LoxiLB API port (default: 11111)
        
    Returns:
        bool: True if successful, False otherwise
    """
    configurator = LoxiLBNetworkConfigurator(loxilb_ip, api_port)
    return configurator.configure_interface_from_port(openstack_port, subnet_info)
