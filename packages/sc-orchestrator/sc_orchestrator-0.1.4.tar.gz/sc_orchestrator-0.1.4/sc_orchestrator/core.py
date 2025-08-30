import os, json, yaml
from pathlib import Path
from typing import Dict, Any
from .utils import (
    now_in_tz, within_work_window, cadence_due, load_state, save_state,
    get_head_sha, hash_dict, ensure_dir, set_github_output
)
from .plugin_loader import load_connectors, load_agents

def _load_dispatch_overrides() -> Dict[str, Any]:
    event_path = os.getenv("GITHUB_EVENT_PATH")
    event_name = os.getenv("GITHUB_EVENT_NAME", "")
    overrides = {}
    if event_name == "repository_dispatch" and event_path and os.path.exists(event_path):
        with open(event_path, "r") as f:
            ev = json.load(f)
        overrides = ev.get("client_payload", {}) or {}
    # workflow_dispatch compatibility
    wf_force = os.getenv("INPUT_FORCE_RUN")
    wf_modules = os.getenv("INPUT_MODULES")
    wf_timeline = os.getenv("INPUT_TIMELINE_ONLY")
    if wf_force:
        overrides["force_run"] = wf_force.lower() == "true"
    if wf_modules:
        mods = [m.strip() for m in wf_modules.split(",") if m.strip()]
        if mods:
            overrides["modules"] = mods
    if wf_timeline:
        overrides["timeline_only"] = wf_timeline.lower() == "true"
    return overrides

def run(config_path: str, state_dir: str, outputs_dir: str, logs_dir: str) -> int:
    ensure_dir(state_dir); ensure_dir(outputs_dir); ensure_dir(logs_dir)
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    overrides = _load_dispatch_overrides()
    force_run = overrides.get("force_run", False)
    timeline_only_override = overrides.get("timeline_only", False)
    modules_override = overrides.get("modules")

    tz = cfg.get("timezone", "UTC")
    now = now_in_tz(tz)
    out_run_dir = Path(outputs_dir) / "latest"
    ensure_dir(out_run_dir)

    state = load_state(Path(state_dir) / "state.json")
    last_repo_sha = state.get("last_repo_sha")
    head_sha = get_head_sha()

    if not force_run:
        due = cadence_due(now, cfg.get("schedule", {}), state.get("last_due_ts"))
        if not due:
            set_github_output("created_changes", "false")
            print("Skip: cadence not due.")
            return 0

    repo_changed = (head_sha != last_repo_sha)
    run_timeline_only = timeline_only_override or (not repo_changed)

    connectors = load_connectors(cfg)
    datasets: Dict[str, Any] = {}
    ext_hash_inputs = {}
    for name, fetcher in connectors.items():
        payload = fetcher()
        datasets[name] = payload
        ext_hash_inputs[name] = hash_dict(payload)
    external_hash = hash_dict(ext_hash_inputs)
    external_changed = external_hash != state.get("last_external_hash")

    agents = load_agents(cfg, modules_override)
    created_changes = False
    for name, agent in agents.items():
        changed = agent(
            datasets=datasets,
            cfg=cfg,
            out_dir=out_run_dir,
            external_changed=external_changed,
            run_timeline_only=run_timeline_only,
        )
        created_changes = created_changes or bool(changed)

    state["last_repo_sha"] = head_sha
    state["last_external_hash"] = external_hash
    state["last_due_ts"] = now.isoformat()
    save_state(Path(state_dir) / "state.json", state)

    set_github_output("created_changes", "true" if created_changes else "false")
    print(f"Done. Changes created: {created_changes}")
    return 0
