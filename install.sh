#!/bin/sh
# Link ccstay into ~/.local/bin. No root needed, nothing else is touched.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$HOME/.local/bin"
ln -sf "$here/ccstay.py" "$HOME/.local/bin/ccstay"
command -v tmux >/dev/null || echo "tmux is missing, install it first" >&2
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "add ~/.local/bin to your PATH" >&2 ;; esac
echo "installed: run ccstay --help"
