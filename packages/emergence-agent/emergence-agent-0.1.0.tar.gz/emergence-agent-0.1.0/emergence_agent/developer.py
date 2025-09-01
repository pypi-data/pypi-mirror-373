"""
Developer Interface for Emergence Agent SDK

This module provides a clean, developer-friendly interface for creating agents.
Developers inherit from the Agent class and override methods to define behavior.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime

from .client import EmergenceClient, AsyncEmergenceClient
from .agent import BaseAgent, WebhookAgent, AsyncAgent
from .exceptions import EmergenceError, ValidationError, PlatformError


class Agent:
    """
    Clean developer interface for creating Emergence Platform agents.
    
    Developers inherit from this class and override methods to define agent behavior.
    The interface handles platform integration, capability declaration, and communication.
    
    Example:
        >>> class MyAgent(Agent):
        ...     def setup(self):
        ...         self.declare_capability("text_processing", 
        ...                                "Process and analyze text")
        ...     
        ...     def handle_request(self, request_type, data):
        ...         if request_type == "analyze_text":
        ...             return self.analyze_text(data["text"])
        ...         return {"error": "Unknown request type"}
        ...     
        ...     def analyze_text(self, text):
        ...         # Your text analysis logic here
        ...         return {"sentiment": "positive", "word_count": len(text.split())}
        
        >>> agent = MyAgent(name="text-analyzer")
        >>> agent.start()  # Automatically registers and starts heartbeat
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        version: str = "1.0.0",
        api_key: Optional[str] = None,
        webhook_url: Optional[str] = None,
        heartbeat_interval: int = 60,
        enable_webhooks: bool = False,
        enable_async: bool = False,
        auto_register: bool = True
    ):
        """
        Initialize the developer agent interface.
        
        Args:
            name: Agent name (must be unique)
            description: Agent description
            version: Agent version
            api_key: Platform API key (or set EMERGENCE_API_KEY env var)
            webhook_url: Webhook URL for receiving requests
            heartbeat_interval: Heartbeat interval in seconds
            enable_webhooks: Enable webhook server functionality
            enable_async: Enable async processing capabilities
            auto_register: Automatically register with platform on start
        """
        self.name = name
        self.description = description
        self.version = version
        self.api_key = api_key or os.getenv('EMERGENCE_API_KEY')
        self.webhook_url = webhook_url
        self.heartbeat_interval = heartbeat_interval
        self.enable_webhooks = enable_webhooks
        self.enable_async = enable_async
        self.auto_register = auto_register
        
        # Internal agent instance
        self._agent: Optional[Union[BaseAgent, WebhookAgent, AsyncAgent]] = None
        self._client: Optional[EmergenceClient] = None
        self._is_started = False
        
        # Developer-declared capabilities
        self._capabilities: Dict[str, Dict[str, Any]] = {}
        self._request_handlers: Dict[str, Callable] = {}
        
        # Initialize the agent
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the underlying agent based on configuration."""
        try:
            # Create platform client if API key available
            if self.api_key:
                self._client = EmergenceClient(api_key=self.api_key)
            
            # Choose agent type based on capabilities
            if self.enable_async:
                self._agent = AsyncAgent(
                    name=self.name,
                    description=self.description,
                    version=self.version,
                    webhook_url=self.webhook_url,
                    platform_client=self._client,
                    heartbeat_interval=self.heartbeat_interval,
                    auto_register=False  # We'll handle registration in start()
                )
            elif self.enable_webhooks:
                self._agent = WebhookAgent(
                    name=self.name,
                    description=self.description,
                    version=self.version,
                    webhook_url=self.webhook_url,
                    platform_client=self._client,
                    heartbeat_interval=self.heartbeat_interval,
                    auto_register=False  # We'll handle registration in start()
                )
            else:
                self._agent = BaseAgent(
                    name=self.name,
                    description=self.description,
                    version=self.version,
                    webhook_url=self.webhook_url,
                    platform_client=self._client,
                    heartbeat_interval=self.heartbeat_interval,
                    auto_register=False  # We'll handle registration in start()
                )
                
        except Exception as e:
            raise EmergenceError(f"Failed to initialize agent: {e}")
    
    # Developer Override Methods
    
    def setup(self):
        """
        Override this method to set up your agent.
        
        Called once during agent initialization. Use this to:
        - Declare capabilities with declare_capability()
        - Initialize resources
        - Set up configurations
        
        Example:
            >>> def setup(self):
            ...     self.declare_capability("math_operations", 
            ...                           "Perform mathematical calculations")
            ...     self.declare_capability("data_validation",
            ...                           "Validate data formats")
        """
        pass
    
    def handle_request(self, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override this method to handle incoming requests.
        
        Args:
            request_type: Type of request being made
            data: Request data payload
            
        Returns:
            Response data dictionary
            
        Example:
            >>> def handle_request(self, request_type, data):
            ...     if request_type == "calculate":
            ...         return {"result": data["a"] + data["b"]}
            ...     elif request_type == "validate":
            ...         return {"valid": self.validate_data(data)}
            ...     return {"error": "Unknown request type"}
        """
        return {"error": "No request handler implemented"}
    
    def on_start(self):
        """
        Override this method for startup logic.
        
        Called after successful platform registration.
        Use for initialization that requires platform connectivity.
        """
        pass
    
    def on_stop(self):
        """
        Override this method for cleanup logic.
        
        Called before agent shutdown.
        Use for resource cleanup and final operations.
        """
        pass
    
    def on_error(self, error: Exception, context: Dict[str, Any]):
        """
        Override this method to handle errors.
        
        Args:
            error: The exception that occurred
            context: Context information about when/where error occurred
            
        Example:
            >>> def on_error(self, error, context):
            ...     self.log(f"Error in {context['operation']}: {error}")
            ...     # Send error notification, retry logic, etc.
        """
        self.log(f"Error in {context.get('operation', 'unknown')}: {error}")
    
    # Developer Helper Methods
    
    def declare_capability(
        self,
        name: str,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        returns: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Declare a capability that this agent provides.
        
        Args:
            name: Capability name
            description: What this capability does
            parameters: Expected input parameters schema
            returns: Expected return value schema
            examples: Usage examples
            
        Example:
            >>> self.declare_capability(
            ...     "text_sentiment",
            ...     "Analyze text sentiment and return score",
            ...     parameters={
            ...         "text": {"type": "string", "required": True},
            ...         "language": {"type": "string", "default": "en"}
            ...     },
            ...     returns={
            ...         "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
            ...         "confidence": {"type": "number", "range": [0, 1]}
            ...     },
            ...     examples=[{
            ...         "input": {"text": "I love this!", "language": "en"},
            ...         "output": {"sentiment": "positive", "confidence": 0.95}
            ...     }]
            ... )
        """
        capability_spec = {
            "name": name,
            "description": description,
            "parameters": parameters or {},
            "returns": returns or {},
            "examples": examples or [],
            "declared_at": datetime.utcnow().isoformat()
        }
        
        self._capabilities[name] = capability_spec
        
        # Also declare on underlying agent if available
        if self._agent:
            self._agent.declare_capability(name, description, parameters, returns, examples)
        
        self.log(f"Declared capability: {name}")
    
    def register_handler(self, request_type: str, handler: Callable):
        """
        Register a handler for a specific request type.
        
        Args:
            request_type: Type of request to handle
            handler: Function to call for this request type
            
        Example:
            >>> def handle_math(data):
            ...     return {"result": data["a"] + data["b"]}
            >>> 
            >>> agent.register_handler("add_numbers", handle_math)
        """
        self._request_handlers[request_type] = handler
        self.log(f"Registered handler for: {request_type}")
    
    def find_agents(
        self,
        capability: Optional[str] = None,
        category: Optional[str] = None,
        live_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find other agents on the platform.
        
        Args:
            capability: Filter by specific capability
            category: Filter by agent category
            live_only: Only return currently active agents
            
        Returns:
            List of agent information dictionaries
            
        Example:
            >>> # Find all agents with text processing capability
            >>> text_agents = agent.find_agents(capability="text_processing")
            >>> 
            >>> # Find all live agents
            >>> live_agents = agent.find_agents(live_only=True)
        """
        if not self._client:
            raise PlatformError("No platform client available. Set API key.")
        
        try:
            # Use the discover_agents method from client
            query = capability if capability else None
            response = self._client.discover_agents(
                query=query,
                category=category,
                live_only=live_only
            )
            
            return response.get('agents', [])
            
        except Exception as e:
            self.on_error(e, {"operation": "find_agents"})
            return []
    
    def call_agent(
        self,
        agent_name: str,
        request_type: str,
        data: Dict[str, Any],
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Call another agent on the platform.
        
        Args:
            agent_name: Name of target agent
            request_type: Type of request to make
            data: Request data
            timeout: Request timeout in seconds
            
        Returns:
            Response from target agent
            
        Example:
            >>> # Call a math agent to perform calculation
            >>> result = agent.call_agent(
            ...     "math-service",
            ...     "calculate",
            ...     {"operation": "add", "a": 5, "b": 3}
            ... )
            >>> print(result["result"])  # 8
        """
        if not self._client:
            raise PlatformError("No platform client available. Set API key.")
        
        try:
            # Create event for agent-to-agent communication
            event_data = {
                "source_agent": self.name,
                "target_agent": agent_name,
                "request_type": request_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "timeout": timeout
            }
            
            response = self._client.send_event(event_data)
            return response.get('result', {})
            
        except Exception as e:
            self.on_error(e, {"operation": "call_agent", "target": agent_name})
            return {"error": str(e)}
    
    def log(self, message: str, level: str = "info"):
        """
        Log a message with agent context.
        
        Args:
            message: Message to log
            level: Log level (info, warning, error, debug)
        """
        if self._agent and hasattr(self._agent, 'logger'):
            logger = self._agent.logger
            if level == "debug":
                logger.debug(message)
            elif level == "warning":
                logger.warning(message)
            elif level == "error":
                logger.error(message)
            else:
                logger.info(message)
        else:
            print(f"[{self.name}] {message}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and statistics.
        
        Returns:
            Comprehensive agent status information
        """
        base_status = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "is_started": self._is_started,
            "enable_webhooks": self.enable_webhooks,
            "enable_async": self.enable_async,
            "declared_capabilities": list(self._capabilities.keys()),
            "registered_handlers": list(self._request_handlers.keys())
        }
        
        if self._agent:
            agent_status = self._agent.get_status()
            base_status.update(agent_status)
        
        return base_status
    
    # Lifecycle Methods
    
    def start(self):
        """
        Start the agent and register with platform.
        
        This method:
        1. Calls setup() for initialization
        2. Registers with platform if API key available
        3. Starts heartbeat
        4. Calls on_start() for custom startup logic
        """
        if self._is_started:
            self.log("Agent already started")
            return
        
        try:
            self.log("Starting agent...")
            
            # Call developer setup
            self.setup()
            
            # Register with platform if client available and auto_register enabled
            if self._agent and self._client and self.auto_register:
                response = self._agent.register_with_platform(self._client)
                if response.get("success"):
                    self.log(f"Registered with platform: {response.get('agent_id')}")
                else:
                    self.log(f"Platform registration failed: {response}")
            elif not self.api_key:
                self.log("No API key provided - running in standalone mode")
            elif not self.auto_register:
                self.log("Auto-registration disabled - running in standalone mode")
            
            # Set up request handling for webhook/async agents
            if isinstance(self._agent, (WebhookAgent, AsyncAgent)):
                self._setup_request_handlers()
            
            self._is_started = True
            
            # Call developer startup hook
            self.on_start()
            
            self.log("Agent started successfully")
            
        except Exception as e:
            self.on_error(e, {"operation": "start"})
            raise EmergenceError(f"Failed to start agent: {e}")
    
    def stop(self):
        """
        Stop the agent and cleanup resources.
        """
        if not self._is_started:
            return
        
        try:
            self.log("Stopping agent...")
            
            # Call developer cleanup hook
            self.on_stop()
            
            # Shutdown underlying agent
            if self._agent:
                self._agent.shutdown()
            
            self._is_started = False
            self.log("Agent stopped")
            
        except Exception as e:
            self.on_error(e, {"operation": "stop"})
    
    def _setup_request_handlers(self):
        """Set up request handlers for webhook/async agents."""
        if isinstance(self._agent, WebhookAgent):
            @self._agent.webhook_handler('/api/request', methods=['POST'])
            def handle_webhook_request(payload):
                return self._dispatch_request(payload)
                
        elif isinstance(self._agent, AsyncAgent):
            @self._agent.async_handler('/api/request', methods=['POST'])
            async def handle_async_request(payload):
                return self._dispatch_request(payload)
    
    def _dispatch_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch incoming requests to appropriate handlers."""
        try:
            request_type = payload.get("request_type")
            data = payload.get("data", {})
            
            if not request_type:
                return {"error": "Missing request_type in payload"}
            
            # Check for registered handler first
            if request_type in self._request_handlers:
                handler = self._request_handlers[request_type]
                return handler(data)
            
            # Fall back to handle_request method
            return self.handle_request(request_type, data)
            
        except Exception as e:
            self.on_error(e, {"operation": "dispatch_request", "payload": payload})
            return {"error": str(e)}
    
    # Context Manager Support
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
    
    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', version='{self.version}', started={self._is_started})"


# Convenience Functions for Global Agent Discovery

def find_agents(
    capability: Optional[str] = None,
    category: Optional[str] = None,
    live_only: bool = True,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Global function to find agents on the platform.
    
    Args:
        capability: Filter by specific capability
        category: Filter by agent category  
        live_only: Only return currently active agents
        api_key: Platform API key (or use EMERGENCE_API_KEY env var)
        
    Returns:
        List of agent information dictionaries
    """
    client = EmergenceClient(api_key=api_key or os.getenv('EMERGENCE_API_KEY'))
    
    response = client.discover_agents(
        query=capability,
        category=category,
        live_only=live_only
    )
    
    return response.get('agents', [])


def call_agent(
    agent_name: str,
    request_type: str,
    data: Dict[str, Any],
    timeout: int = 30,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Global function to call an agent on the platform.
    
    Args:
        agent_name: Name of target agent
        request_type: Type of request to make
        data: Request data
        timeout: Request timeout in seconds
        api_key: Platform API key (or use EMERGENCE_API_KEY env var)
        
    Returns:
        Response from target agent
    """
    client = EmergenceClient(api_key=api_key or os.getenv('EMERGENCE_API_KEY'))
    
    event_data = {
        "target_agent": agent_name,
        "request_type": request_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
        "timeout": timeout
    }
    
    response = client.send_event(event_data)
    return response.get('result', {})