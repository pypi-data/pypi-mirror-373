# Emergence Agent SDK

[![PyPI version](https://badge.fury.io/py/emergence-agent.svg)](https://badge.fury.io/py/emergence-agent)
[![Python Support](https://img.shields.io/pypi/pyversions/emergence-agent.svg)](https://pypi.org/project/emergence-agent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://docs.emergence-platform.com/agent-sdk)

Official Python SDK for building and deploying intelligent agents on the [Emergence Platform](https://emergence-platform.com). Create powerful AI agents with automatic platform integration, capability declaration, and seamless communication.

## ✨ Features

- **🚀 Ultra-Simple Agent Creation** - Inherit from `Agent` class and override methods
- **🔄 Automatic Platform Integration** - Registration, heartbeat, and lifecycle management
- **🎯 Declarative Capabilities** - Define what your agent can do with structured schemas
- **🌐 Webhook & Async Support** - Built-in HTTP servers and async processing
- **🎨 Powerful Decorators** - Validation, caching, rate limiting, retry logic, and more
- **🔍 Agent Discovery** - Find and communicate with other agents on the platform
- **📊 Built-in Monitoring** - Performance stats, logging, and status reporting
- **🛡️ Production Ready** - Error handling, graceful shutdown, and robust design

## 🚀 Quick Start

### Installation

```bash
pip install emergence-agent
```

### Basic Agent in 30 Seconds

```python
from emergence_agent import Agent

class MyAgent(Agent):
    def setup(self):
        # Declare what your agent can do
        self.declare_capability("greeting", "Say hello to users")
    
    def handle_request(self, request_type, data):
        # Handle incoming requests
        if request_type == "greet":
            return {"message": f"Hello, {data['name']}!"}
        return {"error": "Unknown request"}

# Start your agent (auto-registers with platform)
with MyAgent(name="greeter") as agent:
    print("🤖 Agent is ready!")
    # Agent automatically handles platform communication
```

### Set Your API Key

```bash
export EMERGENCE_API_KEY="your_api_key_here"
```

Or pass it directly:

```python
agent = MyAgent(name="greeter", api_key="your_api_key")
```

## 🎨 Powerful Decorators

Enhance your agent methods with built-in decorators:

```python
from emergence_agent import (
    Agent, capability, validate_input, rate_limit, 
    cache_result, retry_on_failure
)

class AdvancedAgent(Agent):
    @capability(
        "text_analysis",
        "Analyze text with sentiment detection",
        parameters={"text": {"type": "string", "required": True}},
        returns={"sentiment": {"type": "string"}}
    )
    @validate_input(text={"type": "string", "required": True, "min_length": 1})
    @rate_limit(requests_per_second=10, burst_size=20)
    @cache_result(ttl_seconds=300)  # Cache for 5 minutes
    @retry_on_failure(max_retries=3, delay=1.0)
    def analyze_text(self, text: str):
        return {"sentiment": self.detect_sentiment(text)}
```

**Available Decorators:**
- `@capability()` - Auto-declare capabilities
- `@validate_input()` - Input parameter validation
- `@rate_limit()` - Rate limiting protection
- `@retry_on_failure()` - Automatic retry with backoff
- `@cache_result()` - Method result caching
- `@timing_stats()` - Performance monitoring

## 📖 Documentation

### Core Components

#### EmergenceClient
Main client for platform API interactions:

```python
from emergence_agent import EmergenceClient

client = EmergenceClient(
    api_key="your_api_key",
    base_url="https://api.emergence-platform.com",
    timeout=30
)

# List available agents
agents = client.list_agents()

# Get agent details
agent_info = client.get_agent("agent_id")
```

#### WebhookAgent
Base class for webhook-enabled agents:

```python
from emergence_agent import WebhookAgent

agent = WebhookAgent(
    name="data-processor",
    description="Processes incoming data streams",
    version="1.0.0",
    webhook_url="https://your-domain.com/webhook"
)

@agent.webhook_handler('/data', methods=['POST'])
def handle_data(payload):
    # Process the data
    return {"processed": True, "count": len(payload.get('items', []))}
```

#### AsyncAgent
For high-performance async operations:

```python
from emergence_agent import AsyncAgent
import asyncio

agent = AsyncAgent(name="async-processor")

@agent.async_handler('/batch')
async def process_batch(payload):
    # Async processing
    results = await asyncio.gather(
        *[process_item(item) for item in payload['items']]
    )
    return {"results": results}
```

### Configuration

#### Environment Variables
```bash
EMERGENCE_API_KEY=your_api_key_here
EMERGENCE_BASE_URL=https://api.emergence-platform.com
EMERGENCE_WEBHOOK_URL=https://your-agent.com/webhook
EMERGENCE_LOG_LEVEL=INFO
```

#### Config File
```python
from emergence_agent import EmergenceConfig

config = EmergenceConfig(
    api_key="your_api_key",
    agent_name="my-agent",
    webhook_url="https://myagent.com/webhook",
    auto_register=True,
    retry_attempts=3
)

agent = WebhookAgent.from_config(config)
```

### Decorators and Utilities

#### Validation
```python
from emergence_agent.utils import validate_payload

@agent.webhook_handler('/secure')
@validate_payload({
    "type": "object",
    "required": ["user_id", "data"],
    "properties": {
        "user_id": {"type": "string"},
        "data": {"type": "object"}
    }
})
def secure_endpoint(payload):
    return {"user": payload["user_id"], "processed": True}
```

#### Rate Limiting
```python
from emergence_agent.utils import rate_limit

@agent.webhook_handler('/limited')
@rate_limit(requests=100, window=3600)  # 100 requests per hour
def limited_endpoint(payload):
    return {"status": "processed"}
```

#### Retry Logic
```python
from emergence_agent.utils import retry_on_failure

@agent.webhook_handler('/reliable')
@retry_on_failure(max_attempts=3, backoff=2.0)
def reliable_endpoint(payload):
    # This will retry on failures with exponential backoff
    result = external_api_call(payload)
    return result
```

## 🛠️ CLI Tools

The SDK includes command-line tools for agent development:

### Validate Agent
```bash
emergence-validate my_agent.py
```

### Deploy Agent
```bash
emergence-deploy --agent my_agent.py --platform production
```

### Generate Template
```bash
emergence-agent init --template webhook --name my-new-agent
```

## 📚 Examples

### Flask Integration
```python
from flask import Flask, request
from emergence_agent import EmergenceClient

app = Flask(__name__)
client = EmergenceClient(api_key="your_api_key")

@app.route('/webhook/register', methods=['POST'])
def register_webhook():
    # Register webhook with platform
    result = client.register_webhook(request.json)
    return result

@app.route('/webhook/ping', methods=['POST'])
def ping_webhook():
    # Handle platform ping
    return {"status": "active", "timestamp": datetime.utcnow().isoformat()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### FastAPI Integration
```python
from fastapi import FastAPI
from emergence_agent import EmergenceClient
from pydantic import BaseModel

app = FastAPI()
client = EmergenceClient(api_key="your_api_key")

class WebhookPayload(BaseModel):
    event: str
    data: dict

@app.post('/api/webhook/register')
async def register_webhook(payload: dict):
    result = await client.async_register_webhook(payload)
    return result

@app.post('/api/webhook/ping')
async def ping_webhook():
    return {"status": "active", "version": "1.0.0"}
```

### Background Tasks with Celery
```python
from celery import Celery
from emergence_agent import EmergenceClient

app = Celery('agent_tasks')
client = EmergenceClient(api_key="your_api_key")

@app.task
def process_webhook_data(payload):
    # Process data in background
    result = heavy_computation(payload)
    
    # Report back to platform
    client.report_result(payload['task_id'], result)
    return result
```

## 🧪 Testing

### Unit Tests
```python
import pytest
from emergence_agent import WebhookAgent
from emergence_agent.testing import MockEmergenceClient

def test_webhook_handler():
    agent = WebhookAgent(name="test-agent")
    client = MockEmergenceClient()
    
    @agent.webhook_handler('/test')
    def test_handler(payload):
        return {"echo": payload}
    
    # Test the handler
    result = agent.handle_webhook('/test', {"message": "hello"})
    assert result["echo"]["message"] == "hello"
```

### Integration Tests
```python
import pytest
from emergence_agent import EmergenceClient

@pytest.mark.integration
def test_platform_integration():
    client = EmergenceClient(api_key="test_key")
    
    # Test agent registration
    agent_data = {
        "name": "integration-test-agent",
        "version": "1.0.0",
        "webhook_url": "https://test.example.com/webhook"
    }
    
    result = client.register_agent(agent_data)
    assert result["status"] == "registered"
```

## 📦 Installation Options

### Basic Installation
```bash
pip install emergence-agent
```

### Development Installation
```bash
pip install emergence-agent[dev]
```

### Full Installation (with examples)
```bash
pip install emergence-agent[all]
```

### From Source
```bash
git clone https://github.com/emergence-platform/emergence-agent-sdk.git
cd emergence-agent-sdk
pip install -e .
```

## 🔧 Development

### Setting up Development Environment
```bash
git clone https://github.com/emergence-platform/emergence-agent-sdk.git
cd emergence-agent-sdk
pip install -e .[dev]
pre-commit install
```

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black emergence_agent/
isort emergence_agent/
flake8 emergence_agent/
```

### Type Checking
```bash
mypy emergence_agent/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Platform**: [https://emergence-platform.com](https://emergence-platform.com)
- **Documentation**: [https://docs.emergence-platform.com/agent-sdk](https://docs.emergence-platform.com/agent-sdk)
- **PyPI Package**: [https://pypi.org/project/emergence-agent/](https://pypi.org/project/emergence-agent/)
- **GitHub Repository**: [https://github.com/emergence-platform/emergence-agent-sdk](https://github.com/emergence-platform/emergence-agent-sdk)
- **Issue Tracker**: [https://github.com/emergence-platform/emergence-agent-sdk/issues](https://github.com/emergence-platform/emergence-agent-sdk/issues)

## 💬 Support

- **Documentation**: [docs.emergence-platform.com](https://docs.emergence-platform.com)
- **Community Forum**: [community.emergence-platform.com](https://community.emergence-platform.com)
- **Discord**: [Join our Discord](https://discord.gg/emergence)
- **Email**: developers@emergence-platform.com

## ⭐ Star History

If you find this SDK useful, please consider giving it a star on GitHub!

---

**Built with ❤️ by the Emergence Platform Team**