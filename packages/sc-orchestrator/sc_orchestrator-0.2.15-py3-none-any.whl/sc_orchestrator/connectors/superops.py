import os, requests, logging

logger = logging.getLogger(__name__)

def fetch_inventory(cfg):
    base = cfg.get("base_url")
    api_key = os.getenv(cfg.get("auth_env", "SUPEROPS_API_KEY"))
    
    # Log start with sanitized URL (no auth info)
    logger.info(f"Starting SuperOps fetch from {base}")
    
    if not api_key or not base:
        logger.error("Missing SuperOps config or API key")
        return {"error": "missing SUPEROPS config or key"}
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    url = f"{base}/v1/assets"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    items = resp.json()
    
    logger.info(f"SuperOps fetch completed: status={resp.status_code}, assets_count={len(items) if isinstance(items, list) else 'unknown'}")
    return {"assets": items}
