# Changelog

## 0.2.5

- `setup` asks whether sessions should come back in their tabs by themselves after each restart (macOS). `ccstay autorestore on|off` changes it later, and `uninstall` removes it
- `restore` opens every tab first, then starts the sessions one by one, oldest first, waiting until each one is up instead of a fixed 2 seconds. It is faster, and the Claude app lists them in the order they had before the restart

## 0.2.4

- `ccstay mem` shows real memory use by terminal, session and app, ranks idle sessions to sleep first, and `--sleep` does it
- `/ccstay page` refreshes the folders page and publishes it to the same private link
- `ccstay popup [name]` brings a session's window to the front, or opens one for a session with none
- `setup` adds `/ccstay` to Claude Code, so every command works from a phone, such as `/ccstay popup`; `uninstall` removes it
- A session whose claude is slow to exit still goes to sleep; it used to vanish with its tab
- A tab you closed yourself is no longer brought back by `restore`; the timer and your shell disagreed on how to write a date. Sessions in plain tabs are judged once more after upgrading
- `reload -y` leaves a session waiting for your answer alone
- Folders with long paths or emoji in the name find their conversations, so their sessions can sleep
- A title starting with `=` no longer breaks waking a session in a plain iTerm tab
- A crashed session whose process number was reused is no longer listed or closed
- `mem` shows the memory pressure macOS reports instead of calling a full swap critical
- Warp is no longer mistaken for Terminal
- Sessions whose conversation is deleted are not searched for again each minute

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
