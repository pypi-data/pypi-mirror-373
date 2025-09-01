"""
Enums for Clyrdia CLI data models.
"""

from enum import Enum

class ModelProvider(Enum):
    """Supported AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
