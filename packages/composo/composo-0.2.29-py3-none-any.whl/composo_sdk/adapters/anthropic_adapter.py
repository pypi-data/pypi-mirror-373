"""
Anthropic format adapter
"""

from typing import List, Dict, Any, Optional
from .base import FormatAdapter
from ..client.types import MessagesType, ToolsType, ResultType

# Import Anthropic types for type checking
from anthropic.types.message import Message


class AnthropicAdapter(FormatAdapter):
    """Adapter for Anthropic format"""

    def can_handle(self, result: ResultType) -> bool:
        """Check if result is Anthropic Message using type checking"""
        return isinstance(result, Message)

    def process_result(
        self,
        messages: MessagesType,
        result: ResultType,
        system: Optional[str] = None,
        tools: ToolsType = None,
    ) -> tuple[List[Dict[str, Any]], Optional[str], Optional[List[Dict[str, Any]]]]:
        if not self.can_handle(result):
            return messages, system, tools
        # Match notebook behavior: directly append without field filtering, excluding None values
        messages.append(result.model_dump(exclude_none=True))
        return messages, system, tools
