# Changelog

## Unreleased

- `ccstay mem` shows real memory use by terminal, session and app, ranks idle sessions to sleep first, and `--sleep` does it
- `/ccstay page` refreshes the folders page and publishes it to the same private link
- `ccstay popup [name]` brings a session's window to the front, or opens one for a session with none
- `setup` adds `/ccstay` to Claude Code, so every command works from a phone, such as `/ccstay popup`; `uninstall` removes it

## 0.2.3

- `sleep` finds the conversation of a session whose folder moved and asks before going ahead; `-y` skips the question
- A closed session whose folder moved is no longer marked gone

## 0.2.2

- The folders page lists every closed session, not just 15
- The folders page picks its look from a sheet with a preview, description and author, so it fits any number of themes
- `folders --theme <name>` is remembered for the next page

## 0.2.1

- `doctor` failures and crashes say how to get them fixed
- Themes can no longer contain network calls or run other code; `ccstay themes` reports the ones that do
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
