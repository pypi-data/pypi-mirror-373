"""
ケース実行管理
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .runner import ExecutionResult, Runner
from ..adapters.base import BaseAdapter
from ..adapters.dummy import DummyAdapter
from ..adapters.shell import ShellAdapter


class CaseExecutor:
    """個別ケースの実行管理"""

    def __init__(self, parent: Runner) -> None:
        self.parent = parent
        # アダプターの登録
        self.adapters = {
            "shell": ShellAdapter(),
            "dummy": DummyAdapter(),
        }

        # simroute アダプターは動的に登録（extras依存）
        try:
            from ..adapters.simroute import SimrouteAdapter

            self.adapters["simroute"] = SimrouteAdapter()
        except ImportError:
            pass

    def execute(self, case: dict) -> ExecutionResult:
        """
        単一ケースの実行

        Args:
            case: ケース情報（case_id, backend, cmd_template等）

        Returns:
            ExecutionResult: 実行結果
        """
        case_id = case["case_id"]
        backend = case.get("backend", "shell")
        timeout_s = int(case.get("timeout_s", 30))

        # アダプター取得
        adapter = self.adapters.get(backend)
        if not adapter:
            raise ValueError(f"Unknown backend: {backend}")

        # 実行開始
        ts_start = datetime.now().isoformat()
        start_time = time.time()

        try:
            # タイムアウト付き実行
            metrics = self._execute_with_timeout(adapter, case, timeout_s)

            stdout = metrics.pop("stdout", None)
            stderr = metrics.pop("stderr", None)

            if self.parent.cfg.obs_enabled and self.parent.cfg.save_stdout:
                ts_dir = datetime.now().strftime("%Y%m%d-%H%M%S")
                adir = self.parent.cfg.artifacts_dir / case_id / ts_dir
                adir.mkdir(parents=True, exist_ok=True)
                if stdout is not None:
                    (adir / "stdout.log").write_text(stdout or "", encoding="utf-8")
                    str(adir / "stdout.log")
                if stderr is not None:
                    (adir / "stderr.log").write_text(stderr or "", encoding="utf-8")
                    str(adir / "stderr.log")

            # 実行時間計測
            run_seconds = time.time() - start_time
            ts_end = datetime.now().isoformat()

            # 結果構築（動的インポート）
            from .runner import ExecutionResult

            result = ExecutionResult(
                case_id=case_id,
                status="OK",
                run_seconds=run_seconds,
                p95=metrics.get("p95"),
                p99=metrics.get("p99"),
                throughput_rps=metrics.get("throughput_rps", 0.0),
                errors=metrics.get("errors", 0),
                ts_start=ts_start,
                ts_end=ts_end,
                cpu_util=metrics.get("cpu_util"),
                mem_peak_mb=metrics.get("mem_peak_mb"),
                queue_depth_p95=metrics.get("queue_depth_p95"),
                latency_p50=metrics.get("latency_p50"),
            )

            return result

        except TimeoutError:
            # タイムアウト
            run_seconds = time.time() - start_time
            from .runner import ExecutionResult

            return ExecutionResult(
                case_id=case_id,
                status="TIMEOUT",
                run_seconds=run_seconds,
                p95=None,
                p99=None,
                throughput_rps=0.0,
                errors=1,
                ts_start=ts_start,
                ts_end=datetime.now().isoformat(),
            )

        except Exception:
            # 実行エラー
            run_seconds = time.time() - start_time
            from .runner import ExecutionResult

            return ExecutionResult(
                case_id=case_id,
                status="FAIL",
                run_seconds=run_seconds,
                p95=None,
                p99=None,
                throughput_rps=0.0,
                errors=1,
                ts_start=ts_start,
                ts_end=datetime.now().isoformat(),
            )

    def _execute_with_timeout(
        self, adapter: BaseAdapter, case: dict, timeout_s: int
    ) -> dict:
        """
        タイムアウト付きアダプター実行

        Args:
            adapter: 実行アダプター
            case: ケース情報
            timeout_s: タイムアウト秒数

        Returns:
            Dict: メトリクス辞書

        Raises:
            TimeoutError: タイムアウト時
            Exception: その他エラー時
        """
        import threading

        result = {}
        exception = None

        def execute_case() -> None:
            nonlocal result, exception
            try:
                result = adapter.execute(case)
            except Exception as e:
                exception = e

        # バックグラウンド実行
        thread = threading.Thread(target=execute_case)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout_s)

        if thread.is_alive():
            # タイムアウト - スレッドを強制終了はできないが、例外を投げる
            raise TimeoutError(f"Execution timed out after {timeout_s}s")

        if exception:
            raise exception

        return result

    def add_adapter(self, name: str, adapter: BaseAdapter) -> None:
        """アダプターを動的に追加"""
        self.adapters[name] = adapter

    def list_adapters(self) -> list[str]:
        """利用可能なアダプター一覧を取得"""
        return list(self.adapters.keys())
