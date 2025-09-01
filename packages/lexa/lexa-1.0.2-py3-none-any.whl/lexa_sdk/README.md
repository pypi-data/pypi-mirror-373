# Lexa Python SDK

> **The simplest way to use Lexa AI in Python**

A modern, OpenAI-compatible Python SDK for Lexa AI that works out of the box with zero configuration. Built for simplicity, reliability, and production use.

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Key Features

- 🚀 **Zero Configuration** - Just `Lexa(api_key)` and you're ready
- 🔒 **Automatic SSL** - Handles SSL certificates transparently
- 📡 **OpenAI Compatible** - Drop-in replacement for OpenAI SDK
- ⚡ **Streaming Support** - Real-time responses
- 🎯 **Multiple Models** - Access all Lexa models (lexa-mml, lexa-x1, lexa-rho)
- 🛡️ **Production Ready** - Robust error handling and retries
- 🔧 **Type Safe** - Full type hints and validation

## Installation

```bash
pip install lexa
```

## 🚀 Quick Start

**That's literally it:**

```python
from lexa_sdk import Lexa

# Just this - NO other configuration needed!
client = Lexa(api_key="your-api-key")

# Ask anything
response = client.chat.completions.create(
    model="lexa-mml",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response["choices"][0]["message"]["content"])
# "Hello! How can I help you today?"
```

The SDK automatically handles SSL certificates, API endpoints, and all configuration. It just works.

## 📚 Usage Examples

### Basic Chat Completion

```python
from lexa_sdk import Lexa

client = Lexa(api_key="your-api-key")

response = client.chat.completions.create(
    model="lexa-mml",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the capital of France?"}
    ],
    temperature=0.7,
    max_tokens=100
)

print(response["choices"][0]["message"]["content"])
```

### Streaming Responses

```python
from lexa_sdk import Lexa

client = Lexa(api_key="your-api-key")

# Enable streaming for real-time responses
stream = client.chat.completions.create(
    model="lexa-mml",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True,
    max_tokens=200
)

for chunk in stream:
    if chunk["choices"][0]["delta"].get("content"):
        print(chunk["choices"][0]["delta"]["content"], end="")
```

### Convenience Function

```python
from lexa_sdk import chat

# Quick one-off requests
response = chat(
    messages=[{"role": "user", "content": "What's 2 + 2?"}],
    api_key="your-api-key",
    model="lexa-mml"
)

print(response["choices"][0]["message"]["content"])
```

### Different Models

```python
from lexa_sdk import Lexa

client = Lexa(api_key="your-api-key")

models = ["lexa-mml", "lexa-x1", "lexa-rho"]

for model in models:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"Hello from {model}!"}],
        max_tokens=20
    )
    print(f"{model}: {response['choices'][0]['message']['content']}")
```

## 🔧 Configuration

### Environment Variables

Set your API key once:

```bash
export LEXA_API_KEY="your-api-key-here"
```

Then use it in code:

```python
import os
from lexa_sdk import Lexa

client = Lexa(api_key=os.getenv("LEXA_API_KEY"))
```

## 📊 Available Models

| Model | Description | Use Case |
|-------|-------------|----------|
| `lexa-mml` | Multimodal model | General purpose, vision |
| `lexa-x1` | Fast & lightweight | Quick responses |
| `lexa-rho` | Advanced reasoning | Complex tasks |

## 🛠️ Advanced Features

### Error Handling

```python
from lexa_sdk import Lexa
from lexa_sdk.exceptions import LexaAPIError, LexaAuthenticationError

client = Lexa(api_key="your-api-key")

try:
    response = client.chat.completions.create(
        model="lexa-mml",
        messages=[{"role": "user", "content": "Hello!"}]
    )
except LexaAuthenticationError:
    print("Invalid API key")
except LexaAPIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Async Support

```python
import asyncio
from lexa_sdk import Lexa

async def main():
    client = Lexa(api_key="your-api-key")

    response = await client.agenerate(
        messages=[{"role": "user", "content": "Hello async!"}]
    )

    print(response["choices"][0]["message"]["content"])

asyncio.run(main())
```

### Model Management

```python
from lexa_sdk import Lexa

client = Lexa(api_key="your-api-key")

# List available models
models = client.list_models()
print("Available models:", [model["id"] for model in models["data"]])

# Get model details
model_info = client.models.retrieve("lexa-mml")
print(f"Model: {model_info['name']}")
print(f"Context: {model_info['context_window']} tokens")
```

## 🔒 Security & SSL

The SDK handles SSL automatically and securely:

- ✅ **Automatic SSL verification** - No manual configuration needed
- ✅ **Certificate validation** - Uses proper certificate chains
- ✅ **Secure by default** - SSL verification enabled
- ✅ **Transparent handling** - Works without user intervention

If you encounter SSL issues (rare), the SDK will automatically use secure fallbacks.

## 📁 Project Structure

```
lexa_sdk/
├── __init__.py          # Package exports
├── client.py            # Main client and convenience functions
├── language_model.py    # Core language model functionality
├── provider.py          # Provider abstraction
├── ssl_enhancer.py      # SSL certificate handling
├── ssl_config.py        # SSL configuration utilities
├── exceptions.py        # Custom exceptions
└── models.py           # Data models and types
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guide for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: [docs.lexa.chat](https://docs.lexa.chat)
- 🐛 **Issues**: [GitHub Issues](https://github.com/Robi-Labs/lexa-python-sdk/issues)
- 💬 **Community**: [Join us](https://community.robiai.com/)

## 🙏 Acknowledgments

Built with ❤️ for the AI community. Thanks to all contributors!

---

**Made with ❤️ by the Robi Labs**
