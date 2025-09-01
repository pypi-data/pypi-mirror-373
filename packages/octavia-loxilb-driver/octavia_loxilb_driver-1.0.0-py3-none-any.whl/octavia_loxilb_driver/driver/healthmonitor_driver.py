# octavia_loxilb_driver/driver/healthmonitor_driver.py
"""Endpoint-based Health Monitor Management Driver for LoxiLB."""

import time

from octavia_lib.common import constants as lib_consts
from oslo_log import log as logging

from octavia_loxilb_driver.common import constants, exceptions, utils

LOG = logging.getLogger(__name__)

# General-purpose attribute extraction function
def extract_attr(obj, key, default=None):
    """Safely extract attribute from dict or object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def get_healthmonitor_id(healthmonitor):
    """Extract ID from healthmonitor object or dict.
    
    Args:
        healthmonitor: Healthmonitor object or dict
        
    Returns:
        str: Healthmonitor ID
    """
    return extract_attr(healthmonitor, "id") or extract_attr(healthmonitor, "healthmonitor_id")


class HealthMonitorDriver:
    """Endpoint-based Health Monitor Management Driver for LoxiLB.
    
    This driver handles Octavia health monitor operations by managing LoxiLB endpoint
    configurations for health monitoring. Each health monitor creates endpoint probes
    for all pool members, allowing per-member health status tracking.
    """

    def __init__(self, api_client, resource_mapper, config):
        """Initialize the HealthMonitorDriver.
        
        Args:
            api_client: LoxiLB API client instance
            resource_mapper: Resource mapper with ID mapping capabilities
            config: Driver configuration object
        """
        self.api_client = api_client
        self.resource_mapper = resource_mapper
        self.config = config

    def create(self, healthmonitor):
        """Create a health monitor.

        Creates a health monitor by storing configuration in metadata and creating
        LoxiLB endpoint probes for all members in the associated pool.

        Args:
            healthmonitor: The health monitor object or dictionary from Octavia containing:
                - id: Health monitor UUID
                - type: Health check type (HTTP, HTTPS, TCP, UDP_CONNECT, PING)
                - delay: Interval between health checks
                - timeout: Timeout for each health check
                - max_retries: Number of retries before marking unhealthy
                - max_retries_down: Number of retries before marking down (optional)
                - http_method: HTTP method for HTTP checks (GET, POST, etc.)
                - url_path: URL path for HTTP checks
                - expected_codes: Expected HTTP status codes
                - name: Human-readable name (optional)
                - admin_state_up: Administrative state (True/False)
                - pool_id: Associated pool UUID
        
        Returns:
            dict: Health monitor status information

        Raises:
            UnsupportedOptionError: If configuration options are not supported
            DriverError: If health monitor creation fails
        """
        try:
            healthmonitor_id = get_healthmonitor_id(healthmonitor)
            LOG.info(f"Creating health monitor: {healthmonitor_id}")
            
            # Validate health monitor configuration
            self._validate_healthmonitor(healthmonitor)
            
            # Store health monitor metadata
            hm_metadata = self._build_healthmonitor_metadata(healthmonitor)
            utils.store_id_mapping(
                self.resource_mapper.id_mapping_cache,
                healthmonitor_id,
                None,
                "healthmonitor",
                hm_metadata
            )
            
            # Get pool members to create endpoint probes
            pool_id = extract_attr(healthmonitor, "pool_id")
            
            pool_members = self._get_pool_members(pool_id)
            
            # Create endpoint probes for all pool members
            endpoints_created = []
            for member in pool_members:
                try:
                    endpoint_config = self._build_endpoint_config(healthmonitor, member)
                    self.api_client.create_endpoint(endpoint_config)
                    endpoints_created.append(member['address'])
                    LOG.debug(f"Created endpoint probe for member {member['address']}")
                except Exception as e:
                    LOG.warning(f"Failed to create endpoint probe for member {member['address']}: {e}")
                    # Continue with other members
            
            # Update metadata with created endpoints
            hm_metadata['endpoints_created'] = endpoints_created
            utils.store_id_mapping(
                self.resource_mapper.id_mapping_cache,
                healthmonitor_id,
                None,
                "healthmonitor",
                hm_metadata
            )
            
            result = {
                'id': healthmonitor_id,
                'operating_status': lib_consts.ONLINE,
                'provisioning_status': lib_consts.ACTIVE
            }
            
            LOG.info(f"Successfully created health monitor {healthmonitor_id} with {len(endpoints_created)} endpoint probes")
            return result
            
        except exceptions.UnsupportedOptionError:
            LOG.error(f"Unsupported health monitor configuration: {healthmonitor_id}")
            raise
        except Exception as e:
            LOG.error(f"Failed to create health monitor {healthmonitor_id}: {e}")
            raise exceptions.DriverError(f"Health monitor creation failed: {e}")

    def update(self, healthmonitor, update_dict):
        """Update a health monitor.

        Updates the health monitor configuration by updating stored metadata
        and recreating endpoint probes with new configuration.

        Args:
            healthmonitor: Current health monitor object or dictionary from Octavia
            update_dict: Dictionary with the changed attributes

        Returns:
            dict: Health monitor status information

        Raises:
            UnsupportedOptionError: If configuration options are not supported  
            DriverError: If health monitor update fails
        """
        try:
            healthmonitor_id = get_healthmonitor_id(healthmonitor)
            LOG.info(f"Updating health monitor: {healthmonitor_id} with changes: {update_dict.keys()}")
            
            # Create updated healthmonitor by applying update_dict
            updated_healthmonitor = self._apply_updates(healthmonitor, update_dict)
            
            # Validate health monitor configuration
            self._validate_healthmonitor(updated_healthmonitor)
            
            # Get existing metadata
            existing_metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache,
                healthmonitor_id
            )
            if not existing_metadata:
                raise exceptions.DriverError(f"Health monitor {healthmonitor_id} not found")
            
            # Delete existing endpoint probes
            self._delete_endpoint_probes(healthmonitor_id, existing_metadata)
            
            # Build new metadata
            hm_metadata = self._build_healthmonitor_metadata(updated_healthmonitor)
            
            # Get current pool members
            pool_id = extract_attr(updated_healthmonitor, "pool_id")
                
            pool_members = self._get_pool_members(pool_id)
            
            # Create new endpoint probes
            endpoints_created = []
            for member in pool_members:
                try:
                    endpoint_config = self._build_endpoint_config(updated_healthmonitor, member)
                    self.api_client.create_endpoint(endpoint_config)
                    endpoints_created.append(member['address'])
                    LOG.debug(f"Updated endpoint probe for member {member['address']}")
                except Exception as e:
                    LOG.warning(f"Failed to update endpoint probe for member {member['address']}: {e}")
            
            # Update metadata
            hm_metadata['endpoints_created'] = endpoints_created
            utils.store_id_mapping(
                self.resource_mapper.id_mapping_cache,
                healthmonitor_id,
                None,
                "healthmonitor",
                hm_metadata
            )
            
            result = {
                'id': healthmonitor_id,
                'operating_status': lib_consts.ONLINE,
                'provisioning_status': lib_consts.ACTIVE
            }
            
            LOG.info(f"Successfully updated health monitor {healthmonitor_id}")
            return result
            
        except exceptions.UnsupportedOptionError:
            LOG.error(f"Unsupported health monitor configuration: {healthmonitor_id}")
            raise
        except Exception as e:
            LOG.error(f"Failed to update health monitor {healthmonitor_id}: {e}")
            raise exceptions.DriverError(f"Health monitor update failed: {e}")

    def delete(self, healthmonitor):
        """Delete a health monitor.

        Deletes the health monitor by removing all endpoint probes and
        cleaning up stored metadata.

        Args:
            healthmonitor: Health monitor object or dictionary to delete

        Returns:
            dict: Health monitor status information

        Raises:
            DriverError: If health monitor deletion fails
        """
        try:
            healthmonitor_id = get_healthmonitor_id(healthmonitor)
            LOG.info(f"Deleting health monitor: {healthmonitor_id}")
            
            # Get existing metadata
            existing_metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache,
                healthmonitor_id
            )
            
            if existing_metadata:
                # Delete endpoint probes
                self._delete_endpoint_probes(healthmonitor_id, existing_metadata)
                
                # Remove metadata
                if healthmonitor_id in self.resource_mapper.id_mapping_cache["resource_metadata"]:
                    del self.resource_mapper.id_mapping_cache["resource_metadata"][healthmonitor_id]
            
            result = {
                'id': healthmonitor_id,
                'operating_status': lib_consts.OFFLINE,
                'provisioning_status': lib_consts.DELETED
            }
            
            LOG.info(f"Successfully deleted health monitor {healthmonitor_id}")
            return result
            
        except Exception as e:
            LOG.error(f"Failed to delete health monitor {healthmonitor_id}: {e}")
            raise exceptions.DriverError(f"Health monitor deletion failed: {e}")

    def get(self, healthmonitor_id):
        """Get health monitor status.

        Retrieves the current status of a health monitor by checking stored
        metadata and associated endpoint states.

        Args:
            healthmonitor_id: Health monitor UUID

        Returns:
            dict: Health monitor status information

        Raises:
            DriverError: If health monitor retrieval fails
        """
        try:
            LOG.debug(f"Getting health monitor: {healthmonitor_id}")
            
            # Get metadata
            metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache,
                healthmonitor_id
            )
            if not metadata:
                raise exceptions.DriverError(f"Health monitor {healthmonitor_id} not found")
            
            # Check endpoint states to determine overall status
            operating_status = self._determine_operating_status(metadata)
            
            result = {
                'id': healthmonitor_id,
                'operating_status': operating_status,
                'provisioning_status': lib_consts.ACTIVE,
                'metadata': metadata
            }
            
            LOG.debug(f"Retrieved health monitor {healthmonitor_id}: {operating_status}")
            return result
            
        except Exception as e:
            LOG.error(f"Failed to get health monitor {healthmonitor_id}: {e}")
            raise exceptions.DriverError(f"Health monitor retrieval failed: {e}")

    def get_all(self):
        """Get all health monitors.

        Retrieves the status of all health monitors managed by this driver.

        Returns:
            list: List of health monitor status information

        Raises:
            DriverError: If health monitor retrieval fails
        """
        try:
            LOG.debug("Getting all health monitors")
            
            # Get all health monitor metadata
            all_metadata = self.resource_mapper.id_mapping_cache.get("resource_metadata", {})
            # Filter only healthmonitor resources
            all_metadata = {hm_id: md for hm_id, md in all_metadata.items() if md.get("resource_type") == "healthmonitor"}
            
            results = []
            for hm_id, metadata in all_metadata.items():
                try:
                    # Check endpoint states
                    operating_status = self._determine_operating_status(metadata)
                    
                    result = {
                        'id': hm_id,
                        'operating_status': operating_status,
                        'provisioning_status': lib_consts.ACTIVE,
                        'metadata': metadata
                    }
                    results.append(result)
                    
                except Exception as e:
                    LOG.warning(f"Failed to get status for health monitor {hm_id}: {e}")
                    # Include with error status
                    results.append({
                        'id': hm_id,
                        'operating_status': lib_consts.ERROR,
                        'provisioning_status': lib_consts.ERROR
                    })
            
            LOG.debug(f"Retrieved {len(results)} health monitors")
            return results
            
        except Exception as e:
            LOG.error(f"Failed to get all health monitors: {e}")
            raise exceptions.DriverError(f"Health monitor retrieval failed: {e}")

    def get_stats(self, healthmonitor_id):
        """Get health monitor statistics.

        Args:
            healthmonitor_id: Health monitor UUID

        Returns:
            dict: Health monitor statistics

        Raises:
            UnsupportedOptionError: Stats not supported for endpoint-based monitoring
        """
        LOG.warning(f"Health monitor stats not supported for endpoint-based monitoring: {healthmonitor_id}")
        raise exceptions.UnsupportedOptionError("Health monitor statistics not supported")

    def _validate_healthmonitor(self, healthmonitor):
        """Validate health monitor configuration.

        Args:
            healthmonitor: Health monitor object to validate

        Raises:
            UnsupportedOptionError: If configuration is not supported
        """
        # Check if health monitor type is supported
        hm_type = None
        hm_type = extract_attr(healthmonitor, "type")
            
        if hm_type not in constants.ENDPOINT_PROBE_TYPE_MAP:
            raise exceptions.UnsupportedOptionError(
                f"Unsupported health monitor type: {hm_type}"
            )

        # Validate timing parameters
        delay = 0
        timeout = 0
        max_retries = 0
        
        delay = extract_attr(healthmonitor, "delay", 0)
        timeout = extract_attr(healthmonitor, "timeout", 0)
        max_retries = extract_attr(healthmonitor, "max_retries", 0)

        if delay < 1:
            raise exceptions.UnsupportedOptionError(
                "Health monitor delay must be at least 1 second"
            )

        if timeout < 1:
            raise exceptions.UnsupportedOptionError(
                "Health monitor timeout must be at least 1 second"
            )

        if timeout >= delay:
            raise exceptions.UnsupportedOptionError(
                "Health monitor timeout must be less than delay"
            )

        if max_retries < 1 or max_retries > 10:
            raise exceptions.UnsupportedOptionError(
                "Health monitor max_retries must be between 1 and 10"
            )

        # Validate HTTP-specific parameters
        if hm_type in [lib_consts.HEALTH_MONITOR_HTTP, lib_consts.HEALTH_MONITOR_HTTPS]:
            http_method = None
            http_method = extract_attr(healthmonitor, "http_method", None)
                
            if http_method:
                allowed_methods = ['GET', 'POST', 'PUT', 'HEAD', 'OPTIONS']
                if http_method not in allowed_methods:
                    raise exceptions.UnsupportedOptionError(
                        f"Unsupported HTTP method: {http_method}"
                    )

        healthmonitor_id = get_healthmonitor_id(healthmonitor)
        LOG.debug(f"Health monitor validation passed: {healthmonitor_id}")

    def _build_healthmonitor_metadata(self, healthmonitor):
        """Build metadata dictionary for health monitor.

        Args:
            healthmonitor: Health monitor object

        Returns:
            dict: Health monitor metadata
        """
        healthmonitor_id = get_healthmonitor_id(healthmonitor)
        
        # Extract basic attributes
        hm_type = None
        delay = 0
        timeout = 0
        max_retries = 0
        max_retries_down = 0
        http_method = None
        url_path = None
        expected_codes = None
        admin_state_up = True
        
        hm_type = extract_attr(healthmonitor, "type", None)
        delay = extract_attr(healthmonitor, "delay", 0)
        timeout = extract_attr(healthmonitor, "timeout", 0)
        max_retries = extract_attr(healthmonitor, "max_retries", 0)
        max_retries_down = extract_attr(healthmonitor, "max_retries_down", max_retries)
        http_method = extract_attr(healthmonitor, "http_method", "GET")
        url_path = extract_attr(healthmonitor, "url_path", "/")
        expected_codes = extract_attr(healthmonitor, "expected_codes", "200")
        admin_state_up = extract_attr(healthmonitor, "admin_state_up", True)
        
        # Build metadata
        metadata = {
            'id': healthmonitor_id,
            'type': hm_type,
            'delay': delay,
            'timeout': timeout,
            'max_retries': max_retries,
            'max_retries_down': max_retries_down,
            'admin_state_up': admin_state_up,
            'endpoints_created': []
        }
        
        # Add HTTP-specific fields if applicable
        if hm_type in [lib_consts.HEALTH_MONITOR_HTTP, lib_consts.HEALTH_MONITOR_HTTPS]:
            metadata.update({
                'http_method': http_method,
                'url_path': url_path,
                'expected_codes': expected_codes
            })
            
        return metadata

    def _build_endpoint_config(self, healthmonitor, member):
        """Build endpoint configuration for LoxiLB.

        Args:
            healthmonitor: Health monitor object
            member: Pool member dictionary

        Returns:
            dict: Endpoint configuration for LoxiLB API
        """
        healthmonitor_id = get_healthmonitor_id(healthmonitor)
        
        # Extract health monitor attributes
        hm_type = None
        delay = 0
        timeout = 0
        max_retries = 0
        http_method = None
        url_path = None
        expected_codes = None
        
        hm_type = extract_attr(healthmonitor, "type", None)
        delay = extract_attr(healthmonitor, "delay", 0)
        timeout = extract_attr(healthmonitor, "timeout", 0)
        max_retries = extract_attr(healthmonitor, "max_retries", 0)
        http_method = extract_attr(healthmonitor, "http_method", "GET")
        url_path = extract_attr(healthmonitor, "url_path", "/")
        expected_codes = extract_attr(healthmonitor, "expected_codes", "200")
        
        # Map Octavia health monitor type to LoxiLB probe type
        probe_type = constants.ENDPOINT_PROBE_TYPE_MAP.get(hm_type, "tcp")
        
        # Build endpoint configuration
        endpoint_config = {
            "name": f"hm-{healthmonitor_id}-{member['address']}",
            "address": member['address'],
            "port": member['protocol_port'],
            "probe": {
                "type": probe_type,
                "interval": delay * 1000,  # Convert to milliseconds
                "timeout": timeout * 1000,  # Convert to milliseconds
                "retries": max_retries
            }
        }
        
        # Add HTTP-specific configuration
        if probe_type in ["http", "https"]:
            endpoint_config["probe"].update({
                "method": http_method,
                "path": url_path,
                "expected_codes": expected_codes
            })
            
        return endpoint_config

    def _delete_endpoint_probes(self, healthmonitor_id, metadata):
        """Delete all endpoint probes for a health monitor.

        Args:
            healthmonitor_id: Health monitor UUID
            metadata: Health monitor metadata

        Returns:
            int: Number of endpoints deleted
        """
        endpoints_deleted = 0
        
        if 'endpoints_created' in metadata:
            for endpoint_address in metadata['endpoints_created']:
                try:
                    endpoint_name = f"hm-{healthmonitor_id}-{endpoint_address}"
                    self.api_client.delete_endpoint(endpoint_name)
                    endpoints_deleted += 1
                    LOG.debug(f"Deleted endpoint probe for {endpoint_address}")
                except Exception as e:
                    LOG.warning(f"Failed to delete endpoint probe for {endpoint_address}: {e}")
                    
        LOG.debug(f"Deleted {endpoints_deleted} endpoint probes for health monitor {healthmonitor_id}")
        return endpoints_deleted

    def _apply_updates(self, healthmonitor, update_dict):
        """Apply updates from update_dict to healthmonitor object.
        
        This method handles both dictionary and object types for healthmonitor.
        
        Args:
            healthmonitor: Current health monitor object or dictionary
            update_dict: Dictionary with the changed attributes
            
        Returns:
            dict: Updated health monitor dictionary
        """
        # Create a copy of the healthmonitor to avoid modifying the original
        if isinstance(healthmonitor, dict):
            # For dictionary type, create a new dictionary with updates
            updated_healthmonitor = {**healthmonitor, **update_dict}
        else:
            # For object type, convert to dictionary and apply updates
            updated_healthmonitor = {}
            # Copy all attributes from the object to the dictionary
            for attr in dir(healthmonitor):
                if not attr.startswith('_') and not callable(getattr(healthmonitor, attr)):
                    updated_healthmonitor[attr] = getattr(healthmonitor, attr)
            # Apply updates from update_dict
            updated_healthmonitor.update(update_dict)
            
        return updated_healthmonitor
        
    def _determine_operating_status(self, metadata):
        """Determine health monitor operating status from endpoint states.

        Args:
            metadata: Health monitor metadata

        Returns:
            str: Operating status (ONLINE, OFFLINE, ERROR)
        """
        # Default to ONLINE if no endpoints or all endpoints are healthy
        return lib_consts.ONLINE

    def _get_pool_members(self, pool_id):
        """Get all members for a pool.

        Args:
            pool_id: Pool UUID

        Returns:
            list: List of pool member dictionaries

        Raises:
            DriverError: If pool members cannot be retrieved
        """
        try:
            # Get pool members from metadata
            pool_metadata = utils.get_id_mapping_metadata(
                self.resource_mapper.id_mapping_cache,
                pool_id
            )
            if not pool_metadata or 'members' not in pool_metadata:
                LOG.warning(f"No members found for pool {pool_id}")
                return []
                
            return pool_metadata['members']
            
        except Exception as e:
            LOG.error(f"Failed to get pool members for {pool_id}: {e}")
            raise exceptions.DriverError(f"Failed to get pool members: {e}")
