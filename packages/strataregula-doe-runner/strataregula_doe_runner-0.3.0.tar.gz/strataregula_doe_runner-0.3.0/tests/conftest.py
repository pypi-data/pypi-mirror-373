import os
import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
os.environ.setdefault("USE_STRATAREGULA", "true")
warnings.filterwarnings("ignore", category=DeprecationWarning)


def pytest_configure(config: pytest.Config) -> None:  # pragma: no cover - test hook
    """Apply global warning suppression for the default test suite."""
    warnings.filterwarnings("ignore", category=DeprecationWarning)


def _load_quarantine():
    """Load flaky test quarantine list from YAML file."""
    import yaml

    p = Path(__file__).parent / "flaky_quarantine.yaml"
    if not p.exists():
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def pytest_collection_modifyitems(session, config, items):
    """Automatically mark quarantined flaky tests as xfail."""
    quarantine = _load_quarantine()
    if not quarantine:
        return

    for item in items:
        # Exact nodeid match
        reason = quarantine.get(item.nodeid)
        if reason:
            item.add_marker(
                pytest.mark.xfail(reason=f"quarantined: {reason}", strict=False)
            )
            continue

        # Partial match for flexibility
        for quarantine_pattern, reason in quarantine.items():
            if quarantine_pattern in item.nodeid:
                item.add_marker(
                    pytest.mark.xfail(reason=f"quarantined: {reason}", strict=False)
                )
                break
