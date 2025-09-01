"""
case_hashによるキャッシュ機能
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .runner import ExecutionResult


class CaseCache:
    """ケース実行結果のキャッシュ"""

    def __init__(self, cache_dir: str = ".doe_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def exists(self, case_hash: str) -> bool:
        """キャッシュが存在するかチェック"""
        cache_file = self.cache_dir / f"{case_hash}.json"
        return cache_file.exists()

    def save(self, case_hash: str, result: ExecutionResult) -> None:
        """実行結果をキャッシュに保存"""
        cache_file = self.cache_dir / f"{case_hash}.json"

        # ExecutionResultを辞書化
        from dataclasses import asdict

        data = asdict(result)

        # メタデータ追加
        data["_cache_meta"] = {"cached_at": result.ts_end, "cache_version": "1.0"}

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, case_hash: str) -> ExecutionResult | None:
        """キャッシュから実行結果を読み込み"""
        cache_file = self.cache_dir / f"{case_hash}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, encoding="utf-8") as f:
                data = json.load(f)

            # メタデータ除去
            data.pop("_cache_meta", None)

            # ExecutionResultに復元（動的インポート）
            from .runner import ExecutionResult

            return ExecutionResult(**data)

        except (json.JSONDecodeError, TypeError, ValueError):
            # 破損したキャッシュファイルは無視
            return None

    def clear(self) -> int:
        """キャッシュをクリア"""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except OSError:
                pass
        return count

    def size(self) -> int:
        """キャッシュエントリ数を取得"""
        return len(list(self.cache_dir.glob("*.json")))

    def cleanup_old(self, days: int = 7) -> int:
        """古いキャッシュエントリを削除"""
        import time

        cutoff = time.time() - (days * 24 * 60 * 60)
        count = 0

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if cache_file.stat().st_mtime < cutoff:
                    cache_file.unlink()
                    count += 1
            except OSError:
                pass

        return count
