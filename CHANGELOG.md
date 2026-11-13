# Changelog

## Unreleased

- `wake`, `reopen`, `restore` and `reload` answer Claude's folder trust prompt when it comes back for a conversation that was already trusted. Claude never saves trust for the home folder, so a session there started again sat at the prompt forever, and `ccstay ls` could not see it
- With Claude Code's "Remote Control at startup" setting on, a session keeps its name in `ccstay ls` across sleep, wake and restart. Since 0.2.8 the name only reached Remote Control, so Claude gave the session a new random name (`project-a2`, then `project-76`) on every start, and `ccstay wake <old name>` found nothing

## 0.2.9

- `ccstay terminal [auto|iterm|ghostty|terminal|herdr|none]` shows or sets where new sessions open. Before, the choice could only be made once, during `ccstay setup`
- Sessions can live in [herdr](https://herdr.dev) instead of tmux: `ccstay new <folder> -t herdr`, or run ccstay from a herdr terminal. `ls`, `sleep`, `wake`, auto-sleep, `close`, `closed`, `reopen`, `restore`, `reload`, `open`, `popup`, `attach`, `mem` and the folders page all cover them. Before, a session in herdr was invisible to ccstay, and since herdr calls itself `ghostty` in `TERM_PROGRAM`, new sessions started from it opened in Ghostty
- A session started in an iTerm tab without tmux uses the Claude config folder of the command that started it, as tmux sessions have since 0.2.7

## 0.2.8

- With Claude Code's "Remote Control at startup" setting on, sessions ccstay starts or restarts show their own name in the Claude app. Before, a new Remote Control connection was named after the computer (`macbook-air-local-…`) because the name was passed with `-n`, which Remote Control ignores

## 0.2.7

- Sessions started, put to sleep or woken by ccstay use the Claude config folder (`CLAUDE_CONFIG_DIR`) of the command that started them. Before, a tmux server already running kept the folder it started with, so a second account in its own folder could not be used from ccstay

## 0.2.6

- `ccstay page on` keeps the published folders page up to date by itself: a small helper session republishes it within about two minutes of any session starting, ending, sleeping, waking or changing state. `ccstay page off` stops it
- On the folders page, tapping an asleep session copies its wake command, `ccstay wake <id>`, to paste into any Remote Control session. `wake` accepts the first 8 characters of the session id

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
