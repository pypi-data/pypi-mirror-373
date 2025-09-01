"""
Cache management for Clyrdia CLI - handles result caching and optimization.
"""

import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .models import CachedResult
from ..models.results import TestCase

class CacheManager:
    """Manages caching for benchmark results"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or (Path.home() / ".clyrdia" / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_db = self.cache_dir / "cache.db"
        self._init_cache_db()
    
    def _init_cache_db(self):
        """Initialize the cache database"""
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cached_results (
                    cache_key TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL,
                    quality_scores TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def _generate_cache_key(self, model: str, test_name: str, prompt: str, 
                           max_tokens: int, temperature: float) -> str:
        """Generate a unique cache key for a test run"""
        # Create a hash based on all parameters that affect the result
        content = f"{model}:{test_name}:{prompt.strip()}:{max_tokens}:{temperature}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_cached_result(self, model: str, test_name: str, prompt: str,
                         max_tokens: int, temperature: float) -> Optional[CachedResult]:
        """Get a cached result if it exists"""
        cache_key = self._generate_cache_key(model, test_name, prompt, max_tokens, temperature)
        
        with sqlite3.connect(self.cache_db) as conn:
            cursor = conn.execute(
                "SELECT * FROM cached_results WHERE cache_key = ?",
                (cache_key,)
            )
            row = cursor.fetchone()
            
            if row:
                return CachedResult(
                    cache_key=row[0],
                    model=row[1],
                    test_name=row[2],
                    prompt=row[3],
                    response=row[4],
                    input_tokens=row[5],
                    output_tokens=row[6],
                    quality_scores=json.loads(row[7]),
                    timestamp=datetime.fromisoformat(row[8]),
                    metadata=json.loads(row[9])
                )
        return None
    
    def cache_result(self, model: str, test_name: str, prompt: str,
                    response: str, input_tokens: int, output_tokens: int,
                    quality_scores: Dict[str, float], max_tokens: int,
                    temperature: float, metadata: Dict[str, Any]):
        """Cache a benchmark result"""
        cache_key = self._generate_cache_key(model, test_name, prompt, max_tokens, temperature)
        
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cached_results 
                (cache_key, model, test_name, prompt, response, input_tokens, 
                 output_tokens, quality_scores, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cache_key, model, test_name, prompt, response, input_tokens,
                output_tokens, json.dumps(quality_scores), 
                datetime.now().isoformat(), json.dumps(metadata)
            ))
            conn.commit()
    
    def clear_cache(self, model: Optional[str] = None):
        """Clear all cache or cache for a specific model"""
        with sqlite3.connect(self.cache_db) as conn:
            if model:
                conn.execute("DELETE FROM cached_results WHERE model = ?", (model,))
            else:
                conn.execute("DELETE FROM cached_results")
            conn.commit()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with sqlite3.connect(self.cache_db) as conn:
            # Total entries
            total = conn.execute("SELECT COUNT(*) FROM cached_results").fetchone()[0]
            
            # Size by model
            model_counts = {}
            cursor = conn.execute(
                "SELECT model, COUNT(*) FROM cached_results GROUP BY model"
            )
            for row in cursor.fetchall():
                model_counts[row[0]] = row[1]
            
            # Cache size on disk
            cache_size = self.cache_db.stat().st_size if self.cache_db.exists() else 0
            
            return {
                "total_entries": total,
                "model_counts": model_counts,
                "cache_size_bytes": cache_size,
                "cache_size_mb": round(cache_size / (1024 * 1024), 2)
            }
    
    def get_cache_hit_rate(self, test_cases: List[TestCase], models: List[str]) -> Dict[str, float]:
        """Calculate potential cache hit rate for a benchmark run"""
        total_tests = len(test_cases) * len(models)
        cacheable_tests = 0
        
        for test_case in test_cases:
            for model in models:
                if self.get_cached_result(model, test_case.name, test_case.prompt, 
                                        test_case.max_tokens, test_case.temperature):
                    cacheable_tests += 1
        
        return {
            "total_tests": total_tests,
            "cacheable_tests": cacheable_tests,
            "hit_rate": cacheable_tests / total_tests if total_tests > 0 else 0
        }

    def get_all_cached_results(self) -> List[CachedResult]:
        """Get all cached results for analysis"""
        results = []
        with sqlite3.connect(self.cache_db) as conn:
            cursor = conn.execute("SELECT * FROM cached_results")
            for row in cursor.fetchall():
                try:
                    result = CachedResult(
                        cache_key=row[0],
                        model=row[1],
                        test_name=row[2],
                        prompt=row[3],
                        response=row[4],
                        input_tokens=row[5],
                        output_tokens=row[6],
                        quality_scores=json.loads(row[7]),
                        timestamp=datetime.fromisoformat(row[8]),
                        metadata=json.loads(row[9])
                    )
                    results.append(result)
                except Exception as e:
                    print(f"Warning: Could not parse cached result: {e}")
                    continue
        return results

    def clear_model_cache(self, model: str):
        """Clear cache for a specific model"""
        try:
            with sqlite3.connect(self.cache_db) as conn:
                conn.execute("DELETE FROM cached_results WHERE model = ?", (model,))
                conn.commit()
            print(f"✅ Cache cleared for model: {model}")
        except Exception as e:
            print(f"❌ Error clearing cache for model {model}: {str(e)}")
