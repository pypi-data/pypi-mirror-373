# NexusAI Python SDK

Python SDK for **NexusAI** - The AI Agent Platform designed for African businesses.

## Features

- 🤖 **Text AI Agents** - ChatGPT-powered conversational AI
- 🎤 **Voice AI Agents** - Real-time voice conversations
- 👁️ **Vision AI Agents** - Image and video analysis
- 📞 **Phone Integration** - Emergency services, customer support
- 🌍 **African Market Focus** - Built for African businesses
- 🔧 **Business Logic Adapters** - Customize AI behavior for your industry

## Quick Start

```bash
pip install nexusai-sdk
```

```python
from nexusai_sdk import NexusAIClient, AgentConfig

# Initialize client
client = NexusAIClient("https://your-nexusai-instance.com")

# Create an agent session
config = AgentConfig(
    agent_id="customer_support",
    instructions="You are a helpful customer support agent for an African telecom company.",
    capabilities=["text", "voice"],
    business_logic_adapter="telecom_support"
)

session = client.create_agent_session(config)

# Send a message
response = session.send_message("Hello, I need help with my mobile data plan")
print(response.content)
```

## Use Cases

### 🏥 Emergency Services

```python
# Emergency dispatcher AI
emergency_config = AgentConfig(
    agent_id="emergency_dispatcher",
    business_logic_adapter="emergency_services",
    capabilities=["text", "voice", "phone"]
)
```

### 📚 Language Learning

```python
# Language learning tutor
learning_config = AgentConfig(
    agent_id="french_tutor",
    business_logic_adapter="language_learning",
    capabilities=["text", "voice"]
)
```

### 🏪 Customer Support

```python
# Business customer support
support_config = AgentConfig(
    agent_id="support_agent",
    business_logic_adapter="customer_support",
    capabilities=["text", "voice", "vision"]
)
```

## Documentation

Visit [nexusai.com/docs](https://nexusai.com/docs) for complete documentation.

## License

MIT License - See LICENSE file for details.
