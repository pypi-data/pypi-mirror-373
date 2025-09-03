# Sentinel Python SDK

[![PyPI](https://img.shields.io/pypi/v/yugenkairo-sentinel-sdk.svg)](https://pypi.org/project/yugenkairo-sentinel-sdk/)
[![License](https://img.shields.io/pypi/l/yugenkairo-sentinel-sdk.svg)](https://github.com/swayam8624/Sentinel/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/yugenkairo-sentinel-sdk.svg)](https://pypi.org/project/yugenkairo-sentinel-sdk/)

Python SDK for Sentinel - A self-healing LLM firewall with cryptographic data protection.

## Overview

The Sentinel Python SDK provides a secure interface to LLM providers through the Sentinel security pipeline. It acts as a drop-in replacement for popular LLM SDKs while adding enterprise-grade security features including:

- Real-time data redaction and tokenization
- Format-preserving encryption (FF3-1)
- Semantic violation detection
- Constitutional AI reflection
- Prompt rewriting and ranking
- Tool/function call guarding

## Installation

```bash
pip install yugenkairo-sentinel-sdk
```

## Quick Start

### Basic Usage

```python
from sentinel import SentinelClient

# Initialize the client
client = SentinelClient(
    base_url="http://localhost:8080",
    api_key="your-api-key"
)

# Send a chat completion request through Sentinel
response = client.chat_completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello, world!"}
    ]
)

print(response.choices[0].message.content)
```

### Advanced Usage

```python
from sentinel import SentinelClient

# Initialize with custom configuration
client = SentinelClient(
    base_url="http://localhost:8080",
    api_key="your-api-key",
    timeout=60
)

# Sanitize a prompt before sending to LLM
sanitized = client.sanitize_prompt("Process sensitive data: 123-45-6789")
print(f"Sanitized prompt: {sanitized['sanitizedPrompt']}")

# Process an LLM response for security
response = "Here's the sensitive information: 123-45-6789"
processed = client.process_response(response)
print(f"Processed response: {processed['processedResponse']}")
```

## Features

### 🔐 Data Protection

- Real-time data redaction/tokenization
- Format-preserving encryption (FF3-1)
- Reversible detokenization with policy gating
- Multi-language PII detection

### 🛡️ Self-Healing Security

- Semantic violation detection
- Constitutional AI reflection
- Prompt rewriting and ranking
- Tool/function call guarding

### 🔌 Provider Compatibility

- Drop-in replacement for OpenAI SDK
- Support for all major LLM providers
- Streaming support with mid-stream inspection
- Multi-tenant policy management

### ⚙️ Advanced Configuration

- Policy engine integration
- Custom security rules
- Audit trails and compliance reporting
- Observability with metrics and tracing

## API Reference

### SentinelClient

#### `__init__(base_url, api_key, timeout)`

Initialize the Sentinel client.

**Parameters:**

- `base_url` (str): The base URL for the Sentinel gateway (default: "http://localhost:8080")
- `api_key` (str, optional): API key for authentication
- `timeout` (int): Request timeout in seconds (default: 30)

#### `sanitize_prompt(prompt)`

Sanitize a prompt before sending to LLM.

**Parameters:**

- `prompt` (str): The prompt to sanitize

**Returns:**

- `dict`: Sanitized prompt and metadata

#### `process_response(response)`

Process an LLM response for security.

**Parameters:**

- `response` (str): The LLM response to process

**Returns:**

- `dict`: Processed response and metadata

#### `configure_policies(policies)`

Configure security policies.

**Parameters:**

- `policies` (dict): Policy configuration

**Returns:**

- `dict`: Policy update result

### ChatCompletions

#### `create(model, messages, temperature, max_tokens, **kwargs)`

Create a chat completion through the Sentinel gateway.

**Parameters:**

- `model` (str): The model to use
- `messages` (list): List of message dictionaries
- `temperature` (float, optional): Sampling temperature
- `max_tokens` (int, optional): Maximum tokens to generate
- `**kwargs`: Additional parameters

**Returns:**

- `dict`: Chat completion response

## Configuration

### Environment Variables

- `SENTINEL_BASE_URL`: Default base URL for the Sentinel gateway
- `SENTINEL_API_KEY`: Default API key for authentication
- `SENTINEL_TIMEOUT`: Default request timeout in seconds

### Configuration File

You can also configure the client using a configuration file:

```python
import os
from sentinel import SentinelClient

# Load configuration from environment
client = SentinelClient(
    base_url=os.getenv("SENTINEL_BASE_URL", "http://localhost:8080"),
    api_key=os.getenv("SENTINEL_API_KEY"),
    timeout=int(os.getenv("SENTINEL_TIMEOUT", "30"))
)
```

## Error Handling

The SDK raises standard Python exceptions:

```python
from sentinel import SentinelClient
import requests

client = SentinelClient(base_url="http://localhost:8080")

try:
    response = client.chat_completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
```

## Examples

### Multi-tenant Usage

```python
from sentinel import SentinelClient

# Different clients for different tenants
tenant_a_client = SentinelClient(
    base_url="http://localhost:8080",
    api_key="tenant-a-key"
)

tenant_b_client = SentinelClient(
    base_url="http://localhost:8080",
    api_key="tenant-b-key"
)
```

### Custom Policy Configuration

```python
from sentinel import SentinelClient

client = SentinelClient(base_url="http://localhost:8080")

# Configure custom policies
policies = {
    "pii_detection": {
        "enabled": True,
        "languages": ["en", "es", "fr"],
        "action": "tokenize"
    },
    "prompt_filtering": {
        "enabled": True,
        "threshold": 0.75
    }
}

result = client.configure_policies(policies)
print(f"Policies configured: {result['success']}")
```

## Integration with Popular Frameworks

### LangChain Integration

```python
from langchain.llms import Sentinel
from langchain.prompts import PromptTemplate

llm = Sentinel(
    base_url="http://localhost:8080",
    api_key="your-api-key"
)

template = "What is {subject}?"
prompt = PromptTemplate.from_template(template)
chain = prompt | llm

response = chain.invoke({"subject": "artificial intelligence"})
print(response)
```

### LlamaIndex Integration

```python
from llama_index.llms import Sentinel
from llama_index import VectorStoreIndex, SimpleDirectoryReader

llm = Sentinel(
    base_url="http://localhost:8080",
    api_key="your-api-key"
)

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents, llm=llm)
query_engine = index.as_query_engine()

response = query_engine.query("What did the author do growing up?")
print(response)
```

## Development

### Installation from Source

```bash
git clone https://github.com/swayam8624/Sentinel.git
cd Sentinel/sdk/python
pip install -e .
```

### Running Tests

```bash
pip install pytest
pytest tests/
```

### Code Formatting

```bash
pip install black flake8
black .
flake8 .
```

## Documentation

For full documentation, visit [https://swayam8624.github.io/Sentinel/](https://swayam8624.github.io/Sentinel/)

## Support

For issues, feature requests, or questions, please [open an issue](https://github.com/swayam8624/Sentinel/issues) on GitHub.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
