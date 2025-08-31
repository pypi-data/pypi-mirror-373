from pathlib import Path
import datetime as dt, logging

logger = logging.getLogger(__name__)

def run(datasets, cfg, out_dir: Path, external_changed: bool, run_timeline_only: bool) -> bool:
    logger.info(f"Starting project manager: run_timeline_only={run_timeline_only}, external_changed={external_changed}")
    
    out_dir.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.utcnow().strftime("%Y-%m-%d")
    report = ["# Project Status", "", f"Run: {now}", ""]
    if not run_timeline_only:
        inv_count = len(datasets.get("superops", {}).get("assets", []))
        report.append(f"- Inventory assets: {inv_count}")
        logger.info(f"Processed {inv_count} inventory assets")
    
    output_path = out_dir / "pm_status.md"
    output_path.write_text("\n".join(report))
    
    logger.info(f"Project manager completed: wrote {output_path}")
    return True
