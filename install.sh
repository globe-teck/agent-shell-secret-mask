#!/usr/bin/env bash
# Install the wrappers into a PATH-first directory (default ~/.local/bin).
set -euo pipefail
dest="${1:-$HOME/.local/bin}"
src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/bin"
mkdir -p "$dest"
install -m 0755 "$src/env" "$dest/env"
install -m 0755 "$src/printenv" "$dest/printenv"
echo "Installed env and printenv to $dest"
case ":$PATH:" in
  *":$dest:"*) [ "$(command -v env)" = "$dest/env" ] && echo "OK: $dest is first for env" || echo "WARN: another env comes earlier in PATH" ;;
  *) echo "WARN: $dest is not on PATH. Put it first in PATH for the agent's shell (see README)." ;;
esac
