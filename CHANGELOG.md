# Changelog

## Unreleased

- macOS Terminal works: each session opens in its own window, with `-t terminal` or when you run ccstay from Terminal
- Pressing Ctrl-D or Ctrl-C at a `setup` prompt cancels cleanly

## 0.2.0

- `setup` asks which terminal to use when both iTerm and Ghostty are installed
- The `folders` page has two looks, Bento and Desk Mates, with a character per session; the viewer switches at the top and the choice is remembered on that phone
- The page reads in English or Traditional Chinese, following the phone's language
- Looks are themes in `themes/<name>/`; `ccstay themes` lists them, `ccstay folders --theme <name>` picks the default, personal ones go in `~/.config/ccstay/themes/`; see `themes/README.md`

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
