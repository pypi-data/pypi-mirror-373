# sc-orchestrator

Control-only, package-first orchestrator for:
- Project management automation
- vCISO daily posture checks
- Quoting / lifecycle proposals
- Backup monitoring

## Usage (child repo workflow)
```bash
sc-orchestrate --config config/policy.yaml --state-dir .bot/state --outputs-dir outputs --logs-dir logs
```

## Extensibility
- Add new agents under `sc_orchestrator/agents/` (expose `run(...)`).
- Add new connectors under `sc_orchestrator/connectors/` (expose fetchers).
- The orchestrator loads agents enabled in YAML, and fetches each connector once.
