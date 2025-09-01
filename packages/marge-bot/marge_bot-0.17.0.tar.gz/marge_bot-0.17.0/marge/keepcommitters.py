#!/usr/bin/env python3
"""Executable script to pass to git rebase to keep the original committer data."""

import os
import subprocess
import sys
from typing import NoReturn

STDERR = sys.stderr.buffer


def die(msg: str) -> NoReturn:
    STDERR.write(b"ERROR: ")
    STDERR.write(msg.encode())
    STDERR.write(b"\n")
    sys.exit(1)


def get_log_info(git_format: str, oid: str) -> str:
    subp = subprocess.run(
        ["git", "log", f"--format={git_format}", "-1", oid],
        capture_output=True,
        check=False,
        text=True,
    )
    if subp.returncode:
        die(subp.stderr)
    return subp.stdout.strip()


def get_committer_env(oid: str) -> dict[str, str]:
    env = {}
    env["GIT_COMMITTER_DATE"] = get_log_info("%cD", oid)
    env["GIT_COMMITTER_NAME"] = get_log_info("%cn", oid)
    env["GIT_COMMITTER_EMAIL"] = get_log_info("%ce", oid)
    return env


def main(oid: str) -> int:
    committer_env = os.environ.copy()
    committer_env.update(get_committer_env(oid))
    subp = subprocess.run(
        ["git", "commit", "--amend", "--no-edit", "--allow-empty"],
        capture_output=True,
        check=False,
        env=committer_env,
        text=True,
    )
    if subp.returncode:
        die(subp.stderr)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        die("Missing OID (sha) argument")
    sys.exit(main(sys.argv[1]))
