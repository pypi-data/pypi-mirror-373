"""
実行アダプター
"""

from typing import Any

from .base import BaseAdapter
from .dummy import DummyAdapter
from .shell import ShellAdapter

# simroute アダプターは extras 依存のため動的インポート
try:
    from .simroute import SimrouteAdapter

    _SIMROUTE_AVAILABLE = True
except ImportError:
    SimrouteAdapter = None
    _SIMROUTE_AVAILABLE = False

__all__ = [
    "BaseAdapter",
    "ShellAdapter",
    "DummyAdapter",
    "get_available_adapters",
]

if _SIMROUTE_AVAILABLE:
    __all__.append("SimrouteAdapter")


def get_available_adapters() -> dict[str, Any]:
    """利用可能なアダプターの情報を返す"""
    adapters = {
        "shell": {
            "name": "ShellAdapter",
            "description": "シェルコマンド実行アダプター",
            "available": True,
            "supported_features": [
                "command_execution",
                "metrics_parsing",
                "timeout_handling",
            ],
        },
        "dummy": {
            "name": "DummyAdapter",
            "description": "テスト用ダミーアダプター",
            "available": True,
            "supported_features": ["simulation", "deterministic_results", "testing"],
        },
        "simroute": {
            "name": "SimrouteAdapter",
            "description": "Simrouteシミュレーションアダプター",
            "available": _SIMROUTE_AVAILABLE,
            "supported_features": ["simulation", "routing_analysis"]
            if _SIMROUTE_AVAILABLE
            else [],
        },
    }

    return adapters
