# Antonnia Conversations Python SDK

[![PyPI version](https://badge.fury.io/py/antonnia-conversations.svg)](https://badge.fury.io/py/antonnia-conversations)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client library for the Antonnia Conversations API v2. This SDK provides a clean, async-first interface for managing conversation sessions, messages, and agents.

Part of the Antonnia namespace packages - install only what you need:
- `pip install antonnia-conversations` for conversations API
- `pip install antonnia-orchestrator` for orchestrator API  
- `pip install antonnia-auth` for authentication API
- Or install multiple: `pip install antonnia-conversations antonnia-orchestrator`

## Features

- 🚀 **Async/await support** - Built with modern Python async patterns
- 🔒 **Type safety** - Full type hints and Pydantic models
- 🛡️ **Error handling** - Comprehensive exception handling with proper HTTP status codes
- 📝 **Rich content** - Support for text, images, audio, files, and function calls
- 🔄 **Session management** - Create, transfer, and manage conversation sessions
- 💬 **Message handling** - Send, receive, and search messages
- 🤖 **Agent support** - Work with both AI and human agents
- 🔧 **Namespace packages** - Modular installation, use only what you need

## Installation

```bash
pip install antonnia-conversations
```

## Quick Start

```python
import asyncio
from antonnia.conversations import Conversations
from antonnia.conversations.types import MessageContentText

async def main():
    async with Conversations(
        token="your_api_token",
        base_url="https://api.antonnia.com"
    ) as client:
        # Create a new conversation session
        session = await client.sessions.create(
            contact_id="user_12345",
            contact_name="John Doe",
            metadata={"priority": "high", "department": "support"}
        )
        
        # Send a message from the user
        message = await client.sessions.messages.create(
            session_id=session.id,
            content=MessageContentText(type="text", text="Hello, I need help with my account"),
            role="user"
        )
        
        # Trigger an AI agent response
        updated_session = await client.sessions.reply(session_id=session.id)
        
        # Search for messages in the session
        messages = await client.sessions.messages.search(
            session_id=session.id,
            limit=10
        )
        
        print(f"Session {session.id} has {len(messages)} messages")

if __name__ == "__main__":
    asyncio.run(main())
```

## Authentication

The SDK requires an API token for authentication. You can obtain this from your Antonnia dashboard.

```python
from antonnia.conversations import Conversations

# Initialize with your API token
client = Conversations(
    token="your_api_token_here",
    base_url="https://api.antonnia.com"  # or your custom API endpoint
)
```

## Core Concepts

### Sessions

Sessions represent active conversations between contacts and agents. Each session can contain multiple messages and be transferred between agents.

```python
# Create a session
session = await client.sessions.create(
    contact_id="contact_123",
    contact_name="Jane Smith",
    agent_id="agent_456",  # Optional
    status="open",
    metadata={"source": "website", "priority": "normal"}
)

# Get session details
session = await client.sessions.get(session_id="sess_123")

# Update session metadata
session = await client.sessions.update(
    session_id="sess_123",
    metadata={"priority": "urgent", "escalated": True}
)

# Transfer to another agent
session = await client.sessions.transfer(
    session_id="sess_123",
    agent_id="agent_789"
)

# Finish the session
session = await client.sessions.finish(
    session_id="sess_123",
    ending_survey_id="survey_123"  # Optional
)
```

### Messages

Messages are the individual communications within a session. They support various content types and roles.

```python
from antonnia.conversations.types import MessageContentText, MessageContentImage

# Send a text message
text_message = await client.sessions.messages.create(
    session_id="sess_123",
    content=MessageContentText(type="text", text="Hello there!"),
    role="user"
)

# Send an image message
image_message = await client.sessions.messages.create(
    session_id="sess_123",
    content=MessageContentImage(type="image", url="https://example.com/image.jpg"),
    role="user"
)

# Get a specific message
message = await client.sessions.messages.get(
    session_id="sess_123",
    message_id="msg_456"
)

# Search messages
messages = await client.sessions.messages.search(
    session_id="sess_123",
    offset=0,
    limit=50
)
```

### Content Types

The SDK supports various message content types:

#### Text Messages
```python
from antonnia.conversations.types import MessageContentText

content = MessageContentText(
    type="text",
    text="Hello, how can I help you?"
)
```

#### Image Messages
```python
from antonnia.conversations.types import MessageContentImage

content = MessageContentImage(
    type="image",
    url="https://example.com/image.jpg"
)
```

#### Audio Messages
```python
from antonnia.conversations.types import MessageContentAudio

content = MessageContentAudio(
    type="audio",
    url="https://example.com/audio.mp3",
    transcript="This is the audio transcript"  # Optional
)
```

#### File Messages
```python
from antonnia.conversations.types import MessageContentFile

content = MessageContentFile(
    type="file",
    url="https://example.com/document.pdf",
    mime_type="application/pdf",
    name="document.pdf"
)
```

#### Function Calls (AI Agents)
```python
from antonnia.conversations.types import MessageContentFunctionCall, MessageContentFunctionResult

# Function call from AI
function_call = MessageContentFunctionCall(
    type="function_call",
    id="call_123",
    name="get_weather",
    input='{"location": "New York"}'
)

# Function result
function_result = MessageContentFunctionResult(
    type="function_result",
    id="call_123",
    name="get_weather",
    output='{"temperature": 72, "condition": "sunny"}'
)
```

## Error Handling

The SDK provides structured exception handling:

```python
from antonnia.conversations import Conversations
from antonnia.conversations.exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    APIError
)

try:
    session = await client.sessions.get("invalid_session_id")
except AuthenticationError:
    print("Invalid API token")
except NotFoundError:
    print("Session not found")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Advanced Usage

### Custom HTTP Client

You can provide your own HTTP client for advanced configuration:

```python
import httpx
from antonnia.conversations import Conversations

# Custom HTTP client with proxy
http_client = httpx.AsyncClient(
    proxies="http://proxy.example.com:8080",
    timeout=30.0
)

async with Conversations(
    token="your_token",
    base_url="https://api.antonnia.com",
    http_client=http_client
) as client:
    # Use client as normal
    session = await client.sessions.create(...)
```

### Session Search and Filtering

```python
# Search sessions by contact
sessions = await client.sessions.search(
    contact_id="contact_123",
    status="open",
    limit=10
)

# Pagination
page_1 = await client.sessions.search(
    contact_id="contact_123",
    offset=0,
    limit=20
)

page_2 = await client.sessions.search(
    contact_id="contact_123",
    offset=20,
    limit=20
)
```

### Webhook Events

The Antonnia API supports webhook events for real-time updates. Configure your webhook endpoint to receive these events:

- `session.created` - New session created
- `session.transferred` - Session transferred between agents  
- `session.finished` - Session completed
- `message.created` - New message in session

## API Reference

### Conversations Client

The main client class for accessing the Antonnia API.

#### `Conversations(token, base_url, timeout, http_client)`

**Parameters:**
- `token` (str): Your API authentication token
- `base_url` (str): API base URL (default: "https://api.antonnia.com")
- `timeout` (float): Request timeout in seconds (default: 60.0)
- `http_client` (httpx.AsyncClient, optional): Custom HTTP client

**Properties:**
- `sessions`: Sessions client for session management

### Sessions Client

Manage conversation sessions.

#### `sessions.create(contact_id, contact_name, agent_id=None, status="open", metadata=None)`
#### `sessions.get(session_id)`
#### `sessions.update(session_id, metadata=None)`
#### `sessions.transfer(session_id, agent_id)`
#### `sessions.finish(session_id, ending_survey_id=None)`
#### `sessions.reply(session_id, debounce_time=0)`
#### `sessions.search(contact_id=None, status=None, offset=None, limit=None)`

### Messages Client

Manage messages within sessions. Accessed via `client.sessions.messages`.

#### `messages.create(session_id, content, role="user", provider_message_id=None, replied_provider_message_id=None)`
#### `messages.get(session_id, message_id)`
#### `messages.update(session_id, message_id, provider_message_id=None, replied_provider_message_id=None)`
#### `messages.search(session_id=None, provider_message_id=None, replied_provider_message_id=None, offset=None, limit=None)`

## Requirements

- Python 3.8+
- httpx >= 0.25.0
- pydantic >= 2.7.0

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Namespace Packages

This SDK is part of the **Antonnia namespace packages** ecosystem. Each service has its own installable package, but they all work together under the `antonnia` namespace.

### Available Packages

- **`antonnia-conversations`** - Conversations API (sessions, messages, agents)
- **`antonnia-orchestrator`** - Orchestrator API (threads, runs, assistants) 
- **`antonnia-auth`** - Authentication API (users, tokens, permissions)
- **`antonnia-contacts`** - Contacts API (contact management)
- **`antonnia-events`** - Events API (webhooks, event streams)
- **`antonnia-functions`** - Functions API (serverless functions)

### Usage Examples

**Install only what you need:**
```bash
# Just conversations
pip install antonnia-conversations

# Just orchestrator  
pip install antonnia-orchestrator

# Multiple services
pip install antonnia-conversations antonnia-orchestrator antonnia-auth
```

**Use together seamlessly:**
```python
# Each package provides its own client and types
from antonnia.conversations import Conversations
from antonnia.conversations.types import Session, MessageContentText
from antonnia.conversations.exceptions import AuthenticationError

from antonnia.orchestrator import Orchestrator  
from antonnia.orchestrator.types import Thread, Run
from antonnia.orchestrator.exceptions import OrchestratorError

from antonnia.auth import Auth
from antonnia.auth.types import User, Token
from antonnia.auth.exceptions import TokenExpiredError

async def integrated_example():
    # Initialize multiple services
    conversations = Conversations(token="conv_token")
    orchestrator = Orchestrator(token="orch_token") 
    auth = Auth(token="auth_token")
    
    # Use them together
    user = await auth.users.get("user_123")
    session = await conversations.sessions.create(
        contact_id=user.id,
        contact_name=user.name
    )
    thread = await orchestrator.threads.create(
        user_id=user.id,
        metadata={"session_id": session.id}
    )
```

### Creating Additional Services

To add a new service (e.g., `antonnia-analytics`):

1. **Create package structure:**
   ```
   antonnia-analytics/
   ├── antonnia/
   │   └── analytics/
   │       ├── __init__.py       # Export main Analytics client
   │       ├── client.py         # Analytics client class
   │       ├── types/
   │       │   ├── __init__.py   # Export all types
   │       │   └── reports.py    # Analytics types
   │       └── exceptions.py     # Analytics exceptions
   ├── pyproject.toml           # Package config
   └── setup.py                 # Alternative setup
   ```

2. **Configure namespace package:**
   ```toml
   # pyproject.toml
   [project]
   name = "antonnia-analytics"
   
   [tool.setuptools.packages.find]
   include = ["antonnia*"]
   
   [tool.setuptools.package-data]
   "antonnia.analytics" = ["py.typed"]
   ```

3. **Use consistent imports:**
   ```python
   # User imports
   from antonnia.analytics import Analytics
   from antonnia.analytics.types import Report, ChartData
   from antonnia.analytics.exceptions import AnalyticsError
   ```

This approach provides:
- **Modular installation** - Install only needed services
- **Consistent API** - All services follow the same patterns  
- **Type safety** - Each service has its own typed interfaces
- **No conflicts** - Services can evolve independently
- **Easy integration** - Services work together seamlessly

## Support

- 📖 [Documentation](https://docs.antonnia.com)
- 💬 [Discord Community](https://discord.gg/antonnia)
- 📧 [Email Support](mailto:support@antonnia.com)
- 🐛 [Issue Tracker](https://github.com/antonnia/antonnia-python/issues) 