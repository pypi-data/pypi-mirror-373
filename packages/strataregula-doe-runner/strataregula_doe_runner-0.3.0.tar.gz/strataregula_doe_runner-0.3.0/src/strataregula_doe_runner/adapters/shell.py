"""
シェルコマンド実行アダプター
"""

import re
import subprocess
import time
from typing import Any

from .base import BaseAdapter


class TemplateEngine:
    """簡単なテンプレート展開エンジン"""

    def expand(self, template: str, context: dict[str, Any]) -> str:
        """
        テンプレート文字列中の {key} を context[key] で置換
        """
        result = template
        for key, value in context.items():
            if key not in ["cmd_template"]:  # cmd_template自体は展開しない
                placeholder = f"{{{key}}}"
                if placeholder in result:
                    result = result.replace(placeholder, str(value))
        return result


class ShellAdapter(BaseAdapter):
    """シェルコマンドを実行するアダプター"""

    def __init__(self) -> None:
        self.template_engine = TemplateEngine()

    def execute(self, case: dict[str, Any]) -> dict[str, Any]:
        """
        シェルコマンドを実行してメトリクスを解析

        コマンド出力から以下の形式でメトリクスを抽出:
        - p95=0.123
        - p99=0.456
        - throughput_rps=1000.0
        - errors=5
        - cpu_util=45.2
        - mem_peak_mb=256
        """
        # テンプレートの展開
        cmd_template = case["cmd_template"]
        cmd = self.template_engine.expand(cmd_template, case)

        # コマンド実行
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                shell=True,  # nosec B602 - shell=True required for DOE Runner shell adapter
                capture_output=True,
                text=True,
                timeout=int(case.get("timeout_s", 30)),
            )

            execution_time = time.time() - start_time

            # 出力からメトリクスを抽出
            metrics = self._parse_metrics(result.stdout + result.stderr)
            metrics["stdout"] = result.stdout
            metrics["stderr"] = result.stderr

            # 実行時間情報を追加
            metrics["execution_time"] = execution_time

            # エラーハンドリング
            if result.returncode != 0:
                metrics["errors"] = metrics.get("errors", 0) + 1

            return metrics

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command timed out: {cmd}") from None
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {e}") from e

    def _parse_metrics(self, output: str) -> dict[str, Any]:
        """
        コマンド出力からメトリクスを抽出

        対応パターン:
        - key=value 形式
        - "key: value" 形式
        - JSON形式の部分抽出
        """
        metrics = {"p95": None, "p99": None, "throughput_rps": 0.0, "errors": 0}

        # key=value パターン
        kv_patterns = [
            (r"p95[=:]\s*([0-9.]+)", "p95"),
            (r"p99[=:]\s*([0-9.]+)", "p99"),
            (r"throughput_rps[=:]\s*([0-9.]+)", "throughput_rps"),
            (r"throughput[=:]\s*([0-9.]+)", "throughput_rps"),
            (r"errors[=:]\s*([0-9]+)", "errors"),
            (r"cpu_util[=:]\s*([0-9.]+)", "cpu_util"),
            (r"mem_peak_mb[=:]\s*([0-9.]+)", "mem_peak_mb"),
            (r"queue_depth_p95[=:]\s*([0-9.]+)", "queue_depth_p95"),
            (r"latency_p50[=:]\s*([0-9.]+)", "latency_p50"),
        ]

        for pattern, key in kv_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                metrics[key] = value

        # JSON形式の部分抽出を試行
        json_match = re.search(r"\{[^}]+\}", output)
        if json_match:
            try:
                import json

                json_data = json.loads(json_match.group(0))

                # JSONからメトリクスを抽出
                for key in [
                    "p95",
                    "p99",
                    "throughput_rps",
                    "errors",
                    "cpu_util",
                    "mem_peak_mb",
                    "queue_depth_p95",
                    "latency_p50",
                ]:
                    if key in json_data:
                        metrics[key] = json_data[key]

            except json.JSONDecodeError:
                pass

        # デフォルト値の設定
        if metrics["throughput_rps"] == 0.0 and metrics.get("errors", 0) == 0:
            # エラーがなくてスループットが0の場合、最低値を設定
            metrics["throughput_rps"] = 1.0

        return metrics

    def validate_case(self, case: dict[str, Any]) -> bool:
        """シェルアダプター用の検証"""
        if not super().validate_case(case):
            return False

        # cmd_templateが空でないかチェック
        cmd_template = case.get("cmd_template", "").strip()
        if not cmd_template:
            return False

        return True
