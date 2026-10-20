# agent-shell-secret-mask

[![CI](https://github.com/leighsrodney-prog/agent-shell-secret-mask/actions/workflows/ci.yml/badge.svg)](https://github.com/leighsrodney-prog/agent-shell-secret-mask/actions/workflows/ci.yml)

PATH-first **`env` / `printenv` wrapper scripts** for shared AI-agent shells. A casual `env` or
`printenv` prints `NAME=****` instead of values, while `env VAR=x cmd` and `env -i ...` still work.
Includes a **leak test** that checks output against the real values by length and hash, without ever
printing them.

> This is a guard rail against *accidental* exposure in logs and transcripts. It is **not** a security
> boundary. See "What it does NOT stop" below.

## The problem
AI coding agents run shell commands and their output lands in transcripts, logs and screenshots.
One `env` while debugging dumps every API token in the environment. The obvious fix (an alias or
function in `~/.bashrc`) does not work: agents usually run **non-interactive `bash -c "..."`** shells,
which never read `.bashrc`. A wrapper earlier on `PATH` does apply, as long as the agent's `PATH`
puts it first.

Background: public discussion at
[forum.cursor.com: mask secret values in bot shell output](https://forum.cursor.com/t/feature-request-mask-secret-values-in-bot-shell-output/175384).

## What it does
| Command | Result |
|---|---|
| `env`, `env -0`, `env -u NAME` | every variable listed as `NAME=****` (names only) |
| `env VAR=x cmd`, `env -i cmd`, `env cmd` | passed through to `/usr/bin/env` unchanged |
| `printenv` | same masked listing |
| `printenv NAME` | `NAME=<set, masked>` or `NAME=<not set>`, exit 1, no value |

## What it does NOT stop
- Calling the real binary: `/usr/bin/env`, `command env`, `busybox env`.
- `cat /proc/self/environ`, `export -p`, `declare -x`, `set`.
- Deliberate reads: `echo "$TOKEN"`, `python -c 'import os; print(os.environ)'`.
- Programs that log their own config or crash dumps.

## Recommended real fix
Do not keep long-lived secrets in the shell environment at all. Give each script its own
**`chmod 600` secret file** and read it at run time, with an env fallback for CI:

```bash
token_file="$HOME/.config/myscript/token"     # chmod 600, owned by you
if [ -r "$token_file" ]; then TOKEN="$(cat "$token_file")"; else TOKEN="${MYSCRIPT_TOKEN:?no token}"; fi
```
Then nothing is in `env` to leak, and the wrappers become a second layer.

## Install
```bash
./install.sh            # installs to ~/.local/bin
./install.sh /opt/mask  # or any directory
```
Make sure that directory is **first** on the agent's `PATH` (set it where the agent's shell gets its
environment, not in `.bashrc`). Check with `command -v env`.

## Leak test
```bash
python3 leak_test.py            # tests ./bin
python3 leak_test.py ~/.local/bin
```
It runs `env`, `env -0`, `printenv` and `printenv <every name>`, then looks for each real value (6+
chars) in the output. It reports only `NAME (len=N sha256=abcd1234)`, never the value. Exit 1 on a leak.

## Tests
```bash
pip install -r requirements.txt && pytest -q
```
Tests use a fake token in a clean environment.

## License
MIT
