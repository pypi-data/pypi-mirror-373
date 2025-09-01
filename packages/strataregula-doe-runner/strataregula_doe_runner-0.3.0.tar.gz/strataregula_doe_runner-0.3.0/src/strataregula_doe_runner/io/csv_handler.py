"""
CSV handler stub for initial testing
"""

import csv
from pathlib import Path
from typing import Any


class CSVHandler:
    """Simple CSV handler for testing"""

    def load_cases(self, file_path: str) -> list[dict[str, Any]]:
        """Load cases from CSV"""
        cases = []

        with open(file_path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cases.append(row)

        return cases

    def write_metrics(self, metrics_data: list[dict[str, Any]], file_path: str) -> None:
        """Write metrics to CSV"""
        if not metrics_data:
            return

        # Create directory
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # Get all column names
        all_columns: set[str] = set()
        for row in metrics_data:
            all_columns.update(row.keys())

        # Simple column ordering
        columns = sorted(all_columns)

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            for row in metrics_data:
                writer.writerow(row)
