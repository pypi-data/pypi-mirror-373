from pathlib import Path
import json, datetime as dt

def run(datasets, cfg, out_dir: Path, external_changed: bool, run_timeline_only: bool) -> bool:
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = datasets.get("veeam", {}).get("jobs", [])
    report = {"generated_at": dt.datetime.utcnow().isoformat(), "jobs": jobs}
    (out_dir / "backup_status.json").write_text(json.dumps(report, indent=2))
    return True
