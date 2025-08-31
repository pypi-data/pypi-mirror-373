import os, json, yaml, logging, datetime as dt
from pathlib import Path
from typing import Dict, Any
from .utils import (
    now_in_tz, within_work_window, cadence_due, load_state, save_state,
    get_head_sha, hash_dict, ensure_dir, set_github_output
)
from .plugin_loader import load_connectors, load_agents

def _setup_logging(logs_dir: str, cfg: Dict[str, Any]) -> None:
    """Setup logging with file handlers and console output."""
    # Create timestamped log filename
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_log_path = Path(logs_dir) / f"run-{timestamp}.log"
    latest_log_path = Path(logs_dir) / "latest.log"
    
    # Get log level from config or environment
    log_level_str = os.getenv("LOG_LEVEL") or cfg.get("logging", {}).get("level", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    
    # File handler for timestamped run log
    run_handler = logging.FileHandler(run_log_path, mode='w')
    run_handler.setFormatter(formatter)
    run_handler.setLevel(log_level)
    root_logger.addHandler(run_handler)
    
    # File handler for latest.log
    latest_handler = logging.FileHandler(latest_log_path, mode='w')
    latest_handler.setFormatter(formatter)
    latest_handler.setLevel(log_level)
    root_logger.addHandler(latest_handler)
    
    # Console handler for stdout
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

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
    
    # Setup logging
    _setup_logging(logs_dir, cfg)
    logger = logging.getLogger("sc_orchestrator")
    
    logger.info(f"Starting orchestrator run")
    logger.info(f"Config path: {config_path}")
    logger.info(f"State dir: {state_dir}, Outputs dir: {outputs_dir}, Logs dir: {logs_dir}")

    overrides = _load_dispatch_overrides()
    force_run = overrides.get("force_run", False)
    timeline_only_override = overrides.get("timeline_only", False)
    modules_override = overrides.get("modules")
    
    logger.info(f"Dispatch overrides: force_run={force_run}, timeline_only={timeline_only_override}, modules={modules_override}")

    tz = cfg.get("timezone", "UTC")
    logger.info(f"Timezone: {tz}")
    now = now_in_tz(tz)
    out_run_dir = Path(outputs_dir) / "latest"
    ensure_dir(out_run_dir)

    state = load_state(Path(state_dir) / "state.json")
    last_repo_sha = state.get("last_repo_sha")
    head_sha = get_head_sha()
    logger.info(f"Repository SHA: head={head_sha}, last={last_repo_sha}")

    if not force_run:
        due = cadence_due(now, cfg.get("schedule", {}), state.get("last_due_ts"))
        logger.info(f"Cadence check: due={due}")
        if not due:
            logger.info("Skipping run: cadence not due")
            set_github_output("created_changes", "false")
            print("Skip: cadence not due.")
            return 0

    repo_changed = (head_sha != last_repo_sha)
    run_timeline_only = timeline_only_override or (not repo_changed)
    logger.info(f"Run mode: repo_changed={repo_changed}, run_timeline_only={run_timeline_only}")

    connectors = load_connectors(cfg)
    datasets: Dict[str, Any] = {}
    ext_hash_inputs = {}
    
    for name, fetcher in connectors.items():
        logger.info(f"Starting connector fetch: {name}")
        start_time = dt.datetime.now()
        try:
            payload = fetcher()
            elapsed = (dt.datetime.now() - start_time).total_seconds()
            # Log summary without sensitive data
            if isinstance(payload, dict):
                if "error" in payload:
                    logger.info(f"Connector {name} completed with error in {elapsed:.2f}s: {payload.get('error')}")
                else:
                    keys = list(payload.keys())
                    logger.info(f"Connector {name} completed in {elapsed:.2f}s with keys: {keys}")
            else:
                logger.info(f"Connector {name} completed in {elapsed:.2f}s")
        except Exception as e:
            elapsed = (dt.datetime.now() - start_time).total_seconds()
            logger.error(f"Connector {name} failed after {elapsed:.2f}s: {str(e)}")
            payload = {"error": str(e)}
        
        datasets[name] = payload
        ext_hash_inputs[name] = hash_dict(payload)
    
    external_hash = hash_dict(ext_hash_inputs)
    external_changed = external_hash != state.get("last_external_hash")
    logger.info(f"External data: hash={external_hash[:8]}..., changed={external_changed}")

    agents = load_agents(cfg, modules_override)
    created_changes = False
    
    for name, agent in agents.items():
        logger.info(f"Starting agent run: {name}")
        start_time = dt.datetime.now()
        changed = agent(
            datasets=datasets,
            cfg=cfg,
            out_dir=out_run_dir,
            external_changed=external_changed,
            run_timeline_only=run_timeline_only,
        )
        elapsed = (dt.datetime.now() - start_time).total_seconds()
        logger.info(f"Agent {name} completed in {elapsed:.2f}s, changed={bool(changed)}")
        created_changes = created_changes or bool(changed)

    state["last_repo_sha"] = head_sha
    state["last_external_hash"] = external_hash
    state["last_due_ts"] = now.isoformat()
    save_state(Path(state_dir) / "state.json", state)

    logger.info(f"Run completed: created_changes={created_changes}")
    set_github_output("created_changes", "true" if created_changes else "false")
    print(f"Done. Changes created: {created_changes}")
    return 0
