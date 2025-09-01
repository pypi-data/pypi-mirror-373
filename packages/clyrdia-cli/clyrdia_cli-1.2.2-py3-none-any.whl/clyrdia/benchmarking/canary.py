"""
Canary system for Clyrdia CLI - handles early warning detection.
"""

from typing import Dict, Any, List

class CanarySystem:
    """Provides early warning detection for model performance issues"""
    
    def __init__(self):
        self.canary_tests = {}
        self.baseline_metrics = {}
    
    def add_canary_test(self, name: str, test_config: Dict[str, Any]):
        """Add a canary test for monitoring"""
        self.canary_tests[name] = test_config
    
    def set_baseline(self, model: str, metrics: Dict[str, float]):
        """Set baseline metrics for a model"""
        self.baseline_metrics[model] = metrics
    
    def check_canary_health(self, model: str, current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Check if canary tests indicate health issues"""
        if model not in self.baseline_metrics:
            return {'healthy': True, 'warnings': []}
        
        baseline = self.baseline_metrics[model]
        warnings = []
        
        for metric, current_value in current_metrics.items():
            if metric in baseline:
                baseline_value = baseline[metric]
                # Simple threshold check (20% degradation)
                if current_value < baseline_value * 0.8:
                    warnings.append(f"{metric} degraded by {((baseline_value - current_value) / baseline_value * 100):.1f}%")
        
        return {
            'healthy': len(warnings) == 0,
            'warnings': warnings
        }
