from pathlib import Path
import datetime as dt, json, logging

logger = logging.getLogger(__name__)

def run(datasets, cfg, out_dir: Path, external_changed: bool, run_timeline_only: bool) -> bool:
    logger.info(f"Starting vCISO agent: run_timeline_only={run_timeline_only}, external_changed={external_changed}")
    
    out_dir.mkdir(parents=True, exist_ok=True)
    findings = datasets.get("galactic", {}).get("findings", [])
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")
    rec = {"date": today, "summary": {"open_findings": len(findings)}}
    
    output_path = out_dir / "security_recommendations.json"
    output_path.write_text(json.dumps(rec, indent=2))
    
    logger.info(f"vCISO agent completed: wrote {output_path}, findings_count={len(findings)}")
    return True
