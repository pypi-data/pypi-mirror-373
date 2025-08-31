import os, requests, logging

logger = logging.getLogger(__name__)

def fetch_backup_status(cfg):
    base = cfg.get("base_url")
    api_key = os.getenv(cfg.get("auth_env", "VEEAM_API_KEY"))
    
    # Log start with sanitized URL (no auth info)
    logger.info(f"Starting Veeam fetch from {base}")
    
    if not api_key or not base:
        logger.error("Missing Veeam config or API key")
        return {"error": "missing VEEAM config or key"}
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    url = f"{base}/v1/jobs"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    jobs = resp.json()
    
    logger.info(f"Veeam fetch completed: status={resp.status_code}, jobs_count={len(jobs) if isinstance(jobs, list) else 'unknown'}")
    return {"jobs": jobs}
