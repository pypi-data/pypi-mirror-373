"""
バッチ実験オーケストレータのコア実装
"""

import hashlib
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..io import CSVHandler, MetricsNormalizer, RunlogWriter
from .cache import CaseCache
from .config import Config
from .executor import CaseExecutor
from .validator import CaseValidator


@dataclass
class ExecutionResult:
    """単一ケースの実行結果"""

    case_id: str
    status: str  # OK|FAIL|TIMEOUT
    run_seconds: float
    p95: float | None
    p99: float | None
    throughput_rps: float
    errors: int
    ts_start: str
    ts_end: str
    # 追加メタデータ
    cpu_util: float | None = None
    mem_peak_mb: float | None = None
    queue_depth_p95: float | None = None
    latency_p50: float | None = None


class Runner:
    """バッチ実験オーケストレータ"""

    VERSION = "0.1.0"

    def __init__(
        self,
        max_workers: int = 1,
        fail_fast: bool = False,
        force_rerun: bool = False,
        dry_run: bool = False,
        verbose: bool = False,
        run_log_dir: str = "docs/run",
        compat_mode: bool = False,
        cfg: Config | None = None,
    ) -> None:
        self.max_workers = max_workers
        self.fail_fast = fail_fast
        self.force_rerun = force_rerun
        self.dry_run = dry_run
        self.verbose = verbose
        self.run_log_dir = Path(run_log_dir)
        self.compat_mode = compat_mode
        self.cfg = cfg or Config()

        # コンポーネント初期化
        self.csv_handler = CSVHandler()
        self.cache = CaseCache()
        self.executor = CaseExecutor(self)
        self.validator = CaseValidator()
        self.normalizer = MetricsNormalizer()

        # 実行統計
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "timeout": 0,
            "skipped": 0,
            "threshold_violations": 0,
        }

    def execute(self, cases_path: str, metrics_path: str) -> int:
        """
        メイン実行ループ

        Returns:
            0: 成功
            2: threshold違反
            3: エラー
        """
        try:
            # JST時刻でRunログ初期化
            jst = timezone(timedelta(hours=9))
            start_time = datetime.now(jst)
            run_label = start_time.strftime("%Y%m%d-%H%M-JST")

            # 1. cases.csv読み込み・検証
            if self.verbose:
                print(f"Loading cases from: {cases_path}")

            cases = self._load_and_validate_cases(cases_path)
            self.stats["total"] = len(cases)

            if self.dry_run:
                print(f"Dry run: {len(cases)} cases validated")
                return 0

            # 2. Runログ初期化
            self.run_log_dir.mkdir(parents=True, exist_ok=True)
            runlog_path = self.run_log_dir / f"{run_label}-doe-runner.md"
            runlog = RunlogWriter(runlog_path, compat_mode=self.compat_mode)
            runlog.write_header(start_time, cases_path, len(cases))

            # 3. ケース実行
            if self.verbose:
                print(
                    f"Executing {len(cases)} cases with {self.max_workers} workers..."
                )

            results = self._execute_cases(cases)

            # 4. threshold検証
            self._check_thresholds(cases, results)

            # 5. metrics.csv出力（決定論的）
            if self.verbose:
                print(f"Writing metrics to: {metrics_path}")

            self._write_metrics(results, metrics_path, cases)

            # 6. Runログ完成
            end_time = datetime.now(jst)
            runlog.write_summary(self.stats, results, end_time - start_time)
            runlog.write_artifacts([metrics_path])

            # 7. Summary非空チェック
            if not runlog.has_non_empty_summary():
                raise ValueError("Runlog Summary is empty")

            # 8. 実行レポート出力
            self._print_report()

            # 9. 退出コード決定
            if self.stats["failed"] > 0 or self.stats["timeout"] > 0:
                return 3
            if self.stats["threshold_violations"] > 0:
                return 2
            return 0

        except Exception as e:
            print(f"Fatal error: {e}", file=sys.stderr)
            if self.verbose:
                import traceback

                traceback.print_exc()
            return 3

    def _load_and_validate_cases(self, path: str) -> list[dict]:
        """cases.csv読み込み・検証"""
        cases = self.csv_handler.load_cases(path)

        # 必須列チェック
        errors = self.validator.validate_cases(cases)
        if errors:
            raise ValueError(f"Validation errors: {errors}")

        # 列名正規化（小文字・トリム）
        normalized = []
        for case in cases:
            normalized.append(
                {k.lower().strip(): str(v).strip() for k, v in case.items()}
            )

        return normalized

    def _compute_case_hash(self, case: dict) -> str:
        """ケースの正規化ハッシュ計算"""
        # 決定論的要素のみ
        key_parts = [
            case.get("case_id", ""),
            case.get("backend", ""),
            case.get("cmd_template", ""),
            case.get("seed", ""),
            self.VERSION,
        ]
        key = "|".join(str(p) for p in key_parts)
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def _execute_cases(self, cases: list[dict]) -> list[ExecutionResult]:
        """並列/直列実行管理"""
        results = []

        # resource_groupでグループ化
        groups = self._group_by_resource(cases)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for group_name, group_cases in groups.items():
                if self.verbose and len(groups) > 1:
                    print(f"Executing group: {group_name}")

                futures = []
                for case in group_cases:
                    # キャッシュチェック
                    case_hash = self._compute_case_hash(case)

                    if not self.force_rerun and self.cache.exists(case_hash):
                        cached = self.cache.load(case_hash)
                        if cached is not None:
                            results.append(cached)
                            self.stats["skipped"] += 1
                            if self.verbose:
                                print(f"  Cached: {case['case_id']}")
                            continue

                    # 実行スケジュール
                    future = executor.submit(self._execute_single_case, case)
                    futures.append((case, future))

                # 結果収集（fail-fast対応）
                for case, future in futures:
                    try:
                        result = future.result()
                        results.append(result)

                        # キャッシュ保存
                        case_hash = self._compute_case_hash(case)
                        self.cache.save(case_hash, result)

                        # 統計更新
                        if result.status == "OK":
                            self.stats["success"] += 1
                            if self.verbose:
                                print(
                                    f"  ✓ {case['case_id']}: {result.run_seconds:.3f}s"
                                )
                        elif result.status == "TIMEOUT":
                            self.stats["timeout"] += 1
                            if self.verbose:
                                print(f"  ⏱ {case['case_id']}: TIMEOUT")
                        else:
                            self.stats["failed"] += 1
                            if self.verbose:
                                print(f"  ✗ {case['case_id']}: FAILED")

                        if self.fail_fast and result.status != "OK":
                            raise RuntimeError(f"Case {case['case_id']} failed")

                    except Exception:
                        if self.fail_fast:
                            raise
                        # エラー結果を記録
                        error_result = ExecutionResult(
                            case_id=case["case_id"],
                            status="FAIL",
                            run_seconds=0,
                            p95=None,
                            p99=None,
                            throughput_rps=0,
                            errors=1,
                            ts_start=datetime.now().isoformat(),
                            ts_end=datetime.now().isoformat(),
                        )
                        results.append(error_result)
                        self.stats["failed"] += 1

        return results

    def _execute_single_case(self, case: dict) -> ExecutionResult:
        """単一ケース実行"""
        return self.executor.execute(case)

    def _check_thresholds(
        self, cases: list[dict], results: list[ExecutionResult]
    ) -> int:
        """threshold検証"""
        violations = 0

        # case_idでマッチング
        result_map = {r.case_id: r for r in results}

        for case in cases:
            result = result_map.get(case["case_id"])
            if not result:
                continue

            # expected_* と threshold_* のチェック
            for metric in ["p95", "p99", "throughput_rps"]:
                threshold_key = f"threshold_{metric}"

                if threshold_key in case and case[threshold_key]:
                    try:
                        threshold = float(case[threshold_key])
                        actual = getattr(result, metric)

                        if actual is not None and actual > threshold:
                            violations += 1
                            if self.verbose:
                                print(
                                    f"⚠️  Threshold violation: {case['case_id']} "
                                    f"{metric}={actual} > {threshold}"
                                )
                    except (ValueError, TypeError):
                        # 無効なthreshold値はスキップ
                        continue

        self.stats["threshold_violations"] = violations
        return violations

    def _write_metrics(
        self, results: list[ExecutionResult], path: str, cases: list[dict]
    ) -> None:
        """決定論的なmetrics.csv出力"""
        # 結果を辞書化
        metrics_data = []

        for result in results:
            row = asdict(result)
            row["run_id"] = self.cfg.run_id

            # param_* を追加（入力転写）
            case = next((c for c in cases if c["case_id"] == result.case_id), {})
            for k, v in case.items():
                if k not in ["case_id", "cmd_template", "backend"]:
                    row[f"param_{k}"] = v

            metrics_data.append(row)

        # 正規化して出力
        normalized = self.normalizer.normalize(metrics_data)
        self.csv_handler.write_metrics(normalized, path)

    def _group_by_resource(self, cases: list[dict]) -> dict[str, list[dict]]:
        """resource_groupによるグループ化"""
        groups: dict[str, list[dict]] = {}
        for case in cases:
            group = case.get("resource_group", "default")
            if group not in groups:
                groups[group] = []
            groups[group].append(case)
        return groups

    def _print_report(self) -> None:
        """実行レポート出力"""
        print("\n" + "=" * 50)
        print("Execution Report")
        print("=" * 50)
        print(f"Total cases: {self.stats['total']}")
        print(f"Success: {self.stats['success']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Timeout: {self.stats['timeout']}")
        print(f"Skipped (cached): {self.stats['skipped']}")
        print(f"Threshold violations: {self.stats['threshold_violations']}")

        # 実行時間の統計も追加可能
        success_rate: float = 0.0
        if self.stats["total"] > 0:
            success_rate = (self.stats["success"] / self.stats["total"]) * 100
        print(f"Success rate: {success_rate:.1f}%")
        print("=" * 50)
