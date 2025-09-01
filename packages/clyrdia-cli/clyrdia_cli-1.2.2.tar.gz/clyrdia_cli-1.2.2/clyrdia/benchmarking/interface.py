"""
Model interface for Clyrdia CLI - handles communication with AI providers.
"""

import time
import asyncio
from typing import Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
import anthropic

from ..models.enums import ModelProvider
from ..models.config import ModelConfig, ClyrdiaConfig
from ..models.results import BenchmarkResult

class ModelInterface:
    """Interface for communicating with AI model providers"""
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self._setup_clients()
    
    def _setup_clients(self):
        """Setup API clients for different providers"""
        if 'openai' in self.api_keys:
            self.openai_client = AsyncOpenAI(api_key=self.api_keys['openai'])
        
        if 'anthropic' in self.api_keys:
            self.anthropic_client = anthropic.Anthropic(api_key=self.api_keys['anthropic'])
    
    async def run_test(self, model: str, prompt: str, max_tokens: int = 1000, 
                      temperature: float = 0.7) -> BenchmarkResult:
        """Run a single test with the specified model"""
        start_time = time.perf_counter()  # More precise timing
        
        try:
            model_config = ClyrdiaConfig.get_model(model)
            if not model_config:
                raise ValueError(f"Unknown model: {model}")
            
            if model_config.provider == ModelProvider.OPENAI:
                response, input_tokens, output_tokens = await self._call_openai(model_config.name, prompt, max_tokens, temperature)
            elif model_config.provider == ModelProvider.ANTHROPIC:
                response, input_tokens, output_tokens = await self._call_anthropic(model_config.name, prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Unsupported provider: {model_config.provider}")
            
            # Calculate precise latency
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            
            # Calculate accurate cost using actual token counts
            cost = self._calculate_cost(model_config, input_tokens, output_tokens)
            
            return BenchmarkResult(
                model=model,
                provider=model_config.provider.value,
                test_name="manual_test",
                prompt=prompt,
                response=response,
                latency_ms=latency_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                success=True
            )
            
        except Exception as e:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            return BenchmarkResult(
                model=model,
                provider="unknown",
                test_name="manual_test",
                prompt=prompt,
                response="",
                latency_ms=latency_ms,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                success=False,
                error=str(e)
            )
    
    async def _call_openai(self, model: str, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, int, int]:
        """Call OpenAI API and return response with token counts"""
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Extract actual token counts from API response
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        return response.choices[0].message.content, input_tokens, output_tokens
    
    async def _call_anthropic(self, model: str, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, int, int]:
        """Call Anthropic API and return response with token counts"""
        # Anthropic client is synchronous, so we need to run it in a thread
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def _call_sync():
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response
        
        # Run the synchronous call in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            response = await loop.run_in_executor(executor, _call_sync)
        
        # Extract actual token counts from API response
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        
        return response.content[0].text, input_tokens, output_tokens
    
    def _calculate_cost(self, model_config: ModelConfig, input_tokens: int, output_tokens: int) -> float:
        """Calculate accurate cost for the API call using actual token counts"""
        # Convert to millions for cost calculation
        input_cost = (input_tokens / 1_000_000) * model_config.input_cost
        output_cost = (output_tokens / 1_000_000) * model_config.output_cost
        
        # Round to 6 decimal places for precision
        total_cost = round(input_cost + output_cost, 6)
        
        return total_cost
