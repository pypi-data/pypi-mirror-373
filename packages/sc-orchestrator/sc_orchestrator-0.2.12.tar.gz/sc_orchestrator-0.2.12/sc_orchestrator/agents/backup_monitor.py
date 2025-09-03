from pathlib import Path
import json, datetime as dt, logging

logger = logging.getLogger(__name__)

def run(datasets, cfg, out_dir: Path, external_changed: bool, run_timeline_only: bool) -> bool:
    logger.info(f"Starting backup monitor: run_timeline_only={run_timeline_only}, external_changed={external_changed}")
    
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = datasets.get("veeam", {}).get("jobs", [])
    report = {"generated_at": dt.datetime.utcnow().isoformat(), "jobs": jobs}
    
    output_path = out_dir / "backup_status.json"
    output_path.write_text(json.dumps(report, indent=2))
    
    logger.info(f"Backup monitor completed: wrote {output_path}, jobs_count={len(jobs)}")
    return True
