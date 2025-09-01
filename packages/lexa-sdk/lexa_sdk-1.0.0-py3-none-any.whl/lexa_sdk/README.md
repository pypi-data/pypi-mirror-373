# Lexa Python SDK

A Python SDK for Lexa AI that provides an OpenAI-compatible interface for easy integration with Lexa's language models.

## Features

- 🔗 **OpenAI-Compatible**: Drop-in replacement for OpenAI SDK
- 🚀 **Async Support**: Full async/await support for high-performance applications
- 📦 **Type Safety**: Comprehensive type hints and validation
- 🔄 **Streaming**: Real-time streaming responses
- 🛡️ **Error Handling**: Robust error handling with custom exceptions
- 📊 **Multiple Models**: Support for all Lexa models (lexa-mml, lexa-x1, lexa-rho)

## Installation

```bash
pip install lexa-sdk
```

## Quick Start

```python
from lexa_sdk import Lexa

# Initialize the client
client = Lexa(api_key="your-api-key")

# Simple chat completion
response = client.chat.completions.create(
    model="lexa-mml",
    messages=[
        {"role": "user", "content": "Hello! Tell me a joke."}
    ],
    temperature=0.7,
    max_tokens=100
)

print(response["choices"][0]["message"]["content"])
```

## Available Models

| Model | Description | Context Window | Max Tokens |
|-------|-------------|----------------|------------|
| `lexa-mml` | Multimodal model with vision capabilities | 8,192 | 4,096 |
| `lexa-x1` | Fast, lightweight text-based model | 4,096 | 2,048 |
| `lexa-rho` | Reasoning model with enhanced capabilities | 16,384 | 8,192 |

## Documentation

For complete documentation, examples, and API reference, visit [docs.lexa.chat](https://docs.lexa.chat/).

## License

This project is licensed under the MIT License.
