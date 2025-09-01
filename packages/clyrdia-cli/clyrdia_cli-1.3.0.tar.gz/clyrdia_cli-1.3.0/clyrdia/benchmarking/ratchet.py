"""
Ratchet system for Clyrdia CLI - handles performance monitoring and alerts.
"""

from typing import Dict, Any, List

class RatchetSystem:
    """Monitors performance and triggers alerts when thresholds are exceeded"""
    
    def __init__(self):
        self.thresholds = {}
        self.alert_history = []
    
    def set_threshold(self, metric: str, threshold: float, direction: str = "above"):
        """Set a performance threshold"""
        self.thresholds[metric] = {
            'value': threshold,
            'direction': direction
        }
    
    def check_threshold(self, metric: str, value: float) -> bool:
        """Check if a threshold has been exceeded"""
        if metric not in self.thresholds:
            return False
        
        threshold = self.thresholds[metric]
        if threshold['direction'] == "above":
            return value > threshold['value']
        else:
            return value < threshold['value']
    
    def record_alert(self, metric: str, value: float, threshold: float):
        """Record an alert when threshold is exceeded"""
        alert = {
            'metric': metric,
            'value': value,
            'threshold': threshold,
            'timestamp': 'now'
        }
        self.alert_history.append(alert)
