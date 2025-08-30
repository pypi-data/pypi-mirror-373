from pathlib import Path
import datetime as dt, json

def run(datasets, cfg, out_dir: Path, external_changed: bool, run_timeline_only: bool) -> bool:
    out_dir.mkdir(parents=True, exist_ok=True)
    findings = datasets.get("galactic", {}).get("findings", [])
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")
    rec = {"date": today, "summary": {"open_findings": len(findings)}}
    (out_dir / "security_recommendations.json").write_text(json.dumps(rec, indent=2))
    return True
