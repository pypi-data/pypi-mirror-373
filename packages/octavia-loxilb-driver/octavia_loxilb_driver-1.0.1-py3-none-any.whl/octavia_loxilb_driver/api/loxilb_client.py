"""LoxiLB API client for Octavia driver."""

import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import requests
from oslo_config import cfg
from oslo_log import log as logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential

from octavia_loxilb_driver.common import constants, exceptions, openstack_sdk_utils, utils

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class LoxiLBAPIClient:
    """Client for communicating with LoxiLB API."""

    def __init__(self, config=None):
        """Initialize LoxiLB API client.

        Args:
            config: Configuration object, defaults to CONF.loxilb
        """
        self.config = config or CONF.loxilb
        self.endpoints = self._parse_endpoints(self.config.api_endpoints)
        self.current_endpoint_index = 0
        self.session = self._create_session()
        self._setup_authentication()
        # Initialize OpenStack SDK connection for dynamic endpoint discovery
        self.sdk_conn = None
        if self.config.use_mgmt_network:
            try:
                from octavia_loxilb_driver.common import openstack_sdk_utils
                self.sdk_conn = openstack_sdk_utils.get_sdk_connection()
                LOG.info("OpenStack SDK connection initialized for dynamic endpoint discovery")
            except Exception as e:
                LOG.warning(f"Failed to initialize OpenStack SDK connection: {e}")

        LOG.info(f"Initialized LoxiLB client with {len(self.endpoints)} endpoints")
        
    def create_dynamic_endpoint(self, lb_id: str) -> Optional[Dict[str, Any]]:
        """Create a dynamic endpoint based on the LoxiLB VM's IP address.
        
        Args:
            lb_id: Load balancer ID to find the associated LoxiLB VM
            
        Returns:
            Endpoint dictionary or None if VM not found
        """
        if not self.sdk_conn:
            LOG.warning("OpenStack SDK connection not initialized, cannot create dynamic endpoint")
            return None
            
        try:
            # Get the LoxiLB VM's IP address from the management network
            ip_address = openstack_sdk_utils.get_loxilb_server_ip(self.sdk_conn, lb_id)
            if not ip_address:
                LOG.warning(f"Could not find IP address for LoxiLB VM for load balancer {lb_id}")
                return None
                
            # Create endpoint using the VM's IP address
            scheme = "https" if self.config.api_use_ssl else "http"
            port = self.config.api_port or (8091 if scheme == "https" else 11111)
            url = f"{scheme}://{ip_address}:{port}"
            
            LOG.info(f"Created dynamic endpoint for LB {lb_id}: {url}")
            
            return {
                "url": url,
                "host": ip_address,
                "port": port,
                "scheme": scheme,
                "healthy": True,
                "last_check": time.time(),
                "dynamic": True,  # Mark as dynamically created
                "lb_id": lb_id    # Associate with the load balancer
            }
            
        except Exception as e:
            LOG.error(f"Failed to create dynamic endpoint for LB {lb_id}: {e}")
            return None

    def _parse_endpoints(self, endpoints: List[str]) -> List[Dict[str, str]]:
        """Parse and validate API endpoints."""
        parsed_endpoints = []

        for endpoint in endpoints:
            try:
                parsed = urlparse(endpoint)
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError(f"Invalid endpoint format: {endpoint}")

                parsed_endpoints.append(
                    {
                        "url": endpoint.rstrip("/"),
                        "host": parsed.hostname,
                        "port": parsed.port
                        or (443 if parsed.scheme == "https" else 11111),
                        "scheme": parsed.scheme,
                        "healthy": True,
                        "last_check": time.time(),
                    }
                )

            except Exception as e:
                LOG.error(f"Failed to parse endpoint {endpoint}: {e}")
                raise exceptions.LoxiLBConfigurationException(
                    "api_endpoints", endpoint, "http://host:port or https://host:port"
                )

        return parsed_endpoints

    def _create_session(self) -> requests.Session:
        """Create HTTP session with connection pooling and retries."""
        session = requests.Session()

        # Configure retries
        try:
            # For newer versions of urllib3
            retry_strategy = Retry(
                total=self.config.api_retries,
                backoff_factor=self.config.api_retry_interval,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            )
        except TypeError:
            # For older versions of urllib3
            retry_strategy = Retry(
                total=self.config.api_retries,
                backoff_factor=self.config.api_retry_interval,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            )

        # Configure HTTP adapter
        adapter = HTTPAdapter(
            pool_connections=self.config.api_connection_pool_size,
            pool_maxsize=self.config.api_max_connections_per_pool,
            max_retries=retry_strategy,
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set common headers
        session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"octavia-loxilb-driver/{constants.DRIVER_VERSION}",
            }
        )

        return session

    def _setup_authentication(self):
        """Setup authentication for API requests."""
        auth_type = self.config.loxilb_auth_type

        if auth_type == constants.AUTH_TYPE_BASIC:
            if not self.config.loxilb_username or not self.config.loxilb_password:
                raise exceptions.LoxiLBConfigurationException(
                    "authentication", "Basic auth requires username and password"
                )
            self.session.auth = (self.config.loxilb_username, self.config.loxilb_password)

        elif auth_type == constants.AUTH_TYPE_TOKEN:
            if not self.config.api_token:
                raise exceptions.LoxiLBConfigurationException(
                    "authentication", "Token auth requires api_token"
                )
            self.session.headers["Authorization"] = f"Bearer {self.config.api_token}"

        elif auth_type == constants.AUTH_TYPE_TLS:
            if not all(
                [self.config.tls_client_cert_file, self.config.tls_client_key_file]
            ):
                raise exceptions.LoxiLBConfigurationException(
                    "authentication",
                    "TLS auth requires client certificate and key files",
                )

            self.session.cert = (
                self.config.tls_client_cert_file,
                self.config.tls_client_key_file,
            )

            if self.config.tls_ca_cert_file:
                self.session.verify = self.config.tls_ca_cert_file
            else:
                self.session.verify = self.config.tls_verify_cert

    def _get_current_endpoint(self) -> Dict[str, str]:
        """Get current healthy endpoint."""
        # Check if current endpoint is healthy
        current = self.endpoints[self.current_endpoint_index]
        if current["healthy"]:
            return current

        # Find next healthy endpoint
        for i, endpoint in enumerate(self.endpoints):
            if endpoint["healthy"]:
                self.current_endpoint_index = i
                return endpoint

        # No healthy endpoints found
        raise exceptions.LoxiLBClusterException(
            "No healthy endpoints available",
            available_nodes=0,
            total_nodes=len(self.endpoints),
        )

    def _mark_endpoint_unhealthy(self, endpoint_url: str):
        """Mark an endpoint as unhealthy."""
        for endpoint in self.endpoints:
            if endpoint["url"] == endpoint_url:
                endpoint["healthy"] = False
                endpoint["last_check"] = time.time()
                LOG.warning(f"Marked endpoint {endpoint_url} as unhealthy")
                break

    def _check_endpoint_health(self, endpoint: Dict[str, str]) -> bool:
        """Check if an endpoint is healthy."""
        try:
            status_path = constants.API_PATHS["status"]
            response = self.session.get(f"{endpoint['url']}{status_path}", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def _recover_endpoints(self):
        """Attempt to recover unhealthy endpoints."""
        current_time = time.time()

        for endpoint in self.endpoints:
            if not endpoint["healthy"]:
                # Only check every 60 seconds
                if current_time - endpoint["last_check"] > 60:
                    if self._check_endpoint_health(endpoint):
                        endpoint["healthy"] = True
                        LOG.info(f"Recovered endpoint {endpoint['url']}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        lb_id: Optional[str] = None,
    ) -> requests.Response:
        """Make HTTP request to LoxiLB API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path
            data: Request data (for POST/PUT/PATCH)
            params: Query parameters
            lb_id: Optional load balancer ID for dynamic endpoint selection
            
        Returns:
            HTTP response object
            
        Raises:
            LoxiLBResourceNotFoundException: Resource not found
            LoxiLBResourceConflictException: Resource conflict
            LoxiLBAuthenticationException: Authentication failure
            LoxiLBAPIException: Other API errors
        """
        self._recover_endpoints()
        
        # Try to use a dynamic endpoint if lb_id is provided
        dynamic_endpoint = None
        if lb_id and self.config.use_mgmt_network:
            dynamic_endpoint = self.create_dynamic_endpoint(lb_id)
            
        # Use dynamic endpoint if available, otherwise use standard endpoint
        endpoint = dynamic_endpoint if dynamic_endpoint else self._get_current_endpoint()
        url = f"{endpoint['url']}{path}"
        
        # Log which endpoint we're using
        if dynamic_endpoint:
            LOG.debug(f"Using dynamic endpoint for LB {lb_id}: {endpoint['url']}")
        else:
            LOG.debug(f"Using standard endpoint: {endpoint['url']}")
        

        request_data = {
            "timeout": self.config.api_timeout, 
            "params": params or {},
            "json": data  # Always include json, even if None
        }

        if self.config.debug_api_calls:
            LOG.debug(f"LoxiLB API {method} {url} - Data: {data}")

        try:
            response = self.session.request(method, url, **request_data)

            if self.config.debug_api_calls:
                LOG.debug(
                    f"LoxiLB API Response: {response.status_code} - {response.text}"
                )

            # Handle different response codes
            if response.status_code in [200, 201, 202, 204]:
                return response
            elif response.status_code == 404:
                raise exceptions.LoxiLBResourceNotFoundException(
                    resource_type="unknown",
                    resource_id="unknown",
                    endpoint=endpoint["url"],
                )
            elif response.status_code == 409:
                raise exceptions.LoxiLBResourceConflictException(
                    resource_type="unknown",
                    resource_id="unknown",
                    conflict_reason=response.text,
                )
            elif response.status_code in [401, 403]:
                raise exceptions.LoxiLBAuthenticationException(
                    endpoint=endpoint["url"], auth_type=self.config.loxilb_auth_type
                )
            else:
                raise exceptions.LoxiLBAPIException(
                    message=f"API request failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_body=response.text,
                    endpoint=endpoint["url"],
                )

        except requests.exceptions.ConnectionError as e:
            self._mark_endpoint_unhealthy(endpoint["url"])
            raise exceptions.LoxiLBConnectionException(
                endpoint=endpoint["url"], original_exception=str(e)
            )
        except requests.exceptions.Timeout as e:
            raise exceptions.LoxiLBTimeoutException(
                endpoint=endpoint["url"],
                timeout_value=self.config.api_timeout,
                operation=f"{method} {path}",
            )
        except requests.exceptions.RequestException as e:
            raise exceptions.LoxiLBAPIException(
                message=f"API request failed: {str(e)}", endpoint=endpoint["url"]
            )

    def get(self, path: str, params: Optional[Dict] = None, lb_id: Optional[str] = None) -> Optional[Dict]:
        """Make GET request to LoxiLB API."""
        response = self._make_request("GET", path, params=params, lb_id=lb_id)
        if response.content:
            return response.json()
        return None

    def post(self, path: str, data: Dict, lb_id: Optional[str] = None) -> Optional[Dict]:
        """Make POST request to LoxiLB API."""
        response = self._make_request("POST", path, data=data, lb_id=lb_id)
        if response.content:
            return response.json()
        return None

    def put(self, path: str, data: Dict, lb_id: Optional[str] = None) -> Optional[Dict]:
        """Make PUT request to LoxiLB API."""
        response = self._make_request("PUT", path, data=data, lb_id=lb_id)
        if response.content:
            return response.json()
        return None

    def delete(self, path: str, lb_id: Optional[str] = None) -> bool:
        """Make DELETE request to LoxiLB API."""
        response = self._make_request("DELETE", path, lb_id=lb_id)
        return response.status_code in [200, 202, 204]

    def patch(self, path: str, data: Dict, lb_id: Optional[str] = None) -> Optional[Dict]:
        """Make PATCH request to LoxiLB API."""
        response = self._make_request("PATCH", path, data=data, lb_id=lb_id)
        if response.content:
            return response.json()
        return None

    # Status and Health Methods
    def get_status(self) -> Dict:
        """Get LoxiLB status.

        Returns status information from the LoxiLB API.

        :return: Status dictionary
        """
        try:
            return self.get(constants.API_PATHS["status"]) or {}
        except Exception as e:
            LOG.error(f"Failed to get LoxiLB status: {e}")
            return {}

    def health_check(self) -> bool:
        """Perform health check on LoxiLB API.

        Checks if the LoxiLB API is responding properly.

        :return: True if healthy, False otherwise
        """
        try:
            status = self.get_status()
            # Check if we got a valid response with expected fields
            return isinstance(status, dict) and len(status) > 0
        except Exception as e:
            LOG.error(f"Health check failed: {e}")
            return False

    # Load Balancer Methods
    def create_loadbalancer(self, lb_data: Dict) -> Dict:
        """Create a load balancer in LoxiLB.

        Creates a new load balancer service in LoxiLB using the provided configuration.
        The lb_data should follow the LoadbalanceEntry structure from LoxiLB API.

        Args:
            lb_data: Dictionary containing load balancer configuration with:
                - serviceArguments: containing externalIP, port, protocol, etc.
                - endpoints: list of backend servers

        Returns:
            Dict: Response from LoxiLB API or empty dict

        Raises:
            LoxiLBApiException: If the API call fails
        """
        try:
            name = lb_data.get("serviceArguments", {}).get("name", "unknown")
            LOG.info(f"Creating load balancer: {name}")
            
            # Extract Octavia load balancer ID from the name (format: octavia-<lb_id>)
            lb_id = None
            if name.startswith("octavia-"):
                # Extract the ID and remove any 'lb-' prefix if present
                extracted_id = name[len("octavia-"):]
                if extracted_id.startswith("lb-"):
                    lb_id = extracted_id[len("lb-"):]
                    LOG.debug(f"Removed 'lb-' prefix from extracted ID: {extracted_id} -> {lb_id}")
                else:
                    lb_id = extracted_id
                LOG.debug(f"Extracted load balancer ID from name: {lb_id}")
                
            result = self.post(constants.API_PATHS["loadbalancer"], lb_data, lb_id=lb_id)
            LOG.info(f"Load balancer created successfully: {name}")
            return result or {}
        except Exception as e:
            LOG.error(f"Failed to create load balancer: {e}")
            raise

    def list_loadbalancers(self, lb_id: Optional[str] = None) -> List[Dict]:
        """List all load balancers.

        Returns a list of all load balancer services configured in LoxiLB.
        
        Args:
            lb_id: Optional load balancer ID for dynamic endpoint selection

        Returns:
            List[Dict]: List of load balancer configurations

        Raises:
            LoxiLBApiException: If the API call fails
        """
        try:
            result = self.get(constants.API_PATHS["loadbalancer_all"], lb_id=lb_id)
            return result.get("lbServices", []) if result else []
        except Exception as e:
            LOG.error(f"Failed to list load balancers: {e}")
            return []
            
    def get_loadbalancer(self, service_key: str, lb_id: Optional[str] = None) -> Optional[Dict]:
        """Get a load balancer by its service key.
        
        The service key is in the format: <ip_address>:<port>/<protocol>
        This method parses the key and calls get_loadbalancer_by_service.
        
        Args:
            service_key: Service key in the format <ip_address>:<port>/<protocol>
            lb_id: Optional load balancer ID
            
        Returns:
            Dict: Load balancer configuration or None if not found
            
        Raises:
            LoxiLBApiException: If the API call fails
        """
        try:
            # Parse service key to extract components
            ip_port, protocol = service_key.split('/')
            ip_address, port_str = ip_port.split(':')
            port = int(port_str)
            
            # Call get_loadbalancer_by_service with the extracted components
            return self.get_loadbalancer_by_service(ip_address, port, protocol, lb_id=lb_id)
        except Exception as e:
            LOG.error(f"Failed to get load balancer by service key {service_key}: {e}")
            raise exceptions.LoxiLBResourceNotFoundException(
                resource_type="loadbalancer",
                resource_id=service_key,
                endpoint="unknown"
            )

    def get_loadbalancer_by_service(
        self, ip_address: str, port: int, protocol: str, lb_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Get a load balancer by its service properties.

        Since LoxiLB doesn't have a direct endpoint for getting by service properties,
        we need to get all and filter.

        Args:
            ip_address: External IP address
            port: Service port
            protocol: Service protocol
            lb_id: Optional load balancer ID for dynamic endpoint selection

        Returns:
            Dict: Load balancer configuration or None if not found

        Raises:
            LoxiLBApiException: If the API call fails
        """
        try:
            # Use dynamic endpoint if lb_id is provided
            all_lbs = self.list_loadbalancers(lb_id=lb_id)
            
            for lb in all_lbs:
                service_args = lb.get("serviceArguments", {})
                if (
                    service_args.get("externalIP") == ip_address
                    and service_args.get("port") == port
                    and service_args.get("protocol") == protocol
                ):
                    # If we found the LB and it has a name that contains the LB ID,
                    # store the ID for future use
                    name = service_args.get("name", "")
                    if not lb_id and name.startswith("octavia-"):
                        # Extract the ID and remove any 'lb-' prefix if present
                        extracted_id = name[len("octavia-"):]
                        if extracted_id.startswith("lb-"):
                            extracted_lb_id = extracted_id[len("lb-"):]
                            LOG.debug(f"Removed 'lb-' prefix from extracted ID: {extracted_id} -> {extracted_lb_id}")
                        else:
                            extracted_lb_id = extracted_id
                        LOG.debug(f"Extracted load balancer ID from name: {extracted_lb_id}")
                    
                    return lb
            return None
        except Exception as e:
            LOG.error(
                f"Failed to get load balancer by service {ip_address}:{port}/{protocol}: {e}"
            )
            raise exceptions.LoxiLBResourceNotFoundException(
                resource_type="loadbalancer",
                resource_id=f"{ip_address}:{port}/{protocol}",
                endpoint="unknown",
            )

    def update_loadbalancer(self, service_key: str, lb_data: Dict) -> Optional[Dict]:
        """Update a load balancer in LoxiLB.
        
        Args:
            service_key: Service key in the format <ip_address>:<port>/<protocol>
            lb_data: Dictionary containing updated load balancer configuration
            
        Returns:
            Dict: Response from LoxiLB API or empty dict
            
        Raises:
            LoxiLBApiException: If the API call fails
        """
        try:
            # Parse service key to extract components
            ip_port, protocol = service_key.split('/')
            ip_address, port_str = ip_port.split(':')
            
            # Extract Octavia load balancer ID from the name if available
            lb_id = None
            name = lb_data.get("serviceArguments", {}).get("name", "")
            if name.startswith("octavia-"):
                # Extract the ID and remove any 'lb-' prefix if present
                extracted_id = name[len("octavia-"):]
                if extracted_id.startswith("lb-"):
                    lb_id = extracted_id[len("lb-"):]
                    LOG.debug(f"Removed 'lb-' prefix from extracted ID: {extracted_id} -> {lb_id}")
                else:
                    lb_id = extracted_id
                LOG.debug(f"Extracted load balancer ID from name: {lb_id}")
            
            # Delete the existing service first
            self.delete_loadbalancer_rule(ip_address, int(port_str), protocol, lb_id=lb_id)
            
            # Then create a new one with the updated configuration
            return self.create_loadbalancer(lb_data)
        except Exception as e:
            LOG.error(f"Failed to update load balancer {service_key}: {e}")
            raise exceptions.LoxiLBApiException(f"Failed to update load balancer: {str(e)}")
    
    def get_loadbalancer_by_name(self, name: str) -> Optional[Dict]:
        """Get a load balancer by its name.

        Since LoxiLB doesn't have a direct endpoint for getting by name,
        we need to get all and filter.

        Args:
            name: Load balancer name

        Returns:
            Dict: Load balancer configuration or None if not found

        Raises:
            LoxiLBApiException: If the API call fails
        """
        try:
            # Extract Octavia load balancer ID from the name if available
            lb_id = None
            if name.startswith("octavia-"):
                # Extract the ID and remove any 'lb-' prefix if present
                extracted_id = name[len("octavia-"):]
                if extracted_id.startswith("lb-"):
                    lb_id = extracted_id[len("lb-"):]
                    LOG.debug(f"Removed 'lb-' prefix from extracted ID: {extracted_id} -> {lb_id}")
                else:
                    lb_id = extracted_id
                LOG.debug(f"Extracted load balancer ID from name: {lb_id}")
            
            # Use dynamic endpoint if lb_id is available
            all_lbs = self.list_loadbalancers(lb_id=lb_id)
            
            for lb in all_lbs:
                service_args = lb.get("serviceArguments", {})
                if service_args.get("name") == name:
                    return lb
            return None
        except Exception as e:
            LOG.error(f"Failed to get load balancer by name {name}: {e}")
            raise exceptions.LoxiLBResourceNotFoundException(
                resource_type="loadbalancer", resource_id=name, endpoint="unknown"
            )

    def delete_loadbalancer_rule(
        self, ip_address: str, port: int, protocol: str, lb_id: Optional[str] = None
    ) -> bool:
        """Delete a load balancer rule.

        Args:
            ip_address: External IP address
            port: Service port
            protocol: Service protocol
            lb_id: Optional load balancer ID for dynamic endpoint selection

        Returns:
            bool: True if successful

        Raises:
            LoxiLBApiException: If the API call fails
        """
        try:
            LOG.info(f"Deleting LoxiLB rule for {ip_address}:{port}/{protocol}")
            path = f"{constants.API_PATHS['loadbalancer_by_service']}/{ip_address}/port/{port}/protocol/{protocol}"
            result = self.delete(path, lb_id=lb_id)
            LOG.info(f"LoxiLB rule for {ip_address}:{port}/{protocol} deleted successfully")
            return result
        except exceptions.LoxiLBResourceNotFoundException:
            LOG.warning(
                f"LoxiLB rule for {ip_address}:{port}/{protocol} not found, "
                "considering as deleted."
            )
            return True
        except Exception as e:
            LOG.error(
                f"Failed to delete LoxiLB rule for {ip_address}:{port}/{protocol}: {e}"
            )
            raise exceptions.LoxiLBApiException(str(e))

    def delete_loadbalancer(self, service_key: str, lb_id: Optional[str] = None) -> bool:
        """Delete a load balancer by its service key.
        
        Args:
            service_key: Service key in the format <ip_address>:<port>/<protocol>
            lb_id: Optional load balancer ID for dynamic endpoint selection
            
        Returns:
            bool: True if successful
            
        Raises:
            LoxiLBApiException: If the API call fails
        """
        try:
            # Parse service key to extract components
            ip_port, protocol = service_key.split('/')
            ip_address, port_str = ip_port.split(':')
            port = int(port_str)
            
            # Delete the load balancer rule using the extracted components
            return self.delete_loadbalancer_rule(ip_address, port, protocol, lb_id=lb_id)
        except Exception as e:
            LOG.error(f"Failed to delete load balancer {service_key}: {e}")
            raise exceptions.LoxiLBApiException(f"Failed to delete load balancer: {str(e)}")
    
    def delete_loadbalancer_by_name(self, lb_name: str) -> bool:
        """Delete a load balancer by its name.

        Args:
            lb_name: Load balancer name

        Returns:
            bool: True if successful

        Raises:
            LoxiLBApiException: If the API call fails
        """
        try:
            LOG.info(f"Deleting load balancer with name {lb_name}")
            
            # Extract Octavia load balancer ID from the name (format: octavia-<lb_id>)
            lb_id = None
            if lb_name.startswith("octavia-"):
                # Extract the ID and remove any 'lb-' prefix if present
                extracted_id = lb_name[len("octavia-"):]
                if extracted_id.startswith("lb-"):
                    lb_id = extracted_id[len("lb-"):]
                    LOG.debug(f"Removed 'lb-' prefix from extracted ID: {extracted_id} -> {lb_id}")
                else:
                    lb_id = extracted_id
                LOG.debug(f"Extracted load balancer ID from name: {lb_id}")
                
            path = f"{constants.API_PATHS['loadbalancer_by_name']}/{lb_name}"
            result = self.delete(path, lb_id=lb_id)
            LOG.info(f"Load balancer {lb_name} deleted successfully")
            return result
        except exceptions.LoxiLBResourceNotFoundException:
            LOG.warning(f"Load balancer {lb_name} not found, considering as deleted")
            return True
        except Exception as e:
            LOG.error(f"Failed to delete load balancer {lb_name}: {e}")
            raise exceptions.LoxiLBApiException(str(e))

    def delete_all_loadbalancers(self) -> bool:
        """Delete all load balancers.

        Returns:
            bool: True if successful, False otherwise
        """
        LOG.debug("Deleting all LoxiLB load balancers")
        try:
            self.delete(constants.API_PATHS["loadbalancer_all"])
            LOG.info("Successfully deleted all LoxiLB load balancers")
            return True
        except exceptions.LoxiLBResourceNotFound:
            LOG.info("No load balancers found to delete")
            return True
        except Exception as e:
            LOG.error(f"Failed to delete all load balancers: {e}")
            return False

    # Metrics API methods

    def get_metrics(self) -> Dict[str, Any]:
        """Get general Prometheus-formatted metrics.

        Returns:
            Dict containing metrics in Prometheus text format
        """
        LOG.debug("Getting LoxiLB metrics")
        try:
            response = self.get(constants.API_PATHS["metrics"])
            return response
        except Exception as e:
            LOG.error(f"Failed to get metrics: {e}")
            raise exceptions.LoxiLBAPIException(f"Failed to get metrics: {e}")

    def get_lb_rule_count_metrics(self) -> Dict[str, Any]:
        """Get load balancer rule count metrics.

        Returns:
            Dict containing load balancer rule count metrics
        """
        LOG.debug("Getting LoxiLB load balancer rule count metrics")
        try:
            response = self.get(constants.API_PATHS["metrics_lbrulecount"])
            return response
        except Exception as e:
            LOG.error(f"Failed to get load balancer rule count metrics: {e}")
            raise exceptions.LoxiLBAPIException(
                f"Failed to get load balancer rule count metrics: {e}"
            )

    def get_lb_processed_traffic_metrics(self) -> Dict[str, Any]:
        """Get load balancer processed traffic metrics.

        Returns:
            Dict containing load balancer processed traffic metrics
        """
        LOG.debug("Getting LoxiLB load balancer processed traffic metrics")
        try:
            response = self.get(constants.API_PATHS["metrics_lbprocessedtraffic"])
            return response
        except Exception as e:
            LOG.error(f"Failed to get load balancer processed traffic metrics: {e}")
            raise exceptions.LoxiLBAPIException(
                f"Failed to get load balancer processed traffic metrics: {e}"
            )

    def get_endpoint_distribution_traffic_metrics(self) -> Dict[str, Any]:
        """Get endpoint distribution traffic metrics per service.

        Returns:
            Dict containing endpoint distribution traffic metrics
        """
        LOG.debug("Getting LoxiLB endpoint distribution traffic metrics")
        try:
            response = self.get(constants.API_PATHS["metrics_epdisttraffic"])
            return response
        except Exception as e:
            LOG.error(f"Failed to get endpoint distribution traffic metrics: {e}")
            raise exceptions.LoxiLBAPIException(
                f"Failed to get endpoint distribution traffic metrics: {e}"
            )

    def get_service_distribution_traffic_metrics(self) -> Dict[str, Any]:
        """Get service distribution traffic metrics.

        Returns:
            Dict containing service distribution traffic metrics
        """
        LOG.debug("Getting LoxiLB service distribution traffic metrics")
        try:
            response = self.get(constants.API_PATHS["metrics_servicedisttraffic"])
            return response
        except Exception as e:
            LOG.error(f"Failed to get service distribution traffic metrics: {e}")
            raise exceptions.LoxiLBAPIException(
                f"Failed to get service distribution traffic metrics: {e}"
            )

    # Status and Metrics Methods
    def get_status(self) -> Dict:
        """Get LoxiLB status.

        Returns status information from the LoxiLB API.

        Returns:
            Dict: Status dictionary

        Raises:
            LoxiLBApiException: If the API call fails
        """
        try:
            return self.get(constants.API_PATHS["status"]) or {}
        except Exception as e:
            LOG.error(f"Failed to get LoxiLB status: {e}")
            return {}

    # Endpoint API methods for health monitoring

    def create_endpoint(self, endpoint_data: Dict) -> Dict:
        """Create an endpoint for health monitoring.

        Args:
            endpoint_data: LoxiLB endpoint configuration

        Returns:
            dict: Response from LoxiLB API

        Raises:
            LoxiLBAPIException: If API call fails
        """
        try:
            LOG.debug(f"Creating endpoint: {endpoint_data}")
            return self._make_request(
                "POST", constants.API_PATHS["endpoint"], json=endpoint_data
            )
        except Exception as e:
            LOG.error(f"Failed to create endpoint: {e}")
            raise exceptions.LoxiLBAPIException(f"Create endpoint failed: {e}")

    def delete_endpoint(self, ip_address: str, name: Optional[str] = None, 
                       probe_type: Optional[str] = None, probe_port: Optional[int] = None) -> Dict:
        """Delete an endpoint from health monitoring.

        Args:
            ip_address: IP address of the endpoint
            name: Optional endpoint identifier
            probe_type: Optional probe type filter
            probe_port: Optional probe port filter

        Returns:
            dict: Response from LoxiLB API

        Raises:
            LoxiLBAPIException: If API call fails
        """
        try:
            # Build the URL with path parameter
            url_path = f"{constants.API_PATHS['endpoint_by_ip']}/{ip_address}"
            
            # Build query parameters
            params = {}
            if name is not None:
                params["name"] = name
            if probe_type is not None:
                params["probe_type"] = probe_type
            if probe_port is not None:
                params["probe_port"] = probe_port

            LOG.debug(f"Deleting endpoint: {ip_address} with params: {params}")
            return self._make_request("DELETE", url_path, params=params)
        except Exception as e:
            LOG.error(f"Failed to delete endpoint {ip_address}: {e}")
            raise exceptions.LoxiLBAPIException(f"Delete endpoint failed: {e}")

    def get_endpoints(self) -> List[Dict]:
        """Get all endpoints.

        Returns:
            list: List of endpoint configurations

        Raises:
            LoxiLBAPIException: If API call fails
        """
        try:
            LOG.debug("Getting all endpoints")
            response = self._make_request("GET", constants.API_PATHS["endpoint_all"])
            return response.get("Attr", []) if response else []
        except Exception as e:
            LOG.error(f"Failed to get endpoints: {e}")
            raise exceptions.LoxiLBAPIException(f"Get endpoints failed: {e}")

    def get_endpoint_by_ip(self, ip_address: str) -> Optional[Dict]:
        """Get endpoint by IP address.

        Args:
            ip_address: IP address of the endpoint

        Returns:
            dict: Endpoint configuration if found, None otherwise

        Raises:
            LoxiLBAPIException: If API call fails
        """
        try:
            LOG.debug(f"Getting endpoint by IP: {ip_address}")
            endpoints = self.get_endpoints()
            
            # Find endpoint matching the IP address
            for endpoint in endpoints:
                if endpoint.get("hostName", "").split("/")[0] == ip_address:
                    return endpoint
            
            return None
        except Exception as e:
            LOG.error(f"Failed to get endpoint {ip_address}: {e}")
            raise exceptions.LoxiLBAPIException(f"Get endpoint failed: {e}")

    def set_endpoint_host_state(self, host_data: Dict) -> Dict:
        """Set the state of an endpoint host.

        Args:
            host_data: Host state configuration

        Returns:
            dict: Response from LoxiLB API

        Raises:
            LoxiLBAPIException: If API call fails
        """
        try:
            LOG.debug(f"Setting endpoint host state: {host_data}")
            return self._make_request(
                "POST", constants.API_PATHS["endpoint_host_state"], json=host_data
            )
        except Exception as e:
            LOG.error(f"Failed to set endpoint host state: {e}")
            raise exceptions.LoxiLBAPIException(f"Set endpoint host state failed: {e}")

    def health_check(self) -> bool:
        """Perform health check on LoxiLB API.

        Checks if the LoxiLB API is responding properly.

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            status = self.get_status()
            # Check if we got a valid response with expected fields
            return isinstance(status, dict) and len(status) > 0
        except Exception as e:
            LOG.error(f"Health check failed: {e}")
            return False

    def close(self):
        """Close the API client and cleanup resources."""
        if hasattr(self, "session"):
            self.session.close()
        LOG.info("LoxiLB API client closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
