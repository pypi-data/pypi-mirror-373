# Strataregula - DOE Runner

> 👋 新しく参加した方はまず [docs/ONBOARDING.md](docs/ONBOARDING.md) をご覧ください。

> **開発者へ**: 作業開始前に必ず [docs/README_FOR_DEVELOPERS.md](docs/README_FOR_DEVELOPERS.md) を確認してください。

[![Tests](https://github.com/strataregula/strataregula-doe-runner/actions/workflows/test.yml/badge.svg)](https://github.com/strataregula/strataregula-doe-runner/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/strataregula-doe-runner.svg)](https://pypi.org/project/strataregula-doe-runner/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Strataregula Plugin](https://img.shields.io/badge/Strataregula-Plugin-green)](https://github.com/strataregula/strataregula)
[![CI](https://img.shields.io/badge/CI-github--actions-blue)](#)
[![RunLog Guard](https://img.shields.io/badge/RunLog-guard-green)](#)
[![Docs LinkCheck](https://img.shields.io/badge/Docs-linkcheck-green)](#)
[![PR Size Guard](https://img.shields.io/badge/PR--Size-guard-orange)](#)

Batch experiment orchestrator for Strataregula ecosystem.

## What is DOE Runner?

**DOE Runner is NOT a Design of Experiments tool.** It is a **batch experiment orchestrator** that:

- 📋 Executes predefined cases from `cases.csv`
- 🔀 Manages execution order and parallelism  
- 📊 Collects standardized metrics to `metrics.csv`
- 🔒 Provides deterministic, reproducible results
- 💾 Caches execution results with `case_hash`
- 📝 Generates comprehensive run logs (JST timezone)

**Definition (1 line)**: cases.csvで定義したケース集合を、決定論的に一括実行し、標準化されたmetrics.csv（＋Runログ）に集約する"バッチ実験オーケストレータ"

## Quick Start

```bash
# Install
pip install strataregula-doe-runner

# Execute cases
srd run --cases cases.csv --out metrics.csv

# With parallel execution  
srd run --cases cases.csv --out metrics.csv --max-workers 4

# Force re-execution (ignore cache)
srd run --cases cases.csv --out metrics.csv --force

# Dry run (validation only)
srd run --cases cases.csv --dry-run
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All cases executed successfully, thresholds met |
| 2 | Execution completed but threshold violations detected |
| 3 | I/O error, invalid configuration, or execution failure |

## Cases CSV Contract

### Required Columns
- `case_id`: Unique case identifier
- `backend`: Execution backend (`shell`/`dummy`/`simroute`)
- `cmd_template`: Command template with `{placeholders}`
- `timeout_s`: Timeout in seconds

### Recommended Columns  
- `seed`: Random seed for reproducibility
- `retries`: Number of retry attempts
- `resource_group`: Resource grouping for execution

### Metrics Expectation Columns (Optional)
- `expected_p95`, `expected_p99`: Expected metric values
- `threshold_p95`, `threshold_p99`: Threshold limits

### Example cases.csv
```csv
case_id,backend,cmd_template,timeout_s,seed,retries,resource_group,expected_p95,threshold_p95
test-01,shell,"echo 'p95=0.05 p99=0.08 throughput_rps=1000'",10,42,2,default,0.05,0.06
test-02,simroute,"python -m cli_run --seed {seed}",120,123,3,compute,0.10,0.12
```

## Metrics CSV Output

### Required Columns (Fixed Order)
```csv
case_id,status,run_seconds,p95,p99,throughput_rps,errors,ts_start,ts_end
```

### Status Values
- `OK`: Successful execution
- `FAIL`: Execution failed
- `TIMEOUT`: Execution timed out

### Additional Columns
- Performance: `cpu_util`, `mem_peak_mb`, `queue_depth_p95`
- Parameters: `param_*` (input case parameters)
- Extensions: `ext_*`, `tag_*`, `note_*`

## Features

### 🔄 Deterministic Execution
- Same input always produces same output
- Fixed column ordering in CSV files
- Consistent number formatting
- LF line endings enforced

### 💾 Intelligent Caching
- `case_hash` calculated from deterministic case elements
- Automatic cache hit detection
- `--force` flag to override cache

### 📊 Threshold Validation
- Automatic metric threshold checking
- Exit code 2 for threshold violations
- Detailed violation reporting

### 🔧 Multiple Backends
- `shell`: Execute shell commands
- `dummy`: Testing/simulation backend
- `simroute`: Integration with world-simulation (extras dependency)

### 📝 Rich Logging
- JST timezone run logs
- Execution summaries with statistics
- Artifact tracking
- Error reporting

## Environment Variables

- `RUN_LOG_DIR`: Directory for run logs (default: `docs/run`)
- `RUN_LOG_WRITE_COMPAT`: Compatibility mode flag (default: `0`)

## Integration with Strataregula

This plugin integrates with Strataregula through entry points:

```toml
[project.entry-points."strataregula.plugins"]
"doe_runner" = "strataregula_doe_runner.plugin:DOERunnerPlugin"
```

When installed, it's automatically discoverable by the Strataregula framework.

### Plugin Commands
- `execute_cases`: Run cases from CSV
- `validate_cases`: Validate case format  
- `get_progress`: Check execution progress
- `export_results`: Export execution results

## Development

```bash
# Clone repository
git clone https://github.com/strataregula/strataregula-doe-runner
cd strataregula-doe-runner

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=strataregula_doe_runner

# Format code
black src tests
isort src tests

# Type checking
mypy src
```

## Examples

See the `examples/` directory for:
- `simple/`: Basic cases.csv example
- `complex/`: Advanced configuration with all features
- `simroute/`: Integration with world-simulation

## License

Apache License 2.0 - see [LICENSE](LICENSE) file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

- 📚 [Documentation](https://strataregula-doe-runner.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/strataregula/strataregula-doe-runner/issues)
- 💬 [Discussions](https://github.com/strataregula/strataregula-doe-runner/discussions)