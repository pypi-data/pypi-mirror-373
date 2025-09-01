"""
cases.csv検証
"""

from typing import Any


class CaseValidator:
    """ケース検証"""

    # 必須列
    REQUIRED_COLUMNS = {
        "case_id": str,
        "backend": str,
        "cmd_template": str,
        "timeout_s": (int, float, str),
    }

    # 推奨列
    RECOMMENDED_COLUMNS = {
        "seed": (int, str),
        "retries": (int, str),
        "resource_group": str,
    }

    # メトリクス期待値列
    METRICS_COLUMNS = {
        "expected_p95": (int, float, str),
        "expected_p99": (int, float, str),
        "threshold_p95": (int, float, str),
        "threshold_p99": (int, float, str),
        "expected_throughput_rps": (int, float, str),
        "threshold_throughput_rps": (int, float, str),
    }

    def validate_cases(self, cases: list[dict[str, Any]]) -> list[str]:
        """
        ケースリストを検証

        Args:
            cases: ケースの辞書リスト

        Returns:
            List[str]: エラーメッセージのリスト（空なら検証通過）
        """
        errors = []

        if not cases:
            errors.append("No cases found")
            return errors

        # 列名の取得（最初のケースから）
        first_case = cases[0]
        columns = set(first_case.keys())

        # 必須列チェック
        for column, _expected_type in self.REQUIRED_COLUMNS.items():
            if column not in columns:
                errors.append(f"Missing required column: {column}")

        # 各ケースの検証
        case_ids = set()
        for i, case in enumerate(cases):
            row_errors = self._validate_single_case(case, i + 1)
            errors.extend(row_errors)

            # case_idの重複チェック
            case_id = case.get("case_id")
            if case_id:
                if case_id in case_ids:
                    errors.append(f"Duplicate case_id: {case_id}")
                case_ids.add(case_id)

        return errors

    def _validate_single_case(self, case: dict[str, Any], row_num: int) -> list[str]:
        """単一ケースの検証"""
        errors = []
        row_prefix = f"Row {row_num}"

        # 必須列の値チェック
        for column, _expected_type in self.REQUIRED_COLUMNS.items():
            value = case.get(column)

            if value is None or value == "":
                errors.append(f"{row_prefix}: {column} cannot be empty")
                continue

            # 型チェック（文字列から変換可能かも含む）
            if column == "timeout_s":
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append(f"{row_prefix}: {column} must be numeric")

            elif column == "backend":
                valid_backends = ["shell", "dummy", "simroute"]
                if str(value).lower() not in valid_backends:
                    errors.append(
                        f"{row_prefix}: {column} must be one of {valid_backends}"
                    )

        # case_idの形式チェック
        case_id = case.get("case_id")
        if case_id:
            if not self._is_valid_case_id(str(case_id)):
                errors.append(f"{row_prefix}: case_id contains invalid characters")

        # 数値列のチェック
        numeric_columns = [
            "seed",
            "retries",
            "expected_p95",
            "expected_p99",
            "threshold_p95",
            "threshold_p99",
            "expected_throughput_rps",
            "threshold_throughput_rps",
        ]

        for column in numeric_columns:
            value = case.get(column)
            if value is not None and value != "":
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append(f"{row_prefix}: {column} must be numeric")

        return errors

    def _is_valid_case_id(self, case_id: str) -> bool:
        """case_idの形式検証"""
        # 英数字、ハイフン、アンダースコアのみ許可
        import re

        return bool(re.match(r"^[a-zA-Z0-9_-]+$", case_id))

    def validate_file_format(self, file_path: str) -> list[str]:
        """CSVファイル形式の検証"""
        errors = []

        try:
            import csv

            with open(file_path, encoding="utf-8") as f:
                # CSVとして読み込めるかテスト
                reader = csv.DictReader(f)
                headers = reader.fieldnames

                if not headers:
                    errors.append("CSV file has no headers")
                    return errors

                # 最初の数行を読んで基本的な形式チェック
                row_count = 0
                for _row in reader:
                    row_count += 1
                    if row_count > 3:  # 最初の3行のみチェック
                        break

                if row_count == 0:
                    errors.append("CSV file has no data rows")

        except FileNotFoundError:
            errors.append(f"File not found: {file_path}")
        except PermissionError:
            errors.append(f"Permission denied: {file_path}")
        except Exception as e:
            errors.append(f"Failed to read CSV file: {e}")

        return errors
