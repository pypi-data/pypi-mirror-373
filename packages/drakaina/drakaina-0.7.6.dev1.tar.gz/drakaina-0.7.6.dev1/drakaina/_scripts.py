"""
Helper scripts exposed via [project.scripts] for uv run.

This module defines console entry points used in local development workflows.
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys


def publish_test() -> int:
    """Publish built distributions to the test repository using Twine.

    - Repository is taken from env var DRAKAINA_TWINE_REPO (default: "drakaina-test").
    - All files under "dist/" are uploaded.
    - Returns the subprocess exit code.
    """
    repo = os.environ.get("DRAKAINA_TWINE_REPO", "drakaina-test")
    files: list[str] = (
        sorted(glob.glob("dist/*.whl")) + sorted(glob.glob("dist/*.tar.gz"))
    )
    if not files:
        print(
            "No distribution files found in dist/. Build first, e.g.:\n"
            "  uv run -- python -m build\n",
            file=sys.stderr,
        )
        return 1

    # Validate distributions before uploading
    check_cmd = [sys.executable, "-m", "twine", "check", *files]
    print(f"Checking: {' '.join(check_cmd)}")
    rc = subprocess.call(check_cmd)
    if rc != 0:
        return rc

    cmd = [
        sys.executable,
        "-m",
        "twine",
        "upload",
        "--repository",
        repo,
        *files,
    ]
    print(f"Running: {' '.join(cmd)}")
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        return 130
