"""
Type definitions for client parameters
"""

from typing import List, Union, Dict, Any, Optional
from typing_extensions import TypeAlias

# Import the actual types for result processing
from openai.types.chat.chat_completion import ChatCompletion
from anthropic.types.message import Message

# Simple dictionary tool format
ToolType = Dict[str, Any]

# Result format - can be OpenAI, Anthropic, dict, string, or None
ResultType: TypeAlias = Union[
    ChatCompletion,
    Message,
    Dict[str, Any],  # Generic result format
    str,  # Simple string result
    None,
]

# Type aliases for lists
MessagesType = List[Dict[str, str]]
ToolsType = Optional[List[ToolType]]
