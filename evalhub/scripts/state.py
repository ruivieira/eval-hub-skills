#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Lightweight key-value state store that survives context compression.

Writes to ~/.evalhub-skills-state.json so job IDs and config persist
across Claude context resets during long-running evaluations.

Commands:
  get KEY              Print value for KEY (empty string if not set)
  set KEY VALUE        Store KEY=VALUE (use empty string to clear)
  status               Print all stored state (compact summary)
  read-ids             Print stored job ID list as JSON array
  write-ids ID [ID...] Replace stored job ID list
"""

import json
import sys
from pathlib import Path

STATE_FILE = Path.home() / ".evalhub-skills-state.json"


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def cmd_get(key: str) -> None:
    state = _load()
    print(state.get(key, ""))


def cmd_set(key: str, value: str) -> None:
    state = _load()
    if value == "":
        state.pop(key, None)
    else:
        state[key] = value
    _save(state)


def cmd_status() -> None:
    state = _load()
    if not state:
        print("No state stored.")
        return
    for k, v in state.items():
        print(f"{k}={v}")


def cmd_read_ids() -> None:
    state = _load()
    ids = state.get("job_ids", [])
    print(json.dumps(ids))


def cmd_write_ids(ids: list[str]) -> None:
    state = _load()
    state["job_ids"] = ids
    _save(state)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "get":
        if len(args) < 2:
            print("Usage: state.py get KEY", file=sys.stderr)
            sys.exit(1)
        cmd_get(args[1])
    elif cmd == "set":
        if len(args) < 3:
            print("Usage: state.py set KEY VALUE", file=sys.stderr)
            sys.exit(1)
        cmd_set(args[1], args[2])
    elif cmd == "status":
        cmd_status()
    elif cmd == "read-ids":
        cmd_read_ids()
    elif cmd == "write-ids":
        cmd_write_ids(args[1:])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print("Commands: get, set, status, read-ids, write-ids", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
