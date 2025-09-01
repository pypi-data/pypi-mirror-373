import datetime
import os
from dataclasses import dataclass
from pathlib import Path


def _b(env: str, default: bool) -> bool:
    v = os.getenv(env)
    return default if v is None else v not in ("0", "false", "False", "off", "OFF")


def _run_id() -> str:
    jst = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(jst).strftime("%Y%m%d-%H%M%S-JST")


@dataclass(frozen=True)
class Config:
    obs_enabled: bool = _b("SR_OBS_ENABLED", False)
    save_stdout: bool = _b("SR_SAVE_STDOUT", False)
    trace_level: str = os.getenv("SR_TRACE_LEVEL", "none")
    artifacts_dir: Path = Path(os.getenv("SR_ARTIFACTS_DIR", "artifacts"))
    run_id: str = os.getenv("SR_RUN_ID", _run_id())
