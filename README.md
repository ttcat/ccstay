# ccstay

**Never lose a Claude Code session.** Close a tab, reboot, or let one sit idle: it stays, and you can find it again.

[繁體中文](README.zh-TW.md)

- **Closing a tab ends nothing.** Sessions run on a private tmux server. You never see tmux: no status bar, no prefix key, and your own tmux setup is left alone.
- **Idle sessions sleep.** A claude process of about 300 MB becomes an idle shell of about 2 MB. The tab stays; press Enter to resume the same conversation.
- **Reboots are survivable.** `ccstay restore` brings back what was running, asleep ones stay asleep, in their windows and tab order.
- **Closed is not gone.** Every session keeps a record, so you can search for it and reopen it later.
- **Works from your phone.** Sessions stay reachable through Remote Control, and `ccstay folders` writes a page that links to each one.

No daemon. One Python file with no dependencies.

| Where it runs | Start with | Survives closing the tab |
|---|---|---|
| iTerm + tmux | `ccstay new <folder>` | Yes |
| Ghostty + tmux | `ccstay new <folder> -t ghostty` | Yes |
| iTerm tab, no tmux | `ccstay new <folder> --no-tmux` | No |

`ccstay ls` also finds Claude Code sessions already running in iTerm tabs. Every command below works on them, except `attach` and `open`. Auto-sleep only applies to tmux sessions.

| You want to | Run |
|---|---|
| Start a session | `ccstay new <folder> [name]` |
| See everything | `ccstay ls` |
| Show a session here, or in a new tab | `ccstay attach <name>`, `ccstay open <name>` |
| Free a session's memory, keep its tab | `ccstay sleep <name>`; press Enter or `ccstay wake <name>` |
| Update Claude Code, restart idle sessions in place | `ccstay reload`, then `ccstay reload -y` |
| Bring everything back after a reboot | `ccstay restore [--tabs]` |
| End a session on purpose | `ccstay close <name>` |
| Find sessions that ended | `ccstay closed [text]` |
| Reopen one | `ccstay reopen <name or id>` |
| Overview of projects | `ccstay board [days]` |
| Phone-friendly list of sessions | `ccstay folders` |

## Install

Needs Python 3.9+, tmux 3.2+ and Claude Code. Opening tabs needs macOS with iTerm2 or Ghostty 1.4+; anywhere else sessions run detached and you use `ccstay attach`.

```sh
git clone https://github.com/ttcat/ccstay && cd ccstay
uv tool install .     # or: pipx install .   or: ./install.sh
ccstay timer on       # optional: record state and auto-sleep every minute
ccstay hooks on       # optional: notice /exit at once
ccstay doctor         # check that everything works
```

The first tab opened in each terminal triggers a macOS Automation permission prompt.

## Light by design

- **No daemon.** A timer runs `ccstay tick` and exits: launchd on macOS, systemd on Linux.
- **One tmux server** for all sessions, about 3 MB.
- **Sleeping costs almost nothing.** A claude process of about 300 MB becomes one idle `/bin/sh` of about 2 MB. Sessions idle for 24 hours sleep on their own.
- **Restores are staggered** and only start what was awake.

## What is remembered

Every session keeps a record for good. Nothing is dropped when a session ends.

| State | Meaning | After a reboot |
|---|---|---|
| `open` | Running | Nothing to do |
| `suspect` | Just vanished, checked again a minute later | Nothing to do |
| `closed` | You ended it | Stays closed; use `ccstay reopen` |
| `interrupted` | A reboot, a crash or quitting iTerm took it down | `ccstay restore` brings it back |
| `gone` | Claude Code has deleted the conversation (see `cleanupPeriodDays`) | Listed only |

Shutdown ends sessions without notice, so ccstay judges afterwards: a session counts as closed only if the machine and its terminal are still the same a check later. A wrong guess only moves it to the other list.

`ccstay hooks on` is optional: it adds two hooks to Claude Code's `settings.json` so `/exit` counts as closed at once, and `ccstay hooks off` removes them. Everything works without them, a check later.

Window and tab positions are recorded every minute, and `restore` uses them to put tabs back in their windows.

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `CCSTAY_IDLE_HOURS` | `24` | Auto-sleep after this many idle hours, `0` turns it off |
| `CCSTAY_TERMINAL` | detected | `iterm`, `ghostty` or `none` |
| `CCSTAY_REMOTE` | unset | `1` forces Remote Control on; otherwise Claude Code's own setting decides |
| `CCSTAY_SOCKET` | `ccstay` | tmux socket name |

The timer does not read your shell setup, so after changing one of these, run `ccstay timer on` again to carry it over.

Add your own tmux settings in `$XDG_CONFIG_HOME/ccstay/tmux.conf`, by default `~/.config/ccstay/tmux.conf`.

`ccstay keep <name>` exempts a session from auto-sleep. Sessions that are working, waiting for you, or have no messages yet are never put to sleep.

## What ccstay touches

Nothing outside its own state folder changes unless you ask. It makes no network calls of its own; `ccstay reload -y` runs Claude Code's own updater.

| Place | When | Undo |
|---|---|---|
| `~/.local/bin/ccstay` | `./install.sh` | `ccstay uninstall` |
| `~/.local/state/ccstay/` | Always, for records and tmux config | `ccstay uninstall --purge` |
| `~/Library/LaunchAgents/dev.ccstay.tick.plist` or a systemd user timer | `ccstay timer on` | `ccstay timer off` |
| `~/.claude/settings.json`, backed up once beside it | `ccstay hooks on` | `ccstay hooks off` |

Claude Code's own background sessions stop when idle and do not stay in your terminal tabs. ccstay manages ordinary interactive sessions and keeps your tabs, sleep and reboot restore under your control.

## Uninstall

```sh
ccstay uninstall           # removes the timer, hooks and link
ccstay uninstall --purge   # also deletes ccstay's records, once no sessions run under it
```

Conversations stay in Claude Code. If you used uv or pipx, then run `uv tool uninstall ccstay` or `pipx uninstall ccstay`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [CHANGELOG.md](CHANGELOG.md).

## Development

```sh
python3 -m unittest discover -s tests
```

Tests drive a real tmux with a fake claude and need no account.

MIT License.
