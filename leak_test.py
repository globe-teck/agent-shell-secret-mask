#!/usr/bin/env python3
"""Leak test: run the wrappers and check that no real value appears in their output.

It never prints a value. It reports only variable names, value lengths and a short
sha256 prefix of the value, so you can confirm which variable leaked without exposing it.
Exit code 0 = clean, 1 = leak found.
"""
import hashlib
import os
import subprocess
import sys

MIN_LEN = 6  # short values like "1" or "C" would match by chance


def fingerprint(value: str) -> str:
    return f"len={len(value)} sha256={hashlib.sha256(value.encode()).hexdigest()[:8]}"


def check(cmd, env=None):
    out = subprocess.run(cmd, capture_output=True, env=env).stdout.decode(errors="replace")
    env = env if env is not None else os.environ
    leaks = [n for n, v in env.items() if len(v) >= MIN_LEN and v in out]
    return leaks


def main(argv):
    bindir = argv[1] if len(argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
    env = dict(os.environ)
    env["PATH"] = bindir + os.pathsep + env.get("PATH", "")
    env.setdefault("LEAK_TEST_CANARY", "canary-" + hashlib.sha256(os.urandom(16)).hexdigest()[:20])
    names = sorted(k for k in env if k != "PATH")
    cases = {
        "env": ["env"],
        "env -0": ["env", "-0"],
        "printenv": ["printenv"],
        "printenv NAMES": ["printenv", *names],
    }
    failed = False
    for label, cmd in cases.items():
        leaks = check(cmd, env)
        if leaks:
            failed = True
            for n in leaks:
                print(f"LEAK [{label}] {n} ({fingerprint(env[n])})")
        else:
            print(f"ok   [{label}] no values found in output")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
