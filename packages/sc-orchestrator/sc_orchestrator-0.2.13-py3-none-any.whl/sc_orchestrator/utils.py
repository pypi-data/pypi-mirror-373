import os, json, hashlib, datetime as dt, subprocess
from pathlib import Path
from typing import Any, Dict
import pytz

def now_in_tz(tz_name: str) -> dt.datetime:
    return dt.datetime.now(pytz.timezone(tz_name))

def parse_time(s: str) -> dt.time:
    return dt.datetime.strptime(s, "%H:%M").time()

def within_work_window(now: dt.datetime, schedule: Dict[str, Any]) -> bool:
    wd = schedule.get("workdays", [])
    if not wd:
        return False
    start = parse_time(schedule.get("work_hours", {}).get("start", "00:00"))
    end = parse_time(schedule.get("work_hours", {}).get("end", "23:59"))
    in_day = now.strftime("%a") in wd
    in_time = start <= now.time() <= end
    return in_day and in_time

def cadence_due(now: dt.datetime, schedule: Dict[str, Any], last_due_ts: str | None) -> bool:
    if last_due_ts is None:
        return True
    try:
        last = dt.datetime.fromisoformat(last_due_ts)
    except Exception:
        last = now - dt.timedelta(hours=1)
    if last.tzinfo is None:
        last = last.replace(tzinfo=now.tzinfo)
    if within_work_window(now, schedule):
        return (now - last).total_seconds() >= 3600
    else:
        off = schedule.get("off_hours", {}).get("cadence", "8h")
        seconds = 8 * 3600 if off.endswith("8h") else 8 * 3600
        return (now - last).total_seconds() >= seconds

def load_state(path: Path) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text())
    return {}

def save_state(path: Path, state: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))

def get_head_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return ""

def hash_dict(d: Any) -> str:
    def _norm(o):
        if isinstance(o, dict):
            return {k: _norm(o[k]) for k in sorted(o)}
        if isinstance(o, list):
            return [_norm(x) for x in o]
        return o
    data = json.dumps(_norm(d), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode()).hexdigest()

def ensure_dir(p: str | Path):
    Path(p).mkdir(parents=True, exist_ok=True)

def set_github_output(name: str, value: str):
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"{name}={value}\n")
