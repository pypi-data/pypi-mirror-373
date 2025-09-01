"""
テスト用ダミーアダプター
"""

import random
import time
from typing import Any

from .base import BaseAdapter


class DummyAdapter(BaseAdapter):
    """テスト用のダミーアダプター"""

    def execute(self, case: dict[str, Any]) -> dict[str, Any]:
        """
        ダミーの実行結果を生成

        seedが指定されている場合は決定論的な結果を生成
        """
        # seedの処理
        seed = case.get("seed")
        if seed is not None:
            random.seed(int(seed))

        # 実行時間のシミュレート
        execution_time = random.uniform(0.1, 2.0)
        time.sleep(min(execution_time, 0.1))  # 実際の待機は短く

        # ダミーメトリクスの生成
        base_latency = random.uniform(0.01, 0.2)

        metrics = {
            "p95": round(base_latency * random.uniform(1.5, 2.0), 4),
            "p99": round(base_latency * random.uniform(2.0, 3.0), 4),
            "throughput_rps": round(random.uniform(100, 2000), 1),
            "errors": random.choices([0, 1, 2, 5], weights=[0.8, 0.1, 0.05, 0.05])[0],
            "latency_p50": round(base_latency * random.uniform(0.8, 1.2), 4),
        }

        # 追加メトリクス（ランダムに含める）
        if random.random() > 0.3:
            metrics["cpu_util"] = round(random.uniform(10, 80), 1)

        if random.random() > 0.3:
            metrics["mem_peak_mb"] = round(random.uniform(50, 500), 1)

        if random.random() > 0.5:
            metrics["queue_depth_p95"] = round(random.uniform(1, 10), 2)

        # 失敗をシミュレート（低確率）
        if case.get("force_failure") or random.random() < 0.05:
            metrics["errors"] = 1
            raise RuntimeError("Simulated execution failure")

        # タイムアウトをシミュレート（極低確率）
        if case.get("force_timeout"):
            raise TimeoutError("Simulated timeout")

        return metrics

    def validate_case(self, case: dict[str, Any]) -> bool:
        """ダミーアダプター用の検証（常にTrue）"""
        return super().validate_case(case)
