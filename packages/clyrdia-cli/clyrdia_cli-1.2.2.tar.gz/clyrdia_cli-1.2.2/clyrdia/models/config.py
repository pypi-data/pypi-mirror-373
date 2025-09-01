"""
Configuration models for Clyrdia CLI.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from .enums import ModelProvider

@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    name: str
    provider: ModelProvider
    input_cost: float  # per 1M tokens
    output_cost: float  # per 1M tokens
    max_tokens: int
    context_window: int
    capabilities: List[str] = field(default_factory=list)
    speed_tier: str = "standard"  # fast, standard, slow
    tier: str = "balanced"  # flagship, balanced, speed_cost
    
    # Additional cost parameters for different token ranges (only for live API calls)
    input_cost_over_200k: Optional[float] = None  # per 1M tokens
    output_cost_over_200k: Optional[float] = None  # per 1M tokens

class ClyrdiaConfig:
    """Global configuration management"""
    
    # Model catalog with 2025 latest models
    # All prices are USD per 1M tokens (or per 1K searches where noted).
    MODELS = {
    # ---------- OpenAI ----------
    "gpt-5": ModelConfig(
        name="gpt-5",
        provider=ModelProvider.OPENAI,
        input_cost=1.25,
        output_cost=10.00,
        max_tokens=128000, context_window=128000,
        capabilities=["chat","code","vision","function_calling"], speed_tier="standard", tier="flagship"
    ),
    "gpt-5-mini": ModelConfig(
        name="gpt-5-mini",
        provider=ModelProvider.OPENAI,
        input_cost=0.25,
        output_cost=2.00,
        max_tokens=128000, context_window=128000,
        capabilities=["chat","code"], speed_tier="fast", tier="balanced"
    ),
    "gpt-5-nano": ModelConfig(
        name="gpt-5-nano",
        provider=ModelProvider.OPENAI,
        input_cost=0.05,
        output_cost=0.40,
        max_tokens=128000, context_window=128000,
        capabilities=["chat"], speed_tier="fastest", tier="speed_cost"
    ),
    "gpt-4.1": ModelConfig(
        name="gpt-4.1",
        provider=ModelProvider.OPENAI,
        input_cost=2.00,
        output_cost=8.00,
        max_tokens=128000, context_window=128000,
        capabilities=["chat","code","vision"], speed_tier="standard", tier="flagship"
    ),
    "gpt-4.1-mini": ModelConfig(
        name="gpt-4.1-mini",
        provider=ModelProvider.OPENAI,
        input_cost=0.40,
        output_cost=1.60,
        max_tokens=128000, context_window=128000,
        capabilities=["chat","code"], speed_tier="fast", tier="balanced"
    ),
    "gpt-4.1-nano": ModelConfig(
        name="gpt-4.1-nano",
        provider=ModelProvider.OPENAI,
        input_cost=0.10,
        output_cost=0.40,
        max_tokens=128000, context_window=128000,
        capabilities=["chat"], speed_tier="fast", tier="speed_cost"
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        provider=ModelProvider.OPENAI,
        input_cost=2.50,
        output_cost=10.00,
        max_tokens=128000, context_window=128000,
        capabilities=["chat","code","vision","function_calling","multimodal"], speed_tier="fast", tier="flagship"
    ),
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        provider=ModelProvider.OPENAI,
        input_cost=0.15,
        output_cost=0.60,
        max_tokens=128000, context_window=128000,
        capabilities=["chat","code"], speed_tier="fast", tier="balanced"
    ),
    "gpt-4o-2024-08-01": ModelConfig(
        name="gpt-4o-2024-08-01",  # Correct API model name
        provider=ModelProvider.OPENAI,
        input_cost=2.50,
        output_cost=10.00,
        max_tokens=128000, context_window=128000,
        capabilities=["chat","code","vision","function_calling","multimodal"], speed_tier="fast", tier="flagship"
    ),

    # ---------- Anthropic (Claude) ----------
    "claude-opus-4.1": ModelConfig(
        name="claude-opus-4-1-20250805",  # API model name
        provider=ModelProvider.ANTHROPIC,
        input_cost=15.00,
        output_cost=75.00,
        max_tokens=200000, context_window=200000,
        capabilities=["chat","code","analysis","creative","multimodal"], speed_tier="standard", tier="flagship"
    ),
    "claude-sonnet-4": ModelConfig(
        name="claude-sonnet-4-20250514",
        provider=ModelProvider.ANTHROPIC,
        input_cost=3.00,                 # ≤200k prompt
        output_cost=15.00,               # ≤200k prompt
        input_cost_over_200k=6.00,       # >200k prompt
        output_cost_over_200k=22.50,     # >200k prompt
        max_tokens=200000, context_window=200000,
        capabilities=["chat","code","analysis","multimodal"], speed_tier="fast", tier="balanced"
    ),
    "claude-haiku-3.5": ModelConfig(
        name="claude-3-5-haiku-20241022",
        provider=ModelProvider.ANTHROPIC,
        input_cost=0.80,
        output_cost=4.00,
        max_tokens=200000, context_window=200000,
        capabilities=["chat","code"], speed_tier="fastest", tier="speed_cost"
    ),
    }
    
    @classmethod
    def get_model(cls, name: str) -> Optional[ModelConfig]:
        return cls.MODELS.get(name)
    
    @classmethod
    def list_models(cls) -> List[str]:
        return list(cls.MODELS.keys())

def get_model_configs() -> Dict[str, ModelConfig]:
    """Get all model configurations (OpenAI and Anthropic only)"""
    return ClyrdiaConfig.MODELS
