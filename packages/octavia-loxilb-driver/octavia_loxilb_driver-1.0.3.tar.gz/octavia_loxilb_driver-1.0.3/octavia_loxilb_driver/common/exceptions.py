"""Custom exceptions for LoxiLB Octavia Driver."""

from octavia_lib.api.drivers import exceptions as driver_exceptions


class LoxiLBDriverException(driver_exceptions.DriverError):
    """Base exception for all LoxiLB driver errors."""

    def __init__(self, message, details=None, fault_string=None):
        super().__init__(
            user_fault_string=fault_string or message, operator_fault_string=message
        )
        self.message = message
        self.details = details or {}
        self.fault_string = fault_string

    def __str__(self):
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


class LoxiLBAPIException(LoxiLBDriverException):
    """Exception for LoxiLB API communication errors."""

    def __init__(
        self,
        message,
        status_code=None,
        response_body=None,
        endpoint=None,
        fault_string=None,
    ):
        details = {
            "status_code": status_code,
            "response_body": response_body,
            "endpoint": endpoint,
        }
        super().__init__(message, details, fault_string)
        self.status_code = status_code
        self.response_body = response_body
        self.endpoint = endpoint


class LoxiLBConnectionException(LoxiLBAPIException):
    """Exception for connection errors to LoxiLB API."""

    def __init__(self, endpoint, original_exception=None):
        message = f"Cannot connect to LoxiLB endpoint: {endpoint}"
        if original_exception:
            message += f". Error: {original_exception}"

        fault_string = "Load balancer service temporarily unavailable"
        super().__init__(message=message, endpoint=endpoint, fault_string=fault_string)
        self.original_exception = original_exception


class LoxiLBTimeoutException(LoxiLBAPIException):
    """Exception for API timeout errors."""

    def __init__(self, endpoint, timeout_value, operation=None):
        message = (
            f"Timeout ({timeout_value}s) connecting to LoxiLB endpoint: {endpoint}"
        )
        if operation:
            message += f" during {operation}"

        fault_string = "Load balancer operation timed out"
        super().__init__(message=message, endpoint=endpoint, fault_string=fault_string)
        self.timeout_value = timeout_value
        self.operation = operation


class LoxiLBAuthenticationException(LoxiLBAPIException):
    """Exception for authentication errors."""

    def __init__(self, endpoint, auth_type=None):
        message = f"Authentication failed for LoxiLB endpoint: {endpoint}"
        if auth_type:
            message += f" using {auth_type} authentication"

        fault_string = "Load balancer service authentication failed"
        super().__init__(
            message=message,
            status_code=401,
            endpoint=endpoint,
            fault_string=fault_string,
        )
        self.auth_type = auth_type


class LoxiLBResourceNotFoundException(LoxiLBDriverException):
    """Exception for resource not found errors."""

    def __init__(self, resource_type, resource_id, endpoint=None):
        message = f"LoxiLB resource not found: {resource_type} {resource_id}"
        if endpoint:
            message += f" on endpoint {endpoint}"

        fault_string = f"Load balancer {resource_type} not found"
        super().__init__(message, fault_string=fault_string)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.endpoint = endpoint


class LoxiLBResourceConflictException(LoxiLBDriverException):
    """Exception for resource conflict errors."""

    def __init__(self, resource_type, resource_id, conflict_reason=None):
        message = f"LoxiLB resource conflict: {resource_type} {resource_id}"
        if conflict_reason:
            message += f". Reason: {conflict_reason}"

        fault_string = f"Load balancer {resource_type} configuration conflict"
        super().__init__(message, fault_string=fault_string)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.conflict_reason = conflict_reason


class LoxiLBConfigurationException(LoxiLBDriverException):
    """Exception for configuration errors."""

    def __init__(self, config_parameter, config_value=None, expected_format=None):
        message = f"Invalid LoxiLB configuration: {config_parameter}"
        if config_value is not None:
            message += f" = {config_value}"
        if expected_format:
            message += f". Expected format: {expected_format}"

        fault_string = "Load balancer driver configuration error"
        super().__init__(message, fault_string=fault_string)
        self.config_parameter = config_parameter
        self.config_value = config_value
        self.expected_format = expected_format


class LoxiLBClusterException(LoxiLBDriverException):
    """Exception for cluster-related errors."""

    def __init__(self, cluster_status, available_nodes=None, total_nodes=None):
        message = f"LoxiLB cluster error: {cluster_status}"
        if available_nodes is not None and total_nodes is not None:
            message += f". Available nodes: {available_nodes}/{total_nodes}"

        fault_string = "Load balancer cluster unavailable"
        super().__init__(message, fault_string=fault_string)
        self.cluster_status = cluster_status
        self.available_nodes = available_nodes
        self.total_nodes = total_nodes


class NetworkOperationException(LoxiLBDriverException):
    """Exception for network interface operations."""

    def __init__(self, operation, server_id, network_id=None, interface_id=None, original_exception=None):
        message = f"Network operation '{operation}' failed"
        if server_id:
            message += f" for server {server_id}"
        if network_id:
            message += f" on network {network_id}"
        if interface_id:
            message += f" (interface {interface_id})"
        if original_exception:
            message += f": {original_exception}"

        fault_string = "Load balancer network operation failed"
        super().__init__(message, fault_string=fault_string)
        self.operation = operation
        self.server_id = server_id
        self.network_id = network_id
        self.interface_id = interface_id
        self.original_exception = original_exception


class LoxiLBValidationException(LoxiLBDriverException):
    """Exception for resource validation errors."""

    def __init__(self, resource_type, validation_errors):
        if isinstance(validation_errors, list):
            error_details = "; ".join(validation_errors)
        else:
            error_details = str(validation_errors)

        message = f"LoxiLB {resource_type} validation failed: {error_details}"
        fault_string = f"Load balancer {resource_type} configuration is invalid"
        super().__init__(message, fault_string=fault_string)
        self.resource_type = resource_type
        self.validation_errors = validation_errors


class LoxiLBOperationException(LoxiLBDriverException):
    """Exception for operation-specific errors."""

    def __init__(self, operation, resource_type, resource_id, reason=None):
        message = (
            f"LoxiLB {operation} operation failed for {resource_type} {resource_id}"
        )
        if reason:
            message += f": {reason}"

        fault_string = f"Load balancer {operation} operation failed"
        super().__init__(message, fault_string=fault_string)
        self.operation = operation
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.reason = reason


class LoxiLBCapacityException(LoxiLBDriverException):
    """Exception for capacity/quota exceeded errors."""

    def __init__(self, resource_type, current_count, max_limit):
        message = (
            f"LoxiLB capacity exceeded for {resource_type}: "
            f"{current_count}/{max_limit}"
        )
        fault_string = f"Load balancer {resource_type} capacity limit reached"
        super().__init__(message, fault_string=fault_string)
        self.resource_type = resource_type
        self.current_count = current_count
        self.max_limit = max_limit


class LoxiLBNetworkException(LoxiLBDriverException):
    """Exception for network-related errors."""

    def __init__(self, network_id, subnet_id=None, port_id=None, reason=None):
        message = f"LoxiLB network error for network {network_id}"
        if subnet_id:
            message += f", subnet {subnet_id}"
        if port_id:
            message += f", port {port_id}"
        if reason:
            message += f": {reason}"

        fault_string = "Load balancer network configuration error"
        super().__init__(message, fault_string=fault_string)
        self.network_id = network_id
        self.subnet_id = subnet_id
        self.port_id = port_id
        self.reason = reason


class LoxiLBHealthCheckException(LoxiLBDriverException):
    """Exception for health check related errors."""

    def __init__(self, health_monitor_id, member_id=None, check_type=None, reason=None):
        message = f"LoxiLB health check error for monitor {health_monitor_id}"
        if member_id:
            message += f", member {member_id}"
        if check_type:
            message += f" ({check_type})"
        if reason:
            message += f": {reason}"

        fault_string = "Load balancer health check configuration error"
        super().__init__(message, fault_string=fault_string)
        self.health_monitor_id = health_monitor_id
        self.member_id = member_id
        self.check_type = check_type
        self.reason = reason


class LoxiLBSSLException(LoxiLBDriverException):
    """Exception for SSL/TLS related errors."""

    def __init__(self, certificate_id=None, reason=None):
        message = "LoxiLB SSL/TLS error"
        if certificate_id:
            message += f" for certificate {certificate_id}"
        if reason:
            message += f": {reason}"

        fault_string = "Load balancer SSL certificate error"
        super().__init__(message, fault_string=fault_string)
        self.certificate_id = certificate_id
        self.reason = reason


class LoxiLBMappingException(LoxiLBDriverException):
    """Exception for resource mapping errors between Octavia and LoxiLB."""

    def __init__(
        self,
        message,
        resource_type=None,
        resource_id=None,
        mapping_direction=None,
        original_data=None,
        fault_string=None,
    ):
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "mapping_direction": mapping_direction,
            "original_data": original_data,
        }
        super().__init__(message, details, fault_string)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.mapping_direction = mapping_direction
        self.original_data = original_data


class UnsupportedOptionError(LoxiLBDriverException):
    """Exception for unsupported configuration options."""

    def __init__(self, option=None, message=None):
        if option and not message:
            message = f"Unsupported option: {option}"
        elif not message:
            message = "Unsupported configuration option"
        super().__init__(message)
        self.option = option


class DriverError(LoxiLBDriverException):
    """General driver error exception."""

    def __init__(self, message, operation=None, resource_type=None, resource_id=None):
        super().__init__(message)
        self.operation = operation
        self.resource_type = resource_type
        self.resource_id = resource_id


# Exception mapping for common HTTP status codes
HTTP_EXCEPTION_MAP = {
    400: LoxiLBValidationException,
    401: LoxiLBAuthenticationException,
    403: LoxiLBAuthenticationException,
    404: LoxiLBResourceNotFoundException,
    409: LoxiLBResourceConflictException,
    500: LoxiLBAPIException,
    502: LoxiLBConnectionException,
    503: LoxiLBClusterException,
    504: LoxiLBTimeoutException,
}


def get_exception_for_status_code(status_code, message, **kwargs):
    """Get appropriate exception class for HTTP status code."""
    exception_class = HTTP_EXCEPTION_MAP.get(status_code, LoxiLBAPIException)
    return exception_class(message, **kwargs)
