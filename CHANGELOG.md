# Changelog

## Unreleased

- `setup` asks which terminal to use when both iTerm and Ghostty are installed

## 0.1.1

- `folders` lists recently closed sessions with a command to reopen each
- `closed` and the page show when a session was last used, not when ccstay noticed it ended

## 0.1.0

First release.

- Sessions on a private tmux server, in iTerm or Ghostty tabs, or directly in iTerm tabs
- Sleep, wake, reload in place, and restore after a reboot, with window and tab order
- A permanent record of every session: open, suspect, closed, interrupted, gone
- `close`, `closed` and `reopen`
- `board`, `folders`, `doctor`, `uninstall`
- Optional timer and hooks
- `setup` turns on the timer and hooks, then runs `doctor`
