"""
Strataregula plugin integration for DOE Runner
"""

import logging
from typing import Any

from .core.cache import CaseCache
from .core.runner import Runner

logger = logging.getLogger(__name__)


class DOERunnerPlugin:
    """Strataregula plugin for DOE Runner batch experiment orchestrator."""

    # Plugin metadata
    name = "doe_runner"
    version = "0.1.0"
    description = "Batch experiment orchestrator for cases.csv → metrics.csv pipeline"
    author = "Strataregula Team"

    def __init__(self) -> None:
        """Initialize DOE Runner plugin."""
        self.runner: Runner | None = None
        self.cache = CaseCache()
        logger.info(f"Initialized {self.name} v{self.version}")

    def get_info(self) -> dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "supported_commands": [
                "execute_cases",
                "validate_cases",
                "get_cache_status",
                "clear_cache",
                "get_adapters",
            ],
            "supported_backends": ["shell", "dummy", "simroute"],
            "exit_codes": {
                "0": "All cases executed successfully",
                "2": "Threshold violations detected",
                "3": "Execution or configuration error",
            },
        }

    def execute_cases(
        self, cases_path: str, metrics_path: str = "metrics.csv", **options: Any
    ) -> dict[str, Any]:
        """Execute cases from CSV file."""
        try:
            config = {
                "max_workers": options.get("max_workers", 1),
                "fail_fast": options.get("fail_fast", False),
                "force_rerun": options.get("force", False),
                "dry_run": options.get("dry_run", False),
                "verbose": options.get("verbose", False),
                "run_log_dir": options.get("run_log_dir", "docs/run"),
                "compat_mode": options.get("compat_mode", False),
            }

            self.runner = Runner(**config)
            exit_code = self.runner.execute(cases_path, metrics_path)

            # エラーコードをチェック
            if exit_code == 3:
                return {
                    "status": "error",
                    "exit_code": exit_code,
                    "message": "File not found or execution failed",
                }

            # 統計情報をテストで期待される形式に変換
            stats: dict[str, Any] = self.runner.stats if self.runner else {}
            test_stats = {
                "total_cases": stats.get("total", 0),
                "successful": stats.get("success", 0),
                "failed": stats.get("failed", 0),
                "timeout": stats.get("timeout", 0),
                "threshold_violations": stats.get("threshold_violations", 0),
            }

            return {
                "status": "success",
                "exit_code": exit_code,
                "exit_meaning": self._get_exit_meaning(exit_code),
                "cases_path": cases_path,
                "metrics_path": metrics_path,
                "stats": test_stats,
            }

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {"status": "error", "exit_code": 3, "message": str(e)}

    def _get_exit_meaning(self, exit_code: int) -> str:
        """Get human-readable exit code meaning."""
        meanings = {
            0: "All cases executed successfully, thresholds met",
            2: "Execution completed but threshold violations detected",
            3: "I/O error, invalid configuration, or execution failure",
        }
        return meanings.get(exit_code, f"Unknown exit code: {exit_code}")

    def validate_cases(self, cases_path: str) -> dict[str, Any]:
        """Validate cases CSV file."""
        try:
            from .core.validator import CaseValidator
            from .io import CSVHandler

            csv_handler = CSVHandler()
            cases = csv_handler.load_cases(cases_path)

            validator = CaseValidator()
            errors = validator.validate_cases(cases)

            return {
                "status": "success",
                "valid": len(errors) == 0,
                "validation_details": {"total_cases": len(cases), "errors": errors},
            }
        except Exception as e:
            return {"status": "error", "valid": False, "message": str(e)}

    def get_cache_status(self, cases_path: str) -> dict[str, Any]:
        """Get cache status for cases."""
        try:
            # キャッシュヒット数を取得
            cache_hits = 0
            if self.runner and hasattr(self.runner, "cache"):
                # CaseCache.size()メソッドを使用
                cache_hits = self.runner.cache.size()

            return {
                "status": "success",
                "cache_hits": cache_hits,
                "cases_path": cases_path,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def clear_cache(self, cases_path: str) -> dict[str, Any]:
        """Clear cache for cases."""
        try:
            if self.runner and hasattr(self.runner, "cache"):
                self.runner.cache.clear()

            return {"status": "success", "message": "Cache cleared successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_adapters(self) -> dict[str, Any]:
        """Get available adapters information."""
        try:
            from .adapters import get_available_adapters

            adapters = get_available_adapters()
            return {"status": "success", "adapters": adapters}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Plugin factory function for strataregula
def create_plugin() -> DOERunnerPlugin:
    """Factory function to create plugin instance."""
    return DOERunnerPlugin()
