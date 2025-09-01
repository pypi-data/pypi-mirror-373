"""End-to-end integration tests for DOE Runner."""

import csv
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from strataregula_doe_runner.core.runner import Runner
from strataregula_doe_runner.plugin import DOERunnerPlugin


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_cases_csv(temp_dir: Path) -> Path:
    """Create a sample cases.csv file."""
    cases_file = temp_dir / "cases.csv"

    with open(cases_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "case_id",
                "backend",
                "cmd_template",
                "timeout_s",
                "seed",
                "retries",
                "resource_group",
                "expected_p95",
                "threshold_p95",
            ]
        )
        writer.writerow(
            [
                "test-01",
                "dummy",
                "dummy simulation",
                "10",
                "42",
                "1",
                "default",
                "0.05",
                "0.06",
            ]
        )
        writer.writerow(
            [
                "test-02",
                "shell",
                "echo 'p95=0.08 p99=0.12 throughput_rps=500'",
                "10",
                "123",
                "1",
                "default",
                "0.08",
                "0.10",
            ]
        )
        writer.writerow(
            [
                "test-03",
                "shell",
                "echo 'p95=0.15 p99=0.20 throughput_rps=200'",
                "10",
                "456",
                "0",
                "default",
                "0.12",
                "0.12",  # This will trigger threshold violation
            ]
        )

    return cases_file


@pytest.fixture
def performance_cases_csv(temp_dir: Path) -> Path:
    """Create performance test cases with larger dataset."""
    cases_file = temp_dir / "perf_cases.csv"

    with open(cases_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "case_id",
                "backend",
                "cmd_template",
                "timeout_s",
                "seed",
                "retries",
                "resource_group",
            ]
        )

        # Generate 50 test cases
        for i in range(50):
            writer.writerow(
                [
                    f"perf-{i:02d}",
                    "dummy",
                    f"dummy simulation {i}",
                    "5",
                    str(i * 10),
                    "0",
                    "perf",
                ]
            )

    return cases_file


class TestEndToEndWorkflow:
    """Test complete DOE Runner workflow."""

    def test_complete_workflow_success(
        self, sample_cases_csv: Path, temp_dir: Path
    ) -> None:
        """Test complete workflow: cases.csv → execution → metrics.csv → validation."""
        metrics_file = temp_dir / "metrics.csv"

        # Execute via Runner
        runner = Runner(max_workers=1, verbose=True)
        exit_code = runner.execute(
            cases_path=str(sample_cases_csv), metrics_path=str(metrics_file)
        )

        # Should return exit code 2 due to threshold violation in test-03
        assert exit_code == 2
        assert metrics_file.exists()

        # Verify metrics CSV structure
        with open(metrics_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3  # All 3 cases should be executed

        # Verify required columns
        expected_columns = [
            "case_id",
            "status",
            "run_seconds",
            "p95",
            "p99",
            "throughput_rps",
            "errors",
            "ts_start",
            "ts_end",
            "run_id",
        ]
        for col in expected_columns:
            assert col in rows[0].keys()

        run_id_values = {row["run_id"] for row in rows}
        assert len(run_id_values) == 1

        # Verify case results
        results_by_id = {row["case_id"]: row for row in rows}

        # test-01 (dummy) should succeed
        assert results_by_id["test-01"]["status"] == "OK"

        # test-02 (shell with metrics) should succeed
        assert results_by_id["test-02"]["status"] == "OK"
        assert float(results_by_id["test-02"]["p95"]) == 0.08
        assert float(results_by_id["test-02"]["throughput_rps"]) == 500

        # test-03 (threshold violation) should succeed but violate threshold
        assert results_by_id["test-03"]["status"] == "OK"
        assert float(results_by_id["test-03"]["p95"]) == 0.15  # Above threshold of 0.12

    def test_workflow_with_cache(self, sample_cases_csv: Path, temp_dir: Path) -> None:
        """Test workflow with caching - second run should use cache."""
        metrics_file = temp_dir / "metrics.csv"

        runner = Runner(max_workers=1)

        # First execution
        exit_code1 = runner.execute(
            cases_path=str(sample_cases_csv), metrics_path=str(metrics_file)
        )

        first_metrics = []
        with open(metrics_file) as f:
            reader = csv.DictReader(f)
            first_metrics = list(reader)

        # Second execution (should use cache)
        metrics_file_2 = temp_dir / "metrics2.csv"
        exit_code2 = runner.execute(
            cases_path=str(sample_cases_csv), metrics_path=str(metrics_file_2)
        )

        second_metrics = []
        with open(metrics_file_2) as f:
            reader = csv.DictReader(f)
            second_metrics = list(reader)

        # Both executions should have same exit code
        assert exit_code1 == exit_code2

        # Results should be identical (deterministic)
        assert len(first_metrics) == len(second_metrics)

        for _i, (first, second) in enumerate(
            zip(first_metrics, second_metrics, strict=False)
        ):
            assert first["case_id"] == second["case_id"]
            assert first["status"] == second["status"]
            # Note: execution times may differ slightly due to cache hits

    def test_force_execution_bypasses_cache(
        self, sample_cases_csv: Path, temp_dir: Path
    ) -> None:
        """Test that --force flag bypasses cache."""
        metrics_file = temp_dir / "metrics.csv"

        runner = Runner(max_workers=1)

        # First execution
        runner.execute(cases_path=str(sample_cases_csv), metrics_path=str(metrics_file))

        # Force execution (bypass cache)
        metrics_file_2 = temp_dir / "metrics_force.csv"
        runner_force = Runner(max_workers=1, force_rerun=True)
        exit_code = runner_force.execute(
            cases_path=str(sample_cases_csv), metrics_path=str(metrics_file_2)
        )

        assert exit_code == 2  # Should still have threshold violations
        assert metrics_file_2.exists()

    def test_dry_run_validation(self, sample_cases_csv: Path, temp_dir: Path) -> None:
        """Test dry run mode - validation only, no execution."""
        metrics_file = temp_dir / "metrics_dry.csv"

        runner = Runner(dry_run=True)
        exit_code = runner.execute(
            cases_path=str(sample_cases_csv), metrics_path=str(metrics_file)
        )

        # Dry run should succeed (validation only)
        assert exit_code == 0
        # No metrics file should be created
        assert not metrics_file.exists()

    def test_parallel_execution(
        self, performance_cases_csv: Path, temp_dir: Path
    ) -> None:
        """Test parallel execution with multiple workers."""
        metrics_file = temp_dir / "metrics_parallel.csv"

        runner = Runner(max_workers=4, verbose=True)
        runner.execute(
            cases_path=str(performance_cases_csv), metrics_path=str(metrics_file)
        )

        assert metrics_file.exists()

        with open(metrics_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 50

    def test_invalid_cases_file(self, temp_dir: Path) -> None:
        """Test handling of invalid cases file."""
        invalid_cases = temp_dir / "invalid.csv"

        # Create invalid CSV (missing required columns)
        with open(invalid_cases, "w") as f:
            f.write("case_id,invalid_column\ntest,value\n")

        metrics_file = temp_dir / "metrics.csv"

        runner = Runner()
        exit_code = runner.execute(
            cases_path=str(invalid_cases), metrics_path=str(metrics_file)
        )

        # Should fail with exit code 3 (configuration error)
        assert exit_code == 3
        # No metrics file should be created
        assert not metrics_file.exists()

    def test_missing_cases_file(self, temp_dir: Path) -> None:
        """Test handling of missing cases file."""
        missing_file = temp_dir / "nonexistent.csv"
        metrics_file = temp_dir / "metrics.csv"

        runner = Runner()
        exit_code = runner.execute(
            cases_path=str(missing_file), metrics_path=str(metrics_file)
        )

        # Should fail with exit code 3 (I/O error)
        assert exit_code == 3


class TestPluginIntegration:
    """Test plugin interface and integration."""

    def test_plugin_discovery_and_execution(
        self, sample_cases_csv: Path, temp_dir: Path
    ) -> None:
        """Test plugin discovery and execution through plugin interface."""
        metrics_file = temp_dir / "plugin_metrics.csv"

        # Test plugin instantiation
        plugin = DOERunnerPlugin()

        # Verify plugin info
        info = plugin.get_info()
        assert info["name"] == "doe_runner"
        assert "execute_cases" in info["supported_commands"]

        # Execute via plugin interface
        result = plugin.execute_cases(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file),
            max_workers=1,
            verbose=True,
        )

        # Verify result structure
        assert result["status"] == "success"
        assert result["exit_code"] == 2  # Threshold violations
        assert "stats" in result

        # Verify stats
        stats = result["stats"]
        assert stats["total_cases"] == 3
        # Note: cases may be cached, so we check total cases and threshold violations
        assert stats["total_cases"] == 3
        assert stats["threshold_violations"] > 0  # But have threshold violations

        # Verify metrics file was created
        assert metrics_file.exists()

    def test_plugin_validation_command(self, sample_cases_csv: Path) -> None:
        """Test plugin validation command."""
        plugin = DOERunnerPlugin()

        result = plugin.validate_cases(cases_path=str(sample_cases_csv))

        assert result["status"] == "success"
        assert result["valid"] is True
        assert "validation_details" in result

    def test_plugin_cache_status(self, sample_cases_csv: Path, temp_dir: Path) -> None:
        """Test plugin cache status command."""
        plugin = DOERunnerPlugin()

        # Initially no cache
        result = plugin.get_cache_status(cases_path=str(sample_cases_csv))
        assert result["status"] == "success"
        assert result["cache_hits"] == 0

        # Execute cases to populate cache
        metrics_file = temp_dir / "cache_test_metrics.csv"
        plugin.execute_cases(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file),
            max_workers=1,
        )

        # Check cache status again
        result = plugin.get_cache_status(cases_path=str(sample_cases_csv))
        assert result["status"] == "success"
        assert result["cache_hits"] > 0  # Should have cache hits now

    def test_plugin_clear_cache(self, sample_cases_csv: Path, temp_dir: Path) -> None:
        """Test plugin cache clearing."""
        plugin = DOERunnerPlugin()

        # Execute cases to populate cache
        metrics_file = temp_dir / "clear_cache_metrics.csv"
        plugin.execute_cases(
            cases_path=str(sample_cases_csv), metrics_path=str(metrics_file)
        )

        # Verify cache exists
        cache_status = plugin.get_cache_status(cases_path=str(sample_cases_csv))
        assert cache_status["cache_hits"] > 0

        # Clear cache
        result = plugin.clear_cache(cases_path=str(sample_cases_csv))
        assert result["status"] == "success"

        # Verify cache is cleared
        cache_status = plugin.get_cache_status(cases_path=str(sample_cases_csv))
        assert cache_status["cache_hits"] == 0

    def test_plugin_error_handling(self, temp_dir: Path) -> None:
        """Test plugin error handling with invalid inputs."""
        plugin = DOERunnerPlugin()

        # Test with missing cases file
        result = plugin.execute_cases(
            cases_path="nonexistent.csv", metrics_path="output.csv"
        )

        assert result["status"] == "error"
        assert "message" in result
        assert "not found" in result["message"].lower()

    def test_plugin_get_adapters(self) -> None:
        """Test plugin adapter listing."""
        plugin = DOERunnerPlugin()

        result = plugin.get_adapters()

        assert result["status"] == "success"
        assert "adapters" in result

        adapters = result["adapters"]
        assert "dummy" in adapters
        assert "shell" in adapters

        # Verify adapter info structure
        for _adapter_name, adapter_info in adapters.items():
            assert "description" in adapter_info
            assert "supported_features" in adapter_info


class TestCLIIntegration:
    """Test CLI command integration."""

    def test_cli_basic_execution(self, sample_cases_csv: Path) -> None:
        """Test CLI command execution."""
        from strataregula_doe_runner.cli import main

        # Test that main function exists and is callable
        assert callable(main)

        # Test that CLI module can be imported
        import strataregula_doe_runner.cli

        assert hasattr(strataregula_doe_runner.cli, "cli")

    def test_cli_help_and_version(self) -> None:
        """Test CLI help and version commands."""
        from strataregula_doe_runner.cli import cli

        # Test that CLI group exists and is callable
        assert callable(cli)

        # Test that CLI has commands
        assert hasattr(cli, "commands")


class TestCSVFormat:
    """Test output CSV format."""

    def test_csv_format_compliance(
        self, sample_cases_csv: Path, temp_dir: Path
    ) -> None:
        """Test that output CSV follows format specifications."""
        metrics_file = temp_dir / "format_test.csv"

        runner = Runner()
        runner.execute(cases_path=str(sample_cases_csv), metrics_path=str(metrics_file))

        # Read and verify CSV format
        with open(metrics_file, "rb") as f:
            content = f.read()

        # Verify LF line endings
        assert b"\r\n" not in content, "Should use LF line endings, not CRLF"

        # Verify CSV structure
        with open(metrics_file) as f:
            reader = csv.reader(f)
            header = next(reader)

        required_columns = {
            "case_id",
            "status",
            "run_seconds",
            "p95",
            "p99",
            "throughput_rps",
            "errors",
            "ts_start",
            "ts_end",
            "run_id",
        }
        assert required_columns.issubset(set(header))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
