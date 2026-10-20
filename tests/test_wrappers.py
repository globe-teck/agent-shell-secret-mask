import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "bin"
FAKE_VAL = "s3cr3t-value-for-tests-0123456789"


def run(args, extra=None):
    env = {"PATH": f"{BIN}:/usr/bin:/bin", "FAKE_TOKEN": FAKE_VAL, "HOME": "/tmp"}
    env.update(extra or {})
    return subprocess.run(args, capture_output=True, text=True, env=env)


def test_env_lists_masked():
    r = run(["env"])
    assert "FAKE_TOKEN=****" in r.stdout
    assert FAKE_VAL not in r.stdout + r.stderr


def test_env_null_and_unset():
    r = run(["env", "-0", "-u", "HOME"])
    entries = [e for e in r.stdout.split("\0") if e]
    assert "FAKE_TOKEN=****" in entries
    assert not any(e.startswith("HOME=") for e in entries)
    assert FAKE_VAL not in r.stdout


def test_env_command_mode_passes_through():
    r = run(["env", "GREETING=hi", "sh", "-c", 'echo "$GREETING"'])
    assert r.stdout.strip() == "hi"


def test_env_i_passes_through():
    r = run(["env", "-i", "A=1", "/usr/bin/env"])
    assert r.stdout.strip() == "A=1"


def test_printenv_refuses_names():
    r = run(["printenv", "FAKE_TOKEN", "MISSING_VAR"])
    assert r.returncode == 1
    assert "FAKE_TOKEN=<set, masked>" in r.stdout
    assert "MISSING_VAR=<not set>" in r.stdout
    assert FAKE_VAL not in r.stdout + r.stderr


def test_printenv_no_args_masked():
    r = run(["printenv"])
    assert "FAKE_TOKEN=****" in r.stdout
    assert FAKE_VAL not in r.stdout


def test_leak_test_clean():
    r = run(["python3", str(ROOT / "leak_test.py"), str(BIN)])
    assert r.returncode == 0, r.stdout
    assert FAKE_VAL not in r.stdout


def test_install(tmp_path):
    r = run(["bash", str(ROOT / "install.sh"), str(tmp_path)])
    assert r.returncode == 0
    assert os.access(tmp_path / "env", os.X_OK)
    assert os.access(tmp_path / "printenv", os.X_OK)
