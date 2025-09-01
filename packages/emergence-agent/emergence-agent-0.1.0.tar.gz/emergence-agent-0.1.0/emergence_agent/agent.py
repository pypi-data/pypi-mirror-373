"""
Base Agent Class for Emergence Platform

This module provides the foundational Agent class that all Emergence agents inherit from.
It handles platform registration, webhook management, and core agent lifecycle.
"""

import os
import json
import logging
import threading
import time
from typing import Dict, Any, Optional, Callable, List, Union
from datetime import datetime, timedelta
import asyncio
from urllib.parse import urlparse

from .version import __version__
from .exceptions import EmergenceError, ValidationError, PlatformError, ConfigurationError


class BaseAgent:
    """
    Base class for all Emergence Platform agents.
    
    Provides core functionality for agent registration, webhook handling,
    platform communication, and lifecycle management.
    
    Example:
        >>> agent = BaseAgent(
        ...     name="my-agent",
        ...     description="A sample agent",
        ...     version="1.0.0"
        ... )
        >>> agent.register_with_platform(client)
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        version: str = "1.0.0",
        webhook_url: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        auto_register: bool = True,
        heartbeat_interval: int = 60,
        platform_client = None,
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name (must be unique)
            description: Agent description
            version: Agent version (semantic versioning recommended)
            webhook_url: URL where agent receives webhooks
            capabilities: List of agent capabilities
            config: Additional configuration options
        """
        self.name = self._validate_name(name)
        self.description = description
        self.version = version
        self.webhook_url = webhook_url
        self.capabilities = capabilities or []
        self.config = config or {}
        self.auto_register = auto_register
        self.heartbeat_interval = heartbeat_interval
        
        # Platform integration
        self.agent_id: Optional[str] = None
        self.platform_client = platform_client
        self.is_registered = False
        
        # Webhook handlers
        self._webhook_handlers: Dict[str, Callable] = {}
        
        # Heartbeat management
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._heartbeat_running = False
        self._last_heartbeat: Optional[datetime] = None
        self._heartbeat_failures = 0
        self._max_heartbeat_failures = 3
        
        # Capability management
        self._declared_capabilities: Dict[str, Dict[str, Any]] = {}
        
        # Logging
        self.logger = self._setup_logging()
        
        # Agent state
        self._state = "initialized"
        self._stats = {
            "created_at": datetime.utcnow().isoformat(),
            "requests_handled": 0,
            "last_activity": None,
            "heartbeat_count": 0,
            "last_heartbeat": None,
        }
        
        self.logger.info(f"Agent '{self.name}' v{self.version} initialized")
        
        # Auto-register if platform client provided
        if self.platform_client and self.auto_register:
            self._auto_register()

    def _validate_name(self, name: str) -> str:
        """Validate agent name format."""
        if not name or not isinstance(name, str):
            raise ValidationError("Agent name must be a non-empty string")
        
        if len(name) < 2 or len(name) > 100:
            raise ValidationError("Agent name must be between 2 and 100 characters")
        
        # Basic validation - alphanumeric, hyphens, underscores
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValidationError(
                "Agent name can only contain alphanumeric characters, hyphens, and underscores"
            )
        
        return name

    def _setup_logging(self) -> logging.Logger:
        """Set up agent-specific logging."""
        logger = logging.getLogger(f"emergence_agent.{self.name}")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.name} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger

    def _auto_register(self) -> None:
        """
        Automatically register agent on startup if platform client is available.
        """
        try:
            self.logger.info("Auto-registering agent on startup...")
            self.register_with_platform(self.platform_client)
            
            if self.is_registered:
                self.start_heartbeat()
                
        except Exception as e:
            self.logger.error(f"Auto-registration failed: {e}")
            if self.auto_register:
                self.logger.warning("Will retry registration later...")

    def register_with_platform(self, client) -> Dict[str, Any]:
        """
        Register agent with the Emergence Platform.
        
        Args:
            client: EmergenceClient instance
            
        Returns:
            Registration response from platform
            
        Raises:
            PlatformError: If registration fails
        """
        if self.is_registered:
            self.logger.warning("Agent is already registered")
            return {"status": "already_registered", "agent_id": self.agent_id}
        
        try:
            self.platform_client = client
            
            registration_data = {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "webhook_url": self.webhook_url,
                "capabilities": self.capabilities,
                "declared_capabilities": self._declared_capabilities,
                "sdk_version": __version__,
                "agent_type": self.__class__.__name__,
                "heartbeat_interval": self.heartbeat_interval,
            }
            
            self.logger.info("Registering with Emergence Platform...")
            response = client.register_agent(registration_data)
            
            if response.get("success"):
                self.agent_id = response.get("agent_id")
                self.is_registered = True
                self._state = "registered"
                
                self.logger.info(f"Successfully registered with platform. Agent ID: {self.agent_id}")
                
                # Start heartbeat automatically after successful registration
                if not self._heartbeat_running:
                    self.start_heartbeat()
                    
                return response
            else:
                raise PlatformError(f"Registration failed: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Registration failed: {e}")
            raise PlatformError(f"Failed to register with platform: {e}")

    def webhook_handler(self, path: str, methods: Optional[List[str]] = None):
        """
        Decorator for registering webhook handlers.
        
        Args:
            path: Webhook endpoint path
            methods: HTTP methods to accept (default: ['POST'])
            
        Example:
            >>> @agent.webhook_handler('/process')
            ... def process_data(payload):
            ...     return {"status": "processed"}
        """
        if methods is None:
            methods = ['POST']
            
        def decorator(func: Callable):
            self._webhook_handlers[path] = {
                'handler': func,
                'methods': methods,
                'registered_at': datetime.utcnow().isoformat()
            }
            self.logger.info(f"Registered webhook handler: {methods} {path}")
            return func
        return decorator

    def handle_webhook(self, path: str, payload: Dict[str, Any], method: str = 'POST') -> Dict[str, Any]:
        """
        Handle incoming webhook request.
        
        Args:
            path: Webhook path
            payload: Request payload
            method: HTTP method
            
        Returns:
            Handler response
            
        Raises:
            ValidationError: If handler not found or method not allowed
        """
        if path not in self._webhook_handlers:
            raise ValidationError(f"No handler registered for path: {path}")
        
        handler_info = self._webhook_handlers[path]
        
        if method not in handler_info['methods']:
            raise ValidationError(f"Method {method} not allowed for path {path}")
        
        try:
            self._stats["requests_handled"] += 1
            self._stats["last_activity"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"Handling webhook: {method} {path}")
            result = handler_info['handler'](payload)
            
            self.logger.info(f"Successfully handled webhook: {method} {path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Webhook handler error: {e}")
            raise

    def ping(self) -> Dict[str, Any]:
        """
        Platform ping/health check endpoint.
        
        Returns:
            Agent status information
        """
        return {
            "status": "active",
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "state": self._state,
            "timestamp": datetime.utcnow().isoformat(),
            "stats": self._stats.copy(),
            "sdk_version": __version__,
        }

    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return self.capabilities.copy()

    def start_heartbeat(self) -> None:
        """
        Start the heartbeat thread to maintain platform connection.
        """
        if self._heartbeat_running:
            self.logger.warning("Heartbeat already running")
            return
            
        if not self.platform_client or not self.is_registered:
            raise PlatformError("Cannot start heartbeat - agent not registered with platform")
            
        self._heartbeat_running = True
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_worker,
            daemon=True,
            name=f"heartbeat-{self.name}"
        )
        self._heartbeat_thread.start()
        self.logger.info(f"Heartbeat started with {self.heartbeat_interval}s interval")

    def stop_heartbeat(self) -> None:
        """
        Stop the heartbeat thread.
        """
        if self._heartbeat_running:
            self._heartbeat_running = False
            if self._heartbeat_thread and self._heartbeat_thread.is_alive():
                self._heartbeat_thread.join(timeout=5)
            self.logger.info("Heartbeat stopped")

    def _heartbeat_worker(self) -> None:
        """
        Background thread worker for sending heartbeats to platform.
        """
        while self._heartbeat_running:
            try:
                if self.platform_client and self.is_registered:
                    heartbeat_data = {
                        "agent_id": self.agent_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": self._state,
                        "stats": self._stats.copy(),
                        "capabilities": self.capabilities,
                        "handlers_count": len(self._webhook_handlers),
                    }
                    
                    # Send heartbeat ping
                    response = self.platform_client.send_webhook_ping(self.agent_id)
                    
                    if response.get("success"):
                        self._last_heartbeat = datetime.utcnow()
                        self._stats["heartbeat_count"] += 1
                        self._stats["last_heartbeat"] = self._last_heartbeat.isoformat()
                        self._heartbeat_failures = 0
                        
                        self.logger.debug("Heartbeat sent successfully")
                    else:
                        self._handle_heartbeat_failure("Platform returned unsuccessful response")
                        
                else:
                    self.logger.warning("Cannot send heartbeat - not registered")
                    
            except Exception as e:
                self._handle_heartbeat_failure(f"Heartbeat error: {e}")
                
            # Wait for next heartbeat
            time.sleep(self.heartbeat_interval)

    def _handle_heartbeat_failure(self, error_msg: str) -> None:
        """
        Handle heartbeat failure with retry logic.
        """
        self._heartbeat_failures += 1
        self.logger.warning(f"{error_msg} (failure {self._heartbeat_failures}/{self._max_heartbeat_failures})")
        
        if self._heartbeat_failures >= self._max_heartbeat_failures:
            self.logger.error("Max heartbeat failures reached. Attempting re-registration...")
            try:
                if self.platform_client:
                    self.is_registered = False
                    self._state = "reconnecting"
                    self.register_with_platform(self.platform_client)
            except Exception as e:
                self.logger.error(f"Re-registration failed: {e}")
                self._state = "disconnected"

    def declare_capability(
        self,
        name: str,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        returns: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Declare a structured capability with detailed information.
        
        Args:
            name: Capability name
            description: Capability description
            parameters: Expected parameters schema
            returns: Return value schema
            examples: Usage examples
        """
        capability_spec = {
            "name": name,
            "description": description,
            "declared_at": datetime.utcnow().isoformat(),
            "parameters": parameters or {},
            "returns": returns or {},
            "examples": examples or [],
        }
        
        self._declared_capabilities[name] = capability_spec
        
        # Add to simple capabilities list if not already present
        if name not in self.capabilities:
            self.capabilities.append(name)
            
        self.logger.info(f"Declared capability: {name}")
        
        # Update platform if registered
        if self.is_registered and self.platform_client:
            try:
                self._update_platform_capabilities()
            except Exception as e:
                self.logger.warning(f"Failed to update platform capabilities: {e}")

    def get_declared_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all declared capabilities with their specifications.
        
        Returns:
            Dictionary of capability specifications
        """
        return self._declared_capabilities.copy()

    def remove_declared_capability(self, name: str) -> None:
        """
        Remove a declared capability.
        
        Args:
            name: Capability name to remove
        """
        if name in self._declared_capabilities:
            del self._declared_capabilities[name]
            
        if name in self.capabilities:
            self.capabilities.remove(name)
            
        self.logger.info(f"Removed capability: {name}")
        
        # Update platform if registered
        if self.is_registered and self.platform_client:
            try:
                self._update_platform_capabilities()
            except Exception as e:
                self.logger.warning(f"Failed to update platform capabilities: {e}")

    def _update_platform_capabilities(self) -> None:
        """
        Update capability information on the platform.
        """
        if not self.platform_client or not self.agent_id:
            return
            
        update_data = {
            "capabilities": self.capabilities,
            "declared_capabilities": self._declared_capabilities,
        }
        
        try:
            response = self.platform_client.update_agent_capabilities(self.agent_id, update_data)
            if response.get("success"):
                self.logger.debug("Updated platform capabilities")
            else:
                self.logger.warning(f"Failed to update platform capabilities: {response}")
        except Exception as e:
            self.logger.error(f"Error updating platform capabilities: {e}")
            raise

    def add_capability(self, capability: str) -> None:
        """Add a simple capability to the agent."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.logger.info(f"Added capability: {capability}")

    def remove_capability(self, capability: str) -> None:
        """Remove a capability from the agent."""
        if capability in self.capabilities:
            self.capabilities.remove(capability)
            self.logger.info(f"Removed capability: {capability}")
            
        # Also remove from declared capabilities if present
        if capability in self._declared_capabilities:
            del self._declared_capabilities[capability]

    def update_config(self, config: Dict[str, Any]) -> None:
        """Update agent configuration."""
        self.config.update(config)
        self.logger.info("Agent configuration updated")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        return {
            "name": self.name,
            "version": self.version,
            "state": self._state,
            "agent_id": self.agent_id,
            "is_registered": self.is_registered,
            "webhook_url": self.webhook_url,
            "capabilities": self.capabilities,
            "declared_capabilities": list(self._declared_capabilities.keys()),
            "handlers_count": len(self._webhook_handlers),
            "handlers": list(self._webhook_handlers.keys()),
            "heartbeat_running": self._heartbeat_running,
            "heartbeat_interval": self.heartbeat_interval,
            "last_heartbeat": self._last_heartbeat.isoformat() if self._last_heartbeat else None,
            "heartbeat_failures": self._heartbeat_failures,
            "stats": self._stats.copy(),
            "sdk_version": __version__,
        }

    def send_platform_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        target: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an event to the platform.
        
        Args:
            event_type: Type of event
            data: Event data
            target: Optional target agent/service
            
        Returns:
            Platform response
        """
        if not self.platform_client:
            raise PlatformError("Agent not connected to platform")
        
        event_data = {
            "agent_id": self.agent_id,
            "event_type": event_type,
            "data": data,
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.logger.info(f"Sending platform event: {event_type}")
        return self.platform_client.send_event(event_data)

    def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        self.logger.info("Shutting down agent...")
        
        # Stop heartbeat first
        self.stop_heartbeat()
        
        # Unregister from platform
        if self.platform_client and self.is_registered:
            try:
                self.platform_client.unregister_agent(self.agent_id)
                self.logger.info("Unregistered from platform")
            except Exception as e:
                self.logger.error(f"Error during unregistration: {e}")
        
        self._state = "shutdown"
        self.logger.info("Agent shutdown complete")

    def __repr__(self) -> str:
        return f"BaseAgent(name='{self.name}', version='{self.version}', state='{self._state}')"

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"


class WebhookAgent(BaseAgent):
    """
    Webhook-enabled agent with built-in HTTP server capabilities.
    
    Extends BaseAgent with webhook server functionality for handling
    HTTP requests from the Emergence Platform.
    
    Example:
        >>> client = EmergenceClient(api_key="your_key")
        >>> agent = WebhookAgent(
        ...     name="webhook-agent",
        ...     webhook_url="https://myagent.com/webhook",
        ...     platform_client=client
        ... )
        >>> agent.start_server(host="0.0.0.0", port=8080)
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._server = None
        self._app = None
        
        # Add webhook server capability
        self.declare_capability(
            "webhook_server",
            "HTTP webhook server for receiving platform events",
            parameters={"host": "string", "port": "integer"},
            examples=[{"description": "Start webhook server", "input": {"host": "0.0.0.0", "port": 8080}}]
        )

    def start_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        debug: bool = False
    ) -> None:
        """
        Start the webhook server.
        
        Args:
            host: Host to bind to
            port: Port to bind to  
            debug: Enable debug mode
        """
        try:
            # Try Flask first
            from flask import Flask, request, jsonify
            
            app = Flask(f"emergence_agent_{self.name}")
            
            # Register webhook endpoints
            for path, handler_info in self._webhook_handlers.items():
                def make_handler(handler_func):
                    def flask_handler():
                        try:
                            payload = request.get_json() or {}
                            result = self.handle_webhook(path, payload, request.method)
                            return jsonify(result)
                        except Exception as e:
                            self.logger.error(f"Handler error: {e}")
                            return jsonify({"error": str(e)}), 500
                    return flask_handler
                
                app.add_url_rule(
                    path,
                    endpoint=f"handler_{path.replace('/', '_')}",
                    view_func=make_handler(handler_info['handler']),
                    methods=handler_info['methods']
                )
            
            # Add health check endpoint
            @app.route('/health')
            def health():
                return jsonify(self.ping())
            
            # Platform registration endpoint
            @app.route('/api/webhook/register', methods=['POST'])
            def register_webhook():
                return jsonify({"status": "registered", "agent": self.get_status()})
            
            # Platform ping endpoint  
            @app.route('/api/webhook/ping', methods=['POST'])
            def ping_webhook():
                return jsonify(self.ping())
            
            # Capability endpoint
            @app.route('/api/capabilities', methods=['GET'])
            def get_capabilities():
                return jsonify({
                    "capabilities": self.capabilities,
                    "declared_capabilities": self.get_declared_capabilities()
                })
            
            self._app = app
            
            self.logger.info(f"Starting webhook server on {host}:{port}")
            app.run(host=host, port=port, debug=debug)
            
        except ImportError:
            raise EmergenceError(
                "Flask is required for WebhookAgent. Install with: pip install flask"
            )


class AsyncAgent(BaseAgent):
    """
    Async-enabled agent for high-performance operations.
    
    Extends BaseAgent with async/await support for handling
    concurrent operations and async webhook handlers.
    
    Example:
        >>> client = EmergenceClient(api_key="your_key")
        >>> agent = AsyncAgent(
        ...     name="async-agent",
        ...     platform_client=client
        ... )
        >>> @agent.async_handler('/process')
        ... async def process_async(payload):
        ...     result = await some_async_operation(payload)
        ...     return result
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_handlers: Dict[str, Callable] = {}
        
        # Add async processing capability
        self.declare_capability(
            "async_processing",
            "Asynchronous request processing with high concurrency",
            parameters={"concurrent_requests": "integer"},
            examples=[{"description": "Process multiple requests concurrently"}]
        )

    def async_handler(self, path: str, methods: Optional[List[str]] = None):
        """
        Decorator for async webhook handlers.
        
        Args:
            path: Webhook endpoint path
            methods: HTTP methods to accept
        """
        if methods is None:
            methods = ['POST']
            
        def decorator(func: Callable):
            if not asyncio.iscoroutinefunction(func):
                raise ValidationError("Handler must be an async function")
                
            self._async_handlers[path] = {
                'handler': func,
                'methods': methods,
                'registered_at': datetime.utcnow().isoformat()
            }
            self.logger.info(f"Registered async handler: {methods} {path}")
            return func
        return decorator

    async def handle_async_webhook(
        self,
        path: str,
        payload: Dict[str, Any],
        method: str = 'POST'
    ) -> Dict[str, Any]:
        """Handle async webhook request."""
        if path not in self._async_handlers:
            raise ValidationError(f"No async handler registered for path: {path}")
        
        handler_info = self._async_handlers[path]
        
        if method not in handler_info['methods']:
            raise ValidationError(f"Method {method} not allowed for path {path}")
        
        try:
            self._stats["requests_handled"] += 1
            self._stats["last_activity"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"Handling async webhook: {method} {path}")
            result = await handler_info['handler'](payload)
            
            self.logger.info(f"Successfully handled async webhook: {method} {path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Async webhook handler error: {e}")
            raise

    async def start_async_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8080
    ) -> None:
        """Start async webhook server using aiohttp."""
        try:
            from aiohttp import web, web_request
            
            app = web.Application()
            
            # Register async webhook endpoints
            for path, handler_info in self._async_handlers.items():
                async def make_async_handler(handler_func, handler_path):
                    async def aiohttp_handler(request):
                        try:
                            payload = await request.json() if request.content_type == 'application/json' else {}
                            result = await self.handle_async_webhook(handler_path, payload, request.method)
                            return web.json_response(result)
                        except Exception as e:
                            self.logger.error(f"Async handler error: {e}")
                            return web.json_response({"error": str(e)}, status=500)
                    return aiohttp_handler
                
                for method in handler_info['methods']:
                    app.router.add_route(
                        method,
                        path,
                        await make_async_handler(handler_info['handler'], path)
                    )
            
            # Health check
            async def health(request):
                return web.json_response(self.ping())
            
            app.router.add_get('/health', health)
            
            # Capability endpoint
            async def capabilities(request):
                return web.json_response({
                    "capabilities": self.capabilities,
                    "declared_capabilities": self.get_declared_capabilities()
                })
            
            app.router.add_get('/api/capabilities', capabilities)
            
            self.logger.info(f"Starting async server on {host}:{port}")
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, host, port)
            await site.start()
            
            self.logger.info(f"Async server running on http://{host}:{port}")
            
        except ImportError:
            raise EmergenceError(
                "aiohttp is required for AsyncAgent. Install with: pip install aiohttp"
            )