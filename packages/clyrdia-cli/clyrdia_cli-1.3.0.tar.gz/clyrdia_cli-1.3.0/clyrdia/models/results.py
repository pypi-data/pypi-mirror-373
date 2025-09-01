"""
Result models for Clyrdia CLI benchmarking.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime

@dataclass
class BenchmarkResult:
    """Result from a single benchmark test"""
    model: str
    provider: str
    test_name: str
    prompt: str
    response: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    cost: float
    success: bool
    error: Optional[str] = None
    quality_scores: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestCase:
    """Definition of a benchmark test case"""
    name: str
    prompt: str
    expected_output: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    evaluation_criteria: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    weight: float = 1.0
