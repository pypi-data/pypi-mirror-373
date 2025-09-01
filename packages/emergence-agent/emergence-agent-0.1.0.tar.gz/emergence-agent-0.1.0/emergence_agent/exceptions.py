"""
Emergence Agent SDK Exceptions

This module defines all custom exception classes used throughout the SDK.
These exceptions provide specific error handling for different types of
platform and agent-related errors.
"""

from typing import Optional, Dict, Any


class EmergenceError(Exception):
    """
    Base exception class for all Emergence SDK errors.
    
    All other SDK exceptions inherit from this class, allowing for
    broad exception handling when needed.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base Emergence exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional machine-readable error code
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary representation."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }


class AuthenticationError(EmergenceError):
    """
    Raised when authentication with the platform fails.
    
    This includes invalid API keys, expired tokens, or insufficient
    permissions for the requested operation.
    
    Example:
        >>> raise AuthenticationError("Invalid API key provided")
    """
    pass


class ValidationError(EmergenceError):
    """
    Raised when input validation fails.
    
    This includes invalid agent configurations, malformed webhook
    payloads, or missing required fields.
    
    Example:
        >>> raise ValidationError("Agent name must be between 2 and 100 characters")
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field name that failed validation
            value: Value that failed validation
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        
        if field:
            self.details.update({'field': field})
        if value is not None:
            self.details.update({'value': str(value)})


class PlatformError(EmergenceError):
    """
    Raised when platform operations fail.
    
    This includes network errors, server errors, API endpoint failures,
    or other platform-related issues.
    
    Example:
        >>> raise PlatformError("Failed to register agent with platform")
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize platform error.
        
        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_data: Platform response data if available
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_data = response_data or {}
        
        if status_code:
            self.details.update({'status_code': status_code})
        if response_data:
            self.details.update({'response_data': response_data})


class WebhookError(EmergenceError):
    """
    Raised when webhook operations fail.
    
    This includes webhook handler errors, invalid webhook payloads,
    or webhook server configuration issues.
    
    Example:
        >>> raise WebhookError("No handler registered for webhook path")
    """
    
    def __init__(
        self,
        message: str,
        webhook_path: Optional[str] = None,
        handler_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize webhook error.
        
        Args:
            message: Error message
            webhook_path: Webhook path that caused the error
            handler_name: Handler name that caused the error
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.webhook_path = webhook_path
        self.handler_name = handler_name
        
        if webhook_path:
            self.details.update({'webhook_path': webhook_path})
        if handler_name:
            self.details.update({'handler_name': handler_name})


class DeploymentError(EmergenceError):
    """
    Raised when agent deployment fails.
    
    This includes packaging errors, upload failures, or deployment
    configuration issues.
    
    Example:
        >>> raise DeploymentError("Failed to package agent for deployment")
    """
    
    def __init__(
        self,
        message: str,
        deployment_stage: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize deployment error.
        
        Args:
            message: Error message
            deployment_stage: Stage of deployment that failed
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.deployment_stage = deployment_stage
        
        if deployment_stage:
            self.details.update({'deployment_stage': deployment_stage})


class RateLimitError(EmergenceError):
    """
    Raised when API rate limits are exceeded.
    
    This exception includes information about retry timing
    and rate limit details when available.
    
    Example:
        >>> raise RateLimitError("Rate limit exceeded, retry after 60 seconds")
    """
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            limit: Rate limit threshold
            window: Rate limit window in seconds
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.limit = limit
        self.window = window
        
        rate_info = {}
        if retry_after:
            rate_info['retry_after'] = retry_after
        if limit:
            rate_info['limit'] = limit
        if window:
            rate_info['window'] = window
        
        if rate_info:
            self.details.update({'rate_limit': rate_info})


class ConfigurationError(EmergenceError):
    """
    Raised when configuration is invalid or missing.
    
    This includes missing environment variables, invalid
    configuration files, or malformed settings.
    
    Example:
        >>> raise ConfigurationError("Missing required configuration: EMERGENCE_API_KEY")
    """
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_source: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            config_source: Source of configuration (env, file, etc.)
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.config_source = config_source
        
        if config_key:
            self.details.update({'config_key': config_key})
        if config_source:
            self.details.update({'config_source': config_source})


class TimeoutError(EmergenceError):
    """
    Raised when operations timeout.
    
    This includes network timeouts, webhook timeouts,
    or other time-based operation failures.
    
    Example:
        >>> raise TimeoutError("Platform request timed out after 30 seconds")
    """
    
    def __init__(
        self,
        message: str,
        timeout_duration: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            timeout_duration: Duration after which timeout occurred
            operation: Operation that timed out
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration
        self.operation = operation
        
        if timeout_duration:
            self.details.update({'timeout_duration': timeout_duration})
        if operation:
            self.details.update({'operation': operation})


class SecurityError(EmergenceError):
    """
    Raised when security violations occur.
    
    This includes invalid signatures, unauthorized access,
    or other security-related issues.
    
    Example:
        >>> raise SecurityError("Invalid webhook signature")
    """
    
    def __init__(
        self,
        message: str,
        security_context: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize security error.
        
        Args:
            message: Error message
            security_context: Context where security violation occurred
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.security_context = security_context
        
        if security_context:
            self.details.update({'security_context': security_context})


# Exception mapping for HTTP status codes
HTTP_ERROR_MAP = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthenticationError,
    404: PlatformError,
    409: ValidationError,
    422: ValidationError,
    429: RateLimitError,
    500: PlatformError,
    502: PlatformError,
    503: PlatformError,
    504: TimeoutError,
}


def create_error_from_response(
    status_code: int,
    message: str,
    response_data: Optional[Dict[str, Any]] = None
) -> EmergenceError:
    """
    Create appropriate exception from HTTP response.
    
    Args:
        status_code: HTTP status code
        message: Error message
        response_data: Response data from platform
        
    Returns:
        Appropriate exception instance
    """
    error_class = HTTP_ERROR_MAP.get(status_code, PlatformError)
    
    if error_class == RateLimitError and response_data:
        # Extract rate limit info if available
        retry_after = response_data.get('retry_after')
        return error_class(
            message,
            status_code=status_code,
            retry_after=retry_after,
            response_data=response_data
        )
    
    return error_class(
        message,
        status_code=status_code,
        response_data=response_data
    )


def handle_exceptions(func):
    """
    Decorator to handle common exceptions and convert them to SDK exceptions.
    
    Example:
        >>> @handle_exceptions
        ... def risky_operation():
        ...     # Operation that might fail
        ...     pass
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except EmergenceError:
            # Re-raise SDK exceptions as-is
            raise
        except ConnectionError as e:
            raise PlatformError(f"Connection error: {e}")
        except TimeoutError as e:
            raise TimeoutError(f"Operation timed out: {e}")
        except ValueError as e:
            raise ValidationError(f"Invalid value: {e}")
        except Exception as e:
            # Convert unexpected exceptions to base EmergenceError
            raise EmergenceError(f"Unexpected error: {e}")
    
    return wrapper


# Export all exceptions for easy importing
__all__ = [
    'EmergenceError',
    'AuthenticationError',
    'ValidationError',
    'PlatformError',
    'WebhookError',
    'DeploymentError',
    'RateLimitError',
    'ConfigurationError',
    'TimeoutError',
    'SecurityError',
    'HTTP_ERROR_MAP',
    'create_error_from_response',
    'handle_exceptions',
]