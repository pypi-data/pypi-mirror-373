import os, requests

def fetch_inventory(cfg):
    base = cfg.get("base_url")
    api_key = os.getenv(cfg.get("auth_env", "SUPEROPS_API_KEY"))
    if not api_key or not base:
        return {"error": "missing SUPEROPS config or key"}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    url = f"{base}/v1/assets"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    items = resp.json()
    return {"assets": items}
