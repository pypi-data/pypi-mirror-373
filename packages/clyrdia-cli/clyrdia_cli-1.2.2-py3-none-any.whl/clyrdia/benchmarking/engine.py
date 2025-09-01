"""
Benchmark engine for Clyrdia CLI - handles benchmark execution.
"""

import asyncio
import uuid
from typing import List, Dict, Any
from datetime import datetime

from ..models.results import BenchmarkResult, TestCase
from ..models.config import ClyrdiaConfig
from .interface import ModelInterface
from .evaluator import QualityEvaluator
from ..caching.manager import CacheManager
from ..database.local_db import LocalDatabase

class BenchmarkEngine:
    """Main engine for running benchmarks"""
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.model_interface = ModelInterface(api_keys)
        self.quality_evaluator = QualityEvaluator()
        self.cache_manager = CacheManager()
        self.database = LocalDatabase()
    
    async def run_benchmark(self, test_cases: List[TestCase], models: List[str], 
                           use_cache: bool = True) -> List[BenchmarkResult]:
        """Run a benchmark with the specified test cases and models"""
        benchmark_id = str(uuid.uuid4())
        results = []
        
        for test_case in test_cases:
            for model in models:
                # Check cache first
                if use_cache:
                    cached_result = self.cache_manager.get_cached_result(
                        model, test_case.name, test_case.prompt,
                        test_case.max_tokens, test_case.temperature
                    )
                    if cached_result:
                        # Convert cached result to BenchmarkResult
                        result = BenchmarkResult(
                            model=model,
                            provider="cached",
                            test_name=test_case.name,
                            prompt=test_case.prompt,
                            response=cached_result.response,
                            latency_ms=0,
                            input_tokens=cached_result.input_tokens,
                            output_tokens=cached_result.output_tokens,
                            cost=0.0,
                            success=True,
                            quality_scores=cached_result.quality_scores,
                            metadata=cached_result.metadata
                        )
                        results.append(result)
                        continue
                
                # Run live test
                result = await self.model_interface.run_test(
                    model, test_case.prompt, test_case.max_tokens, test_case.temperature
                )
                result.test_name = test_case.name
                
                # Evaluate quality
                quality_scores = self.quality_evaluator.evaluate_response(
                    test_case.prompt, result.response, test_case.expected_output
                )
                result.quality_scores = quality_scores
                
                # Cache the result
                self.cache_manager.cache_result(
                    model, test_case.name, test_case.prompt, result.response,
                    result.input_tokens, result.output_tokens, quality_scores,
                    test_case.max_tokens, test_case.temperature, result.metadata
                )
                
                # Save to database
                self.database.save_result(result, benchmark_id)
                
                results.append(result)
        
        return results
