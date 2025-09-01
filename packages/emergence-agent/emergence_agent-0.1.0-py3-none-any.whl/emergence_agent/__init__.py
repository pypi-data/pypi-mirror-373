"""
Emergence Agent SDK

Official Python SDK for building and deploying agents on the Emergence Platform.
Provides tools for agent registration, webhook handling, platform communication,
and deployment automation.

Quick Start:
    from emergence_agent import EmergenceClient, BaseAgent
    
    # Create platform client
    client = EmergenceClient(api_key="your_api_key")
    
    # Create agent
    agent = BaseAgent(name="my-agent", description="My test agent")
    
    # Register with platform
    agent.register_with_platform(client)

For more examples and documentation:
    https://docs.emergence-platform.com/agent-sdk
"""

# Import version info first (no dependencies)
from .version import (
    __version__,
    __version_info__,
    __author__,
    __author_email__,
    __description__,
    __url__,
    __api_version__
)

# Import exception classes (no dependencies)
from .exceptions import (
    EmergenceError,
    AuthenticationError,
    ValidationError,
    DeploymentError,
    WebhookError,
    PlatformError,
    RateLimitError,
    ConfigurationError,
    TimeoutError,
    SecurityError
)

# Import core classes (have dependencies on exceptions and version)
from .client import EmergenceClient, AsyncEmergenceClient
from .agent import BaseAgent, WebhookAgent, AsyncAgent

# Import developer interface
from .developer import Agent, find_agents, call_agent

# Import developer decorators
from .decorators import (
    capability, request_handler, validate_input, rate_limit,
    retry_on_failure, timing_stats, cache_result, log_calls
)

__all__ = [
    # Version info
    '__version__',
    '__version_info__',
    '__author__',
    '__author_email__', 
    '__description__',
    '__url__',
    '__api_version__',
    
    # Developer Interface (Primary)
    'Agent',
    'find_agents',
    'call_agent',
    
    # Developer Decorators
    'capability',
    'request_handler',
    'validate_input',
    'rate_limit',
    'retry_on_failure',
    'timing_stats',
    'cache_result',
    'log_calls',
    
    # Core classes
    'EmergenceClient',
    'AsyncEmergenceClient',
    'BaseAgent',
    'WebhookAgent',
    'AsyncAgent',
    
    # Exceptions
    'EmergenceError',
    'AuthenticationError',
    'ValidationError', 
    'DeploymentError',
    'WebhookError',
    'PlatformError',
    'RateLimitError',
    'ConfigurationError',
    'TimeoutError',
    'SecurityError',
    
    # Utility functions (commented out until implemented)
    # 'validate_agent_config',
    # 'deploy_agent', 
    # 'get_logger',
    # 'webhook_handler',
    # 'rate_limit',
    # 'retry_on_failure',
    # 'validate_payload',
]

# Package metadata for introspection
__package_info__ = {
    'name': 'emergence-agent',
    'version': __version__,
    'description': __description__,
    'author': __author__,
    'url': __url__,
    'api_version': __api_version__,
}

def get_version():
    """Get the package version string."""
    return __version__

def get_api_version():
    """Get the API version string."""
    return __api_version__

def get_package_info():
    """Get complete package information."""
    return __package_info__.copy()

# Initialize default logger
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())