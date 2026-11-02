# Security

Please report vulnerabilities through [GitHub private reporting](https://github.com/ttcat/ccstay/security/advisories/new), not in a public issue.

## What to know

- ccstay makes no network calls of its own. `ccstay reload -y` runs Claude Code's own updater.
- Records and the saved screens of sleeping sessions live in `~/.local/state/ccstay`, readable only by you. Screens can hold anything that was on your terminal.
- `ccstay folders` writes session links into an HTML file. Treat it as private.
- `--trust` answers yes to Claude Code's folder trust prompt.
- `ccstay hooks on` adds commands to Claude Code's `settings.json` and keeps a backup beside it.
