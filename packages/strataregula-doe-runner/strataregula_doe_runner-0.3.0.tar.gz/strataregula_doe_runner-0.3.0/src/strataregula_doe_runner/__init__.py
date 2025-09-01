"""
Strataregula DOE Runner - Batch experiment orchestrator

This package provides functionality to execute predefined cases from CSV files
and collect standardized metrics, not to design experiments.

Core Components:
- Runner: Main execution engine
- Executor: Case execution management
- CSVHandler: Deterministic CSV I/O
- CaseCache: Result caching with case_hash
"""

__version__ = "0.1.0"
__author__ = "Strataregula Team"
__email__ = "support@strataregula.dev"

from .adapters.base import BaseAdapter
from .core.executor import CaseExecutor
from .core.runner import ExecutionResult, Runner
from .io.csv_handler import CSVHandler

# Plugin integration
try:
    from .plugin import DOERunnerPlugin

    _PLUGIN_AVAILABLE = True
except ImportError:
    _PLUGIN_AVAILABLE = False
    DOERunnerPlugin = None  # type: ignore

__all__ = [
    "Runner",
    "ExecutionResult",
    "CaseExecutor",
    "CSVHandler",
    "BaseAdapter",
    "__version__",
]

if _PLUGIN_AVAILABLE:
    __all__.append("DOERunnerPlugin")
