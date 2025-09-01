"""
Clyrdia CLI - Zero-Knowledge AI Benchmarking Platform
"""

__version__ = "1.3.1"
__author__ = "Clyrdia Team"
__email__ = "dev@clyrdia.com"
__url__ = "https://clyrdia.com"

# Import main components for easy access
from .cli_modular import app
from .benchmarking.engine import BenchmarkEngine
from .models.config import ClyrdiaConfig

__all__ = [
    "app",
    "BenchmarkEngine", 
    "ClyrdiaConfig",
    "__version__",
    "__author__",
    "__email__"
]
