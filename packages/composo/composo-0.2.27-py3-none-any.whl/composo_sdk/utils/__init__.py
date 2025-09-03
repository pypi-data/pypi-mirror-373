"""
Utility functions and helpers
"""

import logging
from .validation import validate_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

__all__ = [
    # Validation
    "validate_api_key",
    "logger",
]
