"""
Type definitions for Lexa SDK

This module contains all the data structures and type definitions
used throughout the SDK for API requests and responses.
"""

from typing import Dict, List, Union, Optional, Any, TypedDict, Literal
from dataclasses import dataclass


# Message content types
class TextContent(TypedDict):
    type: Literal["text"]
    text: str


class ImageContent(TypedDict):
    type: Literal["image_url"]
    image_url: Dict[str, str]  # {"url": "data:image/..."}


# Union type for message content
MessageContent = Union[str, List[Union[TextContent, ImageContent]]]


# Core message types
class LexaMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: MessageContent


# Response types
class LexaUsage(TypedDict, total=False):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LexaChoice(TypedDict):
    index: int
    message: LexaMessage
    finish_reason: Optional[str]


class LexaResponse(TypedDict):
    id: str
    object: str
    created: int
    model: str
    choices: List[LexaChoice]
    usage: Optional[LexaUsage]


# Streaming types
class LexaStreamDelta(TypedDict, total=False):
    role: Optional[str]
    content: Optional[str]


class LexaStreamChoice(TypedDict):
    index: int
    delta: LexaStreamDelta
    finish_reason: Optional[str]


class LexaStreamChunk(TypedDict):
    id: str
    object: str
    created: int
    model: str
    choices: List[LexaStreamChoice]
    usage: Optional[LexaUsage]


# Model information
@dataclass
class ModelInfo:
    id: str
    name: str
    description: str
    context_window: int
    max_tokens: int


# Available models configuration
LEXA_MODELS: Dict[str, ModelInfo] = {
    'lexa-mml': ModelInfo(
        id='lexa-mml',
        name='Lexa MML',
        description='Multimodal model with vision capabilities',
        context_window=8192,
        max_tokens=4096,
    ),
    'lexa-x1': ModelInfo(
        id='lexa-x1',
        name='Lexa X1',
        description='Fast, lightweight text-based model',
        context_window=4096,
        max_tokens=2048,
    ),
    'lexa-rho': ModelInfo(
        id='lexa-rho',
        name='Lexa Rho',
        description='Reasoning model with enhanced capabilities',
        context_window=16384,
        max_tokens=8192,
    ),
}


# Request parameter types
class ChatCompletionRequest(TypedDict, total=False):
    model: str
    messages: List[LexaMessage]
    temperature: Optional[float]
    max_tokens: Optional[int]
    top_p: Optional[float]
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]
    stop: Optional[Union[str, List[str]]]
    stream: Optional[bool]
    user: Optional[str]
