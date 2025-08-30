import argparse
from sc_orchestrator.core import run

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--state-dir", required=True)
    ap.add_argument("--outputs-dir", required=True)
    ap.add_argument("--logs-dir", required=True)
    args = ap.parse_args()
    return run(args.config, args.state_dir, args.outputs_dir, args.logs_dir)
