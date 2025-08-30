from pathlib import Path
import datetime as dt

def run(datasets, cfg, out_dir: Path, external_changed: bool, run_timeline_only: bool) -> bool:
    out_dir.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.utcnow().strftime("%Y-%m-%d")
    report = ["# Project Status", "", f"Run: {now}", ""]
    if not run_timeline_only:
        inv_count = len(datasets.get("superops", {}).get("assets", []))
        report.append(f"- Inventory assets: {inv_count}")
    (out_dir / "pm_status.md").write_text("\n".join(report))
    return True
