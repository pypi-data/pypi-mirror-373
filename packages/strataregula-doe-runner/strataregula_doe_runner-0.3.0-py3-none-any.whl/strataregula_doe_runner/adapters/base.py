"""
アダプターベースクラス
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """実行アダプターのベースクラス"""

    @abstractmethod
    def execute(self, case: dict[str, Any]) -> dict[str, Any]:
        """
        ケースを実行してメトリクスを返す

        Args:
            case: ケース情報辞書
                - case_id: str
                - backend: str
                - cmd_template: str
                - その他のパラメータ

        Returns:
            Dict[str, Any]: メトリクス辞書
                必須キー:
                - p95: Optional[float] - 95パーセンタイルレイテンシ
                - p99: Optional[float] - 99パーセンタイルレイテンシ
                - throughput_rps: float - スループット（RPS）
                - errors: int - エラー数

                オプションキー:
                - cpu_util: Optional[float] - CPU使用率
                - mem_peak_mb: Optional[float] - ピークメモリ使用量
                - queue_depth_p95: Optional[float] - キュー深度95パーセンタイル
                - latency_p50: Optional[float] - 50パーセンタイルレイテンシ
        """
        pass

    def name(self) -> str:
        """アダプター名を返す"""
        return self.__class__.__name__.lower().replace("adapter", "")

    def supports_placeholders(self) -> bool:
        """プレースホルダー置換をサポートするか"""
        return True

    def validate_case(self, case: dict[str, Any]) -> bool:
        """ケースがこのアダプターで実行可能かチェック"""
        required_keys = ["case_id", "backend", "cmd_template"]
        return all(key in case for key in required_keys)
