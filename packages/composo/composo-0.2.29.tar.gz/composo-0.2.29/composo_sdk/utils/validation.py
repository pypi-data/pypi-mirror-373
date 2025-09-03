"""
Input validation utilities
"""

from typing import Any, Optional
from ..exceptions import MalformedError


def validate_api_key(api_key: Optional[str]) -> None:
    """Validate API key format"""
    if not api_key:
        raise MalformedError("API key is required")

    if not isinstance(api_key, str) or len(api_key.strip()) == 0:
        raise MalformedError("API key must be a non-empty string")
