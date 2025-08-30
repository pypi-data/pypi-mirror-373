import os, requests

def fetch_vulns(cfg):
    base = cfg.get("base_url")
    token = os.getenv(cfg.get("auth_env", "GALACTIC_TOKEN"))
    if not token or not base:
        return {"error": "missing GALACTIC config or token"}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    url = f"{base}/v1/findings?status=open"  # Replace with actual endpoint
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return {"findings": resp.json()}
