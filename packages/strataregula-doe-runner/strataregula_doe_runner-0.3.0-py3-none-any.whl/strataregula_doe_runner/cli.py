"""
DOE Runner CLI - バッチ実験オーケストレータ
"""

import os
import sys

import click

# 簡易的なCSVハンドラーとRunnerを直接インポート
from .core.runner import Runner


@click.group()
@click.version_option()
def cli() -> None:
    """Strataregula DOE Runner - Batch experiment orchestrator"""
    pass


@cli.command()
@click.option(
    "--cases",
    required=True,
    type=click.Path(exists=True),
    help="Input cases CSV file path",
)
@click.option("--out", default="metrics.csv", help="Output metrics CSV file path")
@click.option(
    "--max-workers", default=1, type=int, help="Maximum parallel workers (default: 1)"
)
@click.option("--fail-fast", is_flag=True, help="Stop execution on first failure")
@click.option("--force", is_flag=True, help="Force re-execution (ignore cache)")
@click.option("--dry-run", is_flag=True, help="Validate only, do not execute")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def run(
    cases: str,
    out: str,
    max_workers: int,
    fail_fast: bool,
    force: bool,
    dry_run: bool,
    verbose: bool,
) -> None:
    """
    Execute cases from CSV and generate metrics.

    Exit codes:
      0: All cases executed successfully, thresholds met
      2: Execution completed but threshold violations detected
      3: I/O error, invalid configuration, or execution failure
    """

    # 環境変数の読み取り
    run_log_dir = os.getenv("RUN_LOG_DIR", "docs/run")
    compat_mode = os.getenv("RUN_LOG_WRITE_COMPAT", "0") == "1"

    runner = Runner(
        max_workers=max_workers,
        fail_fast=fail_fast,
        force_rerun=force,
        dry_run=dry_run,
        verbose=verbose,
        run_log_dir=run_log_dir,
        compat_mode=compat_mode,
    )

    try:
        if verbose:
            click.echo(f"DOE Runner v{Runner.VERSION}")
            click.echo(f"Cases file: {cases}")
            click.echo(f"Output file: {out}")
            click.echo(f"Max workers: {max_workers}")

        exit_code = runner.execute(cases, out)

        # 実行サマリー出力
        if verbose:
            click.echo(f"Execution completed with exit code: {exit_code}")

        sys.exit(exit_code)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(3)


@cli.command()
@click.option(
    "--cases",
    required=True,
    type=click.Path(exists=True),
    help="Cases CSV file to validate",
)
def validate(cases: str) -> None:
    """Validate cases CSV file format and content."""
    from .core.validator import CaseValidator

    try:
        validator = CaseValidator()

        # ファイル形式チェック
        format_errors = validator.validate_file_format(cases)
        if format_errors:
            click.echo("File format errors:", err=True)
            for error in format_errors:
                click.echo(f"  - {error}", err=True)
            sys.exit(1)

        click.echo("✓ Validation passed")

    except Exception as e:
        click.echo(f"Validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--cache-dir", default=".doe_cache", help="Cache directory path")
def cache(cache_dir: str) -> None:
    """Manage execution cache."""
    from .core.cache import CaseCache

    cache_mgr = CaseCache(cache_dir)

    size = cache_mgr.size()
    click.echo(f"Cache directory: {cache_dir}")
    click.echo(f"Cache entries: {size}")

    if size > 0:
        click.echo("\nCache operations:")
        click.echo("  srd cache clear  - Clear all cache")
        click.echo("  srd cache clean  - Remove old entries")


# CLIエントリポイント
def main() -> None:
    cli()


if __name__ == "__main__":
    main()
