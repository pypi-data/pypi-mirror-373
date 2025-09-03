"""
OpenAI format adapter
"""

from typing import List, Dict, Any, Optional
from .base import FormatAdapter
from ..client.types import MessagesType, ToolsType, ResultType

# Import OpenAI types for type checking
from openai.types.chat.chat_completion import ChatCompletion


class OpenAIAdapter(FormatAdapter):
    """Adapter for OpenAI format"""

    def can_handle(self, result: ResultType) -> bool:
        """Check if this adapter can handle the given result type"""
        # Check if result is OpenAI ChatCompletion using type checking
        return isinstance(result, ChatCompletion)

    def process_result(
        self,
        messages: MessagesType,
        result: ResultType,
        system: Optional[str] = None,
        tools: ToolsType = None,
    ) -> tuple[List[Dict[str, Any]], Optional[str], Optional[List[Dict[str, Any]]]]:
        """Process OpenAI format result by preserving original structure"""
        if not self.can_handle(result):
            return messages, system, tools

        # Extract the message from OpenAI result and preserve its structure
        if hasattr(result, "choices") and result.choices:
            choice = result.choices[0]
            if hasattr(choice, "message"):
                # Use model_dump() to preserve the original structure, excluding None values
                message_dict = choice.message.model_dump(exclude_none=True)
                messages.append(message_dict)

        return messages, system, tools
