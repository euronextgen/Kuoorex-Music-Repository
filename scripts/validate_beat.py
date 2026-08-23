#!/usr/bin/env python3
"""
validate_beat.py — Validate a beat's info.json against the Kuoorex schema.

Usage:
    python scripts/validate_beat.py beats/<slug>/info.json
    python scripts/validate_beat.py beats/  # validate all beats
"""

import sys
import json
import os
from pathlib import Path

def load_schema():
    schema_path = Path(__file__).parent.parent / "schema" / "beat.schema.json"
    if not schema_path.exists():
        print(f"ERROR: Schema not found at {schema_path}")
        sys.exit(1)
    with open(schema_path) as f:
        return json.load(f)

def validate_file(info_path: Path, schema: dict) -> bool:
    try:
        import jsonschema
    except ImportError:
        print("ERROR: jsonschema not installed. Run: pip install jsonschema")
        sys.exit(1)

    if not info_path.exists():
        print(f"  MISSING  {info_path}")
        return False

    try:
        with open(info_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  INVALID JSON  {info_path}: {e}")
        return False

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    if not errors:
        title = data.get("title", info_path.parent.name)
        bpm   = data.get("audio", {}).get("bpm", "?")
        mood  = data.get("audio", {}).get("mood", "?")
        print(f"  OK  {info_path.parent.name!s:<35} | {title:<30} | {bpm} BPM | {mood}")
        return True
    else:
        print(f"  FAIL  {info_path}")
        for err in errors:
            path = " > ".join(str(p) for p in err.absolute_path) or "(root)"
            print(f"       [{path}] {err.message}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_beat.py <path>")
        sys.exit(1)

    schema = load_schema()
    target = Path(sys.argv[1])

    # Validate all beats if given the beats/ dir
    if target.is_dir() and target.name == "beats":
        paths = sorted(target.glob("*/info.json"))
        # skip special dirs
        paths = [p for p in paths if not p.parent.name.startswith("_")]
        if not paths:
            print("No beats found.")
            sys.exit(0)
    elif target.is_dir():
        paths = [target / "info.json"]
    else:
        paths = [target]

    print(f"\nKuoorex beat validator - schema v2.0\n{'-' * 60}")
    results = [validate_file(p, schema) for p in paths]
    ok  = sum(results)
    fail = len(results) - ok
    print(f"{'-' * 60}")
    print(f"  {ok} passed | {fail} failed | {len(results)} total\n")
    sys.exit(0 if fail == 0 else 1)

if __name__ == "__main__":
    main()
