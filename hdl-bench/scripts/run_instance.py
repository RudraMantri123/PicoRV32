#!/usr/bin/env python3
"""
HDL Benchmark Instance Runner

Runs a benchmark instance by cloning the repo, applying a patch,
running tests, and checking results.
"""

import json
import subprocess
import sys
import tempfile
import pathlib
import shutil
import os

def run_cmd(cmd, cwd, timeout=None):
    """Run a shell command, return exit code and stdout."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            text=True
        )
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired as e:
        return 124, e.stdout.decode('utf-8', errors='replace') if e.stdout else ""


def main():
    if len(sys.argv) != 3:
        print("Usage: run_instance.py <instance_json> <patch_file>", file=sys.stderr)
        sys.exit(1)

    config_path = pathlib.Path(sys.argv[1]).resolve()
    patch_path = pathlib.Path(sys.argv[2]).resolve()

    # Load config
    with open(config_path) as f:
        cfg = json.load(f)

    # Temp directory for this run
    workdir = pathlib.Path(tempfile.mkdtemp(prefix=cfg["task_id"] + "_"))
    repo_dir = workdir / "repo"

    try:
        print(f"Working directory: {workdir}", file=sys.stderr)

        # Clone repo
        print("Cloning {} ...".format(cfg['repo']), file=sys.stderr)
        code, out = run_cmd(f"git clone {cfg['repo']} repo", cwd=workdir, timeout=300)
        if code != 0:
            return {
                "task_id": cfg["task_id"],
                "status": "fail",
                "reason": "clone_failed",
                "error": out[-500:] if len(out) > 500 else out
            }

        # Checkout baseline
        print("Checking out {} ...".format(cfg['baseline_commit']), file=sys.stderr)
        code, out = run_cmd(f"git checkout {cfg['baseline_commit']}", cwd=repo_dir, timeout=60)
        if code != 0:
            return {
                "task_id": cfg["task_id"],
                "status": "fail",
                "reason": "checkout_failed",
                "error": out[-500:] if len(out) > 500 else out
            }

        # Apply patch
        print("Applying patch {} ...".format(patch_path), file=sys.stderr)
        code, out = run_cmd(f"git apply {patch_path}", cwd=repo_dir, timeout=60)
        if code != 0:
            return {
                "task_id": cfg["task_id"],
                "status": "fail",
                "reason": "patch_failed",
                "error": out[-500:] if len(out) > 500 else out
            }

        # Check allowed paths (optional)
        code, out = run_cmd("git diff --name-only HEAD", cwd=repo_dir, timeout=30)
        if code == 0:
            changed_files = [f.strip() for f in out.split('\n') if f.strip()]
            allowed_paths = cfg.get("allowed_paths", [])
            if allowed_paths:
                for f in changed_files:
                    if not any(f.startswith(prefix) for prefix in allowed_paths):
                        return {
                            "task_id": cfg["task_id"],
                            "status": "fail",
                            "reason": "forbidden_path",
                            "error": f"File {f} not in allowed_paths: {allowed_paths}"
                        }

        # Run tests
        full_log = ""
        all_passed = True

        for cmd in cfg["test_cmds"]:
            print(f"Running: {cmd}", file=sys.stderr)
            code, out = run_cmd(cmd, cwd=repo_dir, timeout=cfg.get("timeout_s", 600))
            full_log += f"\n\n$ {cmd}\n" + out
            if code != 0:
                all_passed = False

        # Check strings
        if all_passed:
            # Forbidden strings
            forbidden_strings = cfg.get("forbidden_strings", [])
            for bad in forbidden_strings:
                if bad in full_log:
                    all_passed = False
                    break

            # Required success strings
            success_strings = cfg.get("success_strings", [])
            for good in success_strings:
                if good not in full_log:
                    all_passed = False
                    break

        # Return result
        result = {
            "task_id": cfg["task_id"],
            "status": "pass" if all_passed else "fail"
        }

        if not all_passed:
            result["log_tail"] = full_log[-1000:] if len(full_log) > 1000 else full_log

        return result

    finally:
        # Cleanup
        print(f"Cleaning up {workdir}", file=sys.stderr)
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    result = main()
    print("=" * 60, file=sys.stderr)
    print("RESULT:", file=sys.stderr)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "pass" else 1)
