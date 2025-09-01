"""
Caching models for Clyrdia CLI.
"""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class CachedResult:
    """Cached benchmark result"""
    cache_key: str
    model: str
    test_name: str
    prompt: str
    response: str
    input_tokens: int
    output_tokens: int
    quality_scores: Dict[str, float]
    timestamp: datetime
    metadata: Dict[str, Any]
    
    @property
    def cost(self) -> float:
        """Calculate cost based on input and output tokens"""
        # Default costs for calculation (can be overridden)
        input_cost_per_1m = 0.15  # Default to gpt-4o-mini rates
        output_cost_per_1m = 0.60
        input_cost = (self.input_tokens * input_cost_per_1m) / 1_000_000
        output_cost = (self.output_tokens * output_cost_per_1m) / 1_000_000
        return input_cost + output_cost
    
    @property
    def quality_score(self) -> float:
        """Get average quality score"""
        if not self.quality_scores:
            return 0.0
        return sum(self.quality_scores.values()) / len(self.quality_scores)
