"""
Adapter factory for creating appropriate format adapters
"""

from typing import Any, Optional
from .base import FormatAdapter
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter


class AdapterFactory:
    """Factory for creating format adapters based on result type"""

    _adapters = [
        OpenAIAdapter(),
        AnthropicAdapter(),
    ]

    @classmethod
    def get_adapter(cls, result: Any) -> Optional[FormatAdapter]:
        """Get appropriate adapter for the given result"""
        for adapter in cls._adapters:
            if adapter.can_handle(result):
                return adapter
        return None

    @classmethod
    def register_adapter(cls, adapter: FormatAdapter) -> None:
        """Register a new adapter"""
        cls._adapters.insert(0, adapter)  # Insert at beginning for priority

    @classmethod
    def get_all_adapters(cls) -> list[FormatAdapter]:
        """Get all registered adapters"""
        return cls._adapters.copy()
