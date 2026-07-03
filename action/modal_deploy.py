#!/usr/bin/env python3
"""
modal_deploy.py — Git2Modal Helper Script

Provides utility functions used by the GitHub Action entrypoint:
  - `auth`  : Verify Modal credentials are valid
  - `deploy`: Deploy a Modal app from a given path

Usage:
    python3 modal_deploy.py auth
    python3 modal_deploy.py deploy <path> [--name <app_name>] [args...]
"""

import os
import subprocess
import sys
from pathlib import Path


def check_auth() -> None:
    """Verify that the Modal token credentials are correctly configured."""
    token_id = os.environ.get("MODAL_TOKEN_ID", "")
    token_secret = os.environ.get("MODAL_TOKEN_SECRET", "")

    if not token_id or not token_secret:
        print("❌ ERROR: MODAL_TOKEN_ID and MODAL_TOKEN_SECRET must be set.", file=sys.stderr)
        sys.exit(1)

    # Try to run `modal token list` or just verify the env vars look valid
    try:
        result = subprocess.run(
            ["modal", "environment", "list"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"⚠️  Warning: Could not list environments: {result.stderr.strip()}", file=sys.stderr)
            print("   Credentials are set but may not be valid.")
            sys.exit(1)
        print(f"✅ Authenticated. Available environments:\n{result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ ERROR: 'modal' CLI not found. Is it installed?", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("⚠️  Warning: auth check timed out. Proceeding anyway.", file=sys.stderr)


def run_deploy(args: list[str]) -> None:
    """Run `modal deploy` with the given arguments."""
    if not args:
        print("❌ ERROR: deploy path is required.", file=sys.stderr)
        sys.exit(1)

    target = args[0]
    # Remove the target from args so we can pass the rest to modal
    rest = args[1:]

    if not Path(target).exists():
        print(f"❌ ERROR: deploy path '{target}' does not exist.", file=sys.stderr)
        sys.exit(1)

    cmd = ["modal", "deploy"] + rest + [target]
    print(f"⚙️  Running: {' '.join(cmd)}")

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    command_args = sys.argv[2:]

    if command == "auth":
        check_auth()
    elif command == "deploy":
        run_deploy(command_args)
    else:
        print(f"❌ Unknown command: {command}", file=sys.stderr)
        print("Available commands: auth, deploy", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()