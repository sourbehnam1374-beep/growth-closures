#!/usr/bin/env python3
"""Run the offline verification stack and preserve a source-bound receipt.

python verifiers/run_verification.py --out verification-logs
python verifiers/run_verification.py --lean lean --out verification-logs
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import py_compile
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
VERIFIERS = ROOT / "verifiers"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "verification-logs")
    parser.add_argument("--lean", help="Also run Lean 4.30.0 using this executable")
    args = parser.parse_args()
    if not __debug__ or os.environ.get("PYTHONOPTIMIZE") not in (None, "", "0"):
        parser.error("Verification requires Python assertions; optimization is forbidden")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    paths = sorted(VERIFIERS.glob("*.py")) + sorted((VERIFIERS / "data").glob("*"))
    paths += [ROOT / "requirements-verification.txt", ROOT / "lean/GrowthClosure.lean",
              ROOT / ".github/workflows/ai-verification.yml"]
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in paths if p.is_file()}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                            capture_output=True)
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True,
                           capture_output=True)
    receipt = {"scope": "python_and_lean" if args.lean else "python",
               "git_head": commit.stdout.strip() if commit.returncode == 0 else None,
               "worktree_dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None,
               "python": platform.python_version(),
               "dependencies": {name: importlib.metadata.version(name)
                                for name in ("hypothesis", "pytest")},
               "source_sha256": source_hashes, "checks": []}
    checks = receipt["checks"]
    try:
        for source in VERIFIERS.glob("*.py"):
            py_compile.compile(str(source), doraise=True)
        checks.append({"name": "python_compile", "returncode": 0})
    except py_compile.PyCompileError as exc:
        checks.append({"name": "python_compile", "returncode": 1, "error": str(exc)})
    pattern = r"^\s*(sorry|admit)(\s|$)|:=\s*(sorry|admit)(\s|$)|by\s+(sorry|admit)(\s|$)|^\s*axiom\s"
    matches = [str(i) + ": " + line for i, line in
               enumerate((ROOT / "lean/GrowthClosure.lean").read_text().splitlines(), 1)
               if re.search(pattern, line)]
    (out / "lean-placeholder-scan.log").write_text("\n".join(matches) if matches else "No source placeholders found.\n")
    checks.append({"name": "lean_source_placeholder_scan", "returncode": int(bool(matches))})
    scripts = ["growth_check.py", "test_growth_properties.py", "delete_growth.py",
               "test_anomaly_characterization.py", "verify_o1_necessity.py",
               "verify_unified.py", "ai_adversarial_verify.py", "corpus_o5.py"]
    commands = [(name, [sys.executable, str(VERIFIERS / name)]) for name in scripts]
    commands.append(("pytest", [sys.executable, "-m", "pytest", str(VERIFIERS), "-q",
                               "--hypothesis-seed=20261027", "-p", "no:cacheprovider"]))
    if args.lean:
        commands += [("lean_version", [args.lean, "--version"]),
                     ("lean_kernel", [args.lean, str(ROOT / "lean/GrowthClosure.lean")])]
    env = {**os.environ, "VERIFY_OUT": str(out), "PYTHONPATH": str(VERIFIERS)}
    for name, command in commands:
        start = time.monotonic()
        try:
            proc = subprocess.run(command, cwd=out, env=env, capture_output=True,
                                  text=True, timeout=180)
            log, code = proc.stdout + proc.stderr, proc.returncode
        except (subprocess.TimeoutExpired, OSError) as exc:
            log, code = str(exc), 1
        if name == "lean_version" and not re.search(r"version 4\.30\.0(?:,|\s|\))", log):
            log += "\nExpected Lean version 4.30.0.\n"
            code = 1
        if re.search(r"\[FAIL\]|\[SKIP\]|ALL CHECKS PASS : False|^.*FAILURE", log, re.MULTILINE):
            code = 1
        (out / (name + ".log")).write_text(log, encoding="utf-8")
        row = {"name": name, "returncode": code, "seconds": round(time.monotonic() - start, 3)}
        checks.append(row)
        print(("PASS " if code == 0 else "FAIL ") + name, flush=True)
    receipt["status"] = "PASS" if all(c["returncode"] == 0 for c in checks) else "FAIL"
    (out / "verification_summary.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("VERIFICATION %s (%s)" % (receipt["status"], receipt["scope"]))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
