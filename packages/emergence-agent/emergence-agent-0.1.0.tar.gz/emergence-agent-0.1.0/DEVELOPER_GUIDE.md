# Emergence Agent Developer Guide

## 🚀 Quick Start

The Emergence Agent SDK provides a clean, developer-friendly interface for creating intelligent agents. Simply inherit from the `Agent` class and override methods to define your agent's behavior.

```python
from emergence_agent import Agent

class MyAgent(Agent):
    def setup(self):
        self.declare_capability("greeting", "Say hello to users")
    
    def handle_request(self, request_type, data):
        if request_type == "greet":
            return {"message": f"Hello, {data['name']}!"}
        return {"error": "Unknown request"}

# Use as context manager (automatically starts/stops)
with MyAgent(name="greeter") as agent:
    print("Agent is ready!")
# Agent automatically cleans up

# Or manage lifecycle manually
agent = MyAgent(name="greeter")
agent.start()  # Registers with platform and starts heartbeat
# ... use agent ...
agent.stop()   # Graceful shutdown
```

## 🏗️ Agent Architecture

### Core Components

1. **Agent Class**: Clean inheritance-based interface
2. **Override Methods**: Define custom behavior
3. **Helper Methods**: Platform interaction utilities
4. **Decorators**: Add functionality declaratively
5. **Automatic Integration**: Platform registration and heartbeat

### Agent Lifecycle

```
Initialize → setup() → register → on_start() → [running] → on_stop() → shutdown
```

## 📖 API Reference

### Agent Constructor

```python
class Agent:
    def __init__(
        self,
        name: str,                    # Agent name (required, must be unique)
        description: str = "",        # Agent description
        version: str = "1.0.0",      # Agent version
        api_key: Optional[str] = None, # Platform API key (or set EMERGENCE_API_KEY)
        webhook_url: Optional[str] = None, # Webhook URL for receiving requests
        heartbeat_interval: int = 60,  # Heartbeat interval in seconds
        enable_webhooks: bool = False, # Enable webhook server functionality
        enable_async: bool = False,    # Enable async processing capabilities
        auto_register: bool = True     # Automatically register with platform on start
    )
```

### Override Methods

#### `setup()`
Called once during agent initialization. Use for:
- Declaring capabilities
- Initializing resources
- Setting up configurations

```python
def setup(self):
    self.declare_capability("text_analysis", "Analyze text sentiment")
    # Initialize any resources needed
```

#### `handle_request(request_type, data)`
Handle incoming requests from the platform or other agents.

```python
def handle_request(self, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    if request_type == "analyze":
        return self.analyze_text(data["text"])
    elif request_type == "summarize":
        return self.summarize_text(data["text"])
    return {"error": "Unknown request type"}
```

#### `on_start()`
Called after successful platform registration. Use for initialization requiring platform connectivity.

```python
def on_start(self):
    # Find other agents to work with
    math_agents = self.find_agents(capability="arithmetic")
    self.math_service = math_agents[0] if math_agents else None
```

#### `on_stop()`
Called before agent shutdown. Use for cleanup and final operations.

```python
def on_stop(self):
    # Save state, close connections, etc.
    self.save_state()
```

#### `on_error(error, context)`
Handle errors that occur during agent operation.

```python
def on_error(self, error: Exception, context: Dict[str, Any]):
    self.log(f"Error in {context['operation']}: {error}")
    # Custom error handling logic
```

### Helper Methods

#### `declare_capability(name, description, parameters=None, returns=None, examples=None)`
Declare what your agent can do with detailed specifications.

```python
self.declare_capability(
    "sentiment_analysis",
    "Analyze text sentiment and return confidence scores",
    parameters={
        "text": {"type": "string", "required": True, "min_length": 1},
        "language": {"type": "string", "default": "en"},
        "detailed": {"type": "boolean", "default": False}
    },
    returns={
        "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
        "confidence": {"type": "number", "range": [0, 1]},
        "keywords": {"type": "array", "items": "string"}
    },
    examples=[
        {
            "description": "Basic sentiment analysis",
            "input": {"text": "I love this product!", "language": "en"},
            "output": {"sentiment": "positive", "confidence": 0.95, "keywords": ["love"]}
        }
    ]
)
```

#### `register_handler(request_type, handler_function)`
Register specific handlers for request types.

```python
def handle_math(data):
    return {"result": data["a"] + data["b"]}

self.register_handler("add_numbers", handle_math)
```

#### `find_agents(capability=None, category=None, live_only=True)`
Discover other agents on the platform.

```python
# Find all agents with text processing capability
text_agents = self.find_agents(capability="text_processing")

# Find all live agents
live_agents = self.find_agents(live_only=True)
```

#### `call_agent(agent_name, request_type, data, timeout=30)`
Call another agent on the platform.

```python
# Call a math service to perform calculation
result = self.call_agent(
    "math-service",
    "calculate", 
    {"operation": "multiply", "a": 6, "b": 7}
)
print(result["result"])  # 42
```

#### `log(message, level="info")`
Log messages with agent context.

```python
self.log("Processing request", "info")
self.log("Warning: Low memory", "warning") 
self.log("Error occurred", "error")
self.log("Debug info", "debug")
```

#### `get_status()`
Get comprehensive agent status and statistics.

```python
status = self.get_status()
print(f"Agent {status['name']} has {len(status['capabilities'])} capabilities")
```

## 🎨 Decorators

Enhance your agent methods with powerful decorators:

### `@capability(...)`
Automatically declare capabilities when methods are defined.

```python
@capability(
    "text_processing",
    "Process and analyze text content",
    parameters={"text": {"type": "string", "required": True}},
    returns={"word_count": {"type": "integer"}}
)
def process_text(self, text: str):
    return {"word_count": len(text.split())}
```

### `@request_handler(request_type)`
Automatically register method as request handler.

```python
@request_handler("calculate")
def handle_calculation(self, data):
    return {"result": data["a"] + data["b"]}
```

### `@validate_input(**field_specs)`
Validate input parameters with detailed schemas.

```python
@validate_input(
    email={"type": "string", "required": True},
    age={"type": "integer", "min": 0, "max": 150},
    tags={"type": "array", "max_length": 10}
)
def update_profile(self, email: str, age: int, tags: list):
    return {"updated": True}
```

### `@rate_limit(requests_per_second, burst_size)`
Rate limit method calls to prevent abuse.

```python
@rate_limit(requests_per_second=2.0, burst_size=5)
def expensive_operation(self, data):
    # This method will be rate limited
    return process_heavy_computation(data)
```

### `@retry_on_failure(max_retries, delay, backoff_multiplier)`
Automatically retry failed operations with exponential backoff.

```python
@retry_on_failure(max_retries=3, delay=1.0, backoff_multiplier=2.0)
def unreliable_api_call(self, data):
    return external_api.call(data)
```

### `@cache_result(ttl_seconds, key_func=None)`
Cache method results for improved performance.

```python
@cache_result(ttl_seconds=300)  # Cache for 5 minutes
def expensive_calculation(self, x, y):
    time.sleep(2)  # Simulate expensive operation
    return x ** y
```

### `@timing_stats(include_args=False)`
Track timing statistics for performance monitoring.

```python
@timing_stats(include_args=True)
def monitored_method(self, data):
    # Timing stats will be automatically collected
    return process_data(data)
```

### `@log_calls(level="info", include_args=False, include_result=False)`
Automatically log method calls for debugging.

```python
@log_calls(level="debug", include_args=True, include_result=True)
def debug_method(self, data):
    return {"processed": True}
```

## 🌐 Webhook Agents

For agents that need to receive HTTP requests:

```python
class WebhookServiceAgent(Agent):
    def __init__(self, *args, **kwargs):
        kwargs["enable_webhooks"] = True
        kwargs["webhook_url"] = "http://localhost:8080/webhook"
        super().__init__(*args, **kwargs)
    
    def setup(self):
        # Webhook server capability is automatically declared
        pass
    
    def handle_request(self, request_type, data):
        if request_type == "process_webhook":
            return {"processed": True, "data": data}
        return {"error": "Unknown request"}

# Start the agent and HTTP server
agent = WebhookServiceAgent(name="webhook-service")
agent.start()
agent.start_server(host="0.0.0.0", port=8080)  # Starts HTTP server
```

## ⚡ Async Agents

For high-performance concurrent processing:

```python
class AsyncProcessorAgent(Agent):
    def __init__(self, *args, **kwargs):
        kwargs["enable_async"] = True
        super().__init__(*args, **kwargs)
    
    def setup(self):
        # Async processing capability is automatically declared
        pass
    
    async def process_batch(self, items):
        # Process items concurrently
        tasks = [self.process_item(item) for item in items]
        results = await asyncio.gather(*tasks)
        return {"results": results}

# Usage with async context
async with AsyncProcessorAgent(name="async-processor") as agent:
    await agent.start_async_server(port=8080)
```

## 🔧 Global Helper Functions

Use these functions outside of agent classes:

```python
from emergence_agent import find_agents, call_agent

# Find agents globally
agents = find_agents(capability="text_processing")

# Call agents globally 
result = call_agent(
    "text-service",
    "analyze",
    {"text": "Hello world!"}
)
```

## 🎯 Best Practices

### 1. Capability Declaration
- Declare all capabilities in `setup()`
- Use detailed parameter and return schemas
- Provide examples for complex operations
- Group related capabilities logically

### 2. Request Handling
- Handle all expected request types
- Return consistent response formats
- Provide meaningful error messages
- Use appropriate HTTP status codes

### 3. Error Handling
- Override `on_error()` for custom error handling
- Log errors with context information
- Use try/except blocks for external calls
- Provide graceful degradation

### 4. Performance
- Use `@cache_result` for expensive operations
- Implement `@rate_limit` for protection
- Use `@timing_stats` for monitoring
- Consider async processing for I/O operations

### 5. Platform Integration
- Set EMERGENCE_API_KEY environment variable
- Use meaningful agent names and descriptions
- Implement proper capability discovery
- Handle platform disconnections gracefully

## 📊 Monitoring and Debugging

### Status Reporting
```python
status = agent.get_status()
print(f"Agent: {status['name']}")
print(f"State: {status['state']}")
print(f"Registered: {status['is_registered']}")
print(f"Capabilities: {status['capabilities']}")
print(f"Heartbeat: {status['heartbeat_running']}")
```

### Timing Statistics
```python
# Enable timing stats in constructor
agent._timing_stats = {}

# Use @timing_stats decorator on methods
stats = agent._timing_stats
for method, data in stats.items():
    print(f"{method}: {data['avg_time']:.3f}s avg, {data['call_count']} calls")
```

### Logging
```python
# Configure logging level
import logging
logging.getLogger('emergence_agent').setLevel(logging.DEBUG)

# Use agent logging
self.log("Debug message", "debug")
self.log("Info message", "info") 
self.log("Warning message", "warning")
self.log("Error message", "error")
```

## 🚀 Deployment

### Environment Setup
```bash
# Set your platform API key
export EMERGENCE_API_KEY="your_api_key_here"

# Install dependencies
pip install emergence-agent
```

### Production Considerations
- Use proper logging configuration
- Implement health checks
- Handle graceful shutdowns
- Monitor resource usage
- Set appropriate rate limits
- Use secrets management for API keys

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "my_agent.py"]
```

## 🎉 Complete Example

```python
from emergence_agent import Agent, capability, validate_input, rate_limit

class ProductionAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._timing_stats = {}  # Enable timing stats
    
    def setup(self):
        """Set up agent capabilities."""
        self.declare_capability(
            "data_analysis",
            "Analyze datasets and generate insights",
            parameters={
                "dataset": {"type": "object", "required": True},
                "analysis_type": {"type": "string", "enum": ["basic", "advanced"]}
            },
            returns={
                "insights": {"type": "array"},
                "summary": {"type": "string"}
            }
        )
    
    @capability(
        "text_processing", 
        "Process text with various operations",
        parameters={"text": {"type": "string", "required": True}},
        returns={"result": {"type": "object"}}
    )
    @validate_input(
        text={"type": "string", "required": True, "min_length": 1},
        operation={"type": "string", "default": "analyze"}
    )
    @rate_limit(requests_per_second=10, burst_size=20)
    def process_text(self, text: str, operation: str = "analyze"):
        """Process text with specified operation."""
        return {
            "result": {
                "word_count": len(text.split()),
                "char_count": len(text),
                "operation": operation
            }
        }
    
    def handle_request(self, request_type: str, data: dict):
        """Handle incoming requests."""
        if request_type == "analyze_data":
            return self.analyze_dataset(data.get("dataset", {}))
        elif request_type == "health_check":
            return {"status": "healthy", "timestamp": time.time()}
        
        return {"error": f"Unknown request type: {request_type}"}
    
    def on_start(self):
        """Called after successful platform registration."""
        self.log("Production agent started successfully")
    
    def on_error(self, error: Exception, context: dict):
        """Handle errors with proper logging."""
        self.log(f"Error in {context.get('operation', 'unknown')}: {error}", "error")
        # Could send alerts, metrics, etc.

# Deploy the agent
if __name__ == "__main__":
    with ProductionAgent(
        name="production-service",
        description="Production-ready data processing agent",
        version="2.1.0"
    ) as agent:
        print(f"Agent {agent.name} is running...")
        # Agent runs until interrupted
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
    # Agent automatically stops and cleans up
```

## 📚 Additional Resources

- [Platform Documentation](https://docs.emergence-platform.com)
- [API Reference](https://api.emergence-platform.com/docs)  
- [Examples Repository](https://github.com/emergence-platform/examples)
- [Community Discord](https://discord.gg/emergence)

---

**🎯 Ready to build amazing agents? Start with the Quick Start example above!**