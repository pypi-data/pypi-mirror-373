import os, requests, logging

logger = logging.getLogger(__name__)

def fetch_vulns(cfg):
    base = cfg.get("base_url")
    token = os.getenv(cfg.get("auth_env", "GALACTIC_TOKEN"))
    
    # Log start with sanitized URL (no auth info)
    logger.info(f"Starting Galactic fetch from {base}")
    
    if not token or not base:
        logger.error("Missing Galactic config or token")
        return {"error": "missing GALACTIC config or token"}
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    url = f"{base}/v1/findings?status=open"  # Replace with actual endpoint
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    findings = resp.json()
    
    logger.info(f"Galactic fetch completed: status={resp.status_code}, findings_count={len(findings) if isinstance(findings, list) else 'unknown'}")
    return {"findings": findings}
