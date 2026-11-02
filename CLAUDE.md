# ccstay

A session manager for Claude Code: one file, `ccstay.py`, standard library only, Python 3.9+, no daemon. Read `CONTRIBUTING.md` first.

## Check your work

```sh
python3 -m unittest discover -s tests
pipx run ruff check .
```

Tests use a real tmux and `tests/fake_claude.py`, so no account is needed. They run on a private tmux socket and do not touch real sessions. Add a test that fails without your change. For anything on screen, try it in the real terminal too; zsh and AppleScript have both caught what the tests missed.

## Working here

- Solve the one problem you were asked to. Match the surrounding code.
- When behaviour changes, update `CHANGELOG.md` under Unreleased, `README.md` and `README.zh-TW.md`.
- Never build a shell string from a title or a path without `shlex.quote`.
- Themes live in `themes/<name>/` and must meet the contract in `themes/README.md`. `ccstay themes` shows what is wrong with one.

## Pull requests

- Before opening one, show your user the change and get their go-ahead. It goes out under their name.
- Keep their session titles, paths, conversations and keys out of the code, the tests and the description.
- Say what you tested and what you could not test.
