# Lexa Provider Architecture Guide

## Overview

The `@robilabs/lexa` package is a JavaScript/TypeScript SDK that provides both:
1. **AI SDK v2 Compatible Provider** - For integration with Vercel's AI SDK
2. **OpenAI-style Interface** - For drop-in replacement of OpenAI SDK

## Core Architecture

### 1. Provider Structure (AI SDK v2 Compatible)

```
src/
├── lexa-provider.ts      # Main provider class implementing ProviderV2
├── lexa-language-model.ts # Language model implementation
├── types.ts              # TypeScript interfaces
└── index.ts              # Main exports + OpenAI-style wrapper
```

### 2. Key Components

#### **LexaProvider** (`src/lexa-provider.ts`)
- Implements `ProviderV2` interface from `@ai-sdk/provider`
- Factory for creating language models
- Contains predefined model configurations

```typescript
export class LexaProvider implements ProviderV2 {
  languageModel(modelId: string): LanguageModelV2
  textEmbeddingModel(modelId: string): EmbeddingModelV2<string> // Not implemented
  imageModel(modelId: string): ImageModelV2 // Not implemented
}
```

#### **LexaLanguageModel** (`src/lexa-language-model.ts`)
- Implements `LanguageModelV2` interface
- Handles API communication with Lexa backend
- Converts between AI SDK format and Lexa API format
- Supports both streaming and non-streaming responses

```typescript
export class LexaLanguageModel implements LanguageModelV2 {
  async doGenerate(options: LanguageModelV2CallOptions): Promise<...>
  async doStream(options: LanguageModelV2CallOptions): Promise<...>
}
```

#### **OpenAI-style Wrapper** (`src/index.ts`)
- Provides familiar OpenAI API interface
- Converts OpenAI format to AI SDK format internally
- Main export for easy consumption

```typescript
class Lexa {
  async chat(options): Promise<OpenAI-like-response>
  async models(): Promise<models-list>
}
```

## API Integration

### Base Configuration
- **Base URL**: `https://www.lexa.chat/api`
- **Endpoint**: `/chat/completions`
- **Authentication**: Bearer token in Authorization header
- **Format**: OpenAI-compatible API

### Available Models
```javascript
const LEXA_MODELS = {
  'lexa-mml': {
    name: 'Lexa MML',
    description: 'Multimodal model with vision capabilities',
    contextWindow: 8192,
    maxTokens: 4096,
  },
  'lexa-x1': {
    name: 'Lexa X1', 
    description: 'Fast, lightweight text-based model',
    contextWindow: 4096,
    maxTokens: 2048,
  },
  'lexa-rho': {
    name: 'Lexa Rho',
    description: 'Reasoning model with enhanced capabilities',
    contextWindow: 16384,
    maxTokens: 8192,
  },
}
```

## Message Format Conversion

### Input: AI SDK v2 Format
```typescript
interface LanguageModelV2Prompt {
  role: 'system' | 'user' | 'assistant';
  content: Array<{
    type: 'text' | 'file';
    text?: string;
    data?: string; // For images
  }>;
}
```

### Output: Lexa API Format
```typescript
interface LexaMessage {
  role: 'system' | 'user' | 'assistant';
  content: string | Array<{
    type: 'text' | 'image_url';
    text?: string;
    image_url?: { url: string };
  }>;
}
```

### OpenAI-style Input
```typescript
interface OpenAIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}
```

## Response Handling

### Non-streaming Response
```typescript
interface LexaResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: LexaMessage;
    finish_reason: string;
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}
```

### Streaming Response
- Server-Sent Events (SSE) format
- Each chunk: `data: {JSON}\n\n`
- Final chunk: `data: [DONE]\n\n`
- Chunks contain delta updates

## Error Handling

### Custom Error Types
```typescript
class TooManyRequestsError extends Error {
  constructor(public retryAfter?: number)
}

// Uses AI SDK's APICallError for other errors
```

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (invalid API key)
- `429`: Rate Limited
- `500`: Server Error

## Python SDK Implementation Guide

### 1. Core Structure
```python
lexa_sdk/
├── __init__.py           # Main exports
├── provider.py           # LexaProvider class
├── language_model.py     # LexaLanguageModel class
├── types.py              # Data classes/TypedDict
├── client.py             # OpenAI-style wrapper
└── exceptions.py         # Custom exceptions
```

### 2. Key Classes to Implement

#### **LexaProvider**
```python
class LexaProvider:
    def __init__(self, api_key: str, base_url: str = "https://www.lexa.chat/api"):
        self.api_key = api_key
        self.base_url = base_url
    
    def language_model(self, model_id: str) -> LexaLanguageModel:
        return LexaLanguageModel(model_id, self.api_key, self.base_url)
```

#### **LexaLanguageModel**
```python
class LexaLanguageModel:
    def generate(self, messages: List[Dict], **kwargs) -> Dict:
        # Non-streaming generation
    
    def stream(self, messages: List[Dict], **kwargs) -> Iterator[Dict]:
        # Streaming generation
    
    async def agenerate(self, messages: List[Dict], **kwargs) -> Dict:
        # Async non-streaming
    
    async def astream(self, messages: List[Dict], **kwargs) -> AsyncIterator[Dict]:
        # Async streaming
```

#### **OpenAI-style Client**
```python
class Lexa:
    def __init__(self, api_key: str, base_url: str = "https://www.lexa.chat/api"):
        self.provider = LexaProvider(api_key, base_url)
    
    def chat(self, messages: List[Dict], model: str = "lexa-mml", **kwargs) -> Dict:
        # OpenAI-compatible interface
    
    def models(self) -> Dict:
        # List available models
```

### 3. Dependencies
```python
# requirements.txt
requests>=2.25.0          # HTTP client
httpx>=0.24.0            # Async HTTP client  
pydantic>=2.0.0          # Data validation
typing-extensions>=4.0.0 # Type hints
```

### 4. Package Structure
```python
# __init__.py
from .client import Lexa
from .provider import LexaProvider
from .language_model import LexaLanguageModel
from .types import (
    LexaMessage,
    LexaResponse,
    LexaStreamChunk,
    ModelInfo,
)
from .exceptions import (
    LexaError,
    LexaAPIError,
    LexaRateLimitError,
)

__version__ = "1.0.0"
__all__ = [
    "Lexa",
    "LexaProvider", 
    "LexaLanguageModel",
    "LexaMessage",
    "LexaResponse",
    "LexaStreamChunk",
    "ModelInfo",
    "LexaError",
    "LexaAPIError", 
    "LexaRateLimitError",
]
```

### 5. Key Implementation Details

#### **HTTP Client Setup**
```python
import httpx

class LexaLanguageModel:
    def __init__(self, model_id: str, api_key: str, base_url: str):
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
```

#### **Message Conversion**
```python
def convert_to_lexa_format(messages: List[Dict]) -> List[Dict]:
    """Convert OpenAI format to Lexa API format"""
    lexa_messages = []
    for msg in messages:
        lexa_msg = {
            "role": msg["role"],
            "content": msg["content"]
        }
        lexa_messages.append(lexa_msg)
    return lexa_messages
```

#### **Streaming Implementation**
```python
def stream(self, messages: List[Dict], **kwargs) -> Iterator[Dict]:
    payload = {
        "model": self.model_id,
        "messages": messages,
        "stream": True,
        **kwargs
    }
    
    with httpx.stream(
        "POST",
        f"{self.base_url}/chat/completions",
        headers=self.headers,
        json=payload
    ) as response:
        for line in response.iter_lines():
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    yield chunk
                except json.JSONDecodeError:
                    continue
```

### 6. Usage Examples

#### **Basic Usage**
```python
from lexa_sdk import Lexa

# Initialize client
lexa = Lexa(api_key="your-api-key")

# Simple chat
response = lexa.chat(
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
    model="lexa-mml",
    temperature=0.7,
    max_tokens=100
)

print(response["choices"][0]["message"]["content"])
```

#### **Streaming Usage**
```python
response = lexa.chat(
    messages=[{"role": "user", "content": "Write a story"}],
    model="lexa-rho", 
    stream=True
)

for chunk in response:
    if "choices" in chunk and chunk["choices"]:
        delta = chunk["choices"][0].get("delta", {})
        if "content" in delta:
            print(delta["content"], end="")
```

### 7. Testing Strategy
```python
# tests/test_client.py
def test_basic_chat():
    lexa = Lexa(api_key="test-key")
    # Mock the HTTP call
    response = lexa.chat(messages=[{"role": "user", "content": "test"}])
    assert "choices" in response

def test_streaming():
    lexa = Lexa(api_key="test-key") 
    chunks = list(lexa.chat(
        messages=[{"role": "user", "content": "test"}],
        stream=True
    ))
    assert len(chunks) > 0
```

### 8. Publishing Setup
```python
# setup.py or pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "lexa-sdk"
version = "1.0.0"
description = "Python SDK for Lexa AI"
authors = [{name = "Robi Labs", email = "lexa@robiai.com"}]
license = {text = "MIT"}
dependencies = [
    "requests>=2.25.0",
    "httpx>=0.24.0", 
    "pydantic>=2.0.0",
    "typing-extensions>=4.0.0",
]

[project.urls]
Homepage = "https://lexa.chat"
Repository = "https://github.com/Robi-Labs/lexa-python-sdk"
Documentation = "https://docs.lexa.chat/"
```

## Key Implementation Notes

1. **Authentication**: Always use Bearer token in Authorization header
2. **Error Handling**: Implement proper HTTP status code handling with custom exceptions
3. **Rate Limiting**: Handle 429 responses with retry-after headers
4. **Streaming**: Use Server-Sent Events format parsing
5. **Type Safety**: Use TypedDict/Pydantic for data validation
6. **Async Support**: Provide both sync and async interfaces
7. **OpenAI Compatibility**: Maintain familiar API surface for easy migration

This architecture provides a solid foundation for implementing the Python SDK with the same capabilities and interface patterns as the JavaScript version.
