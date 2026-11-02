# Contributing

ccstay stays small on purpose: one Python file, standard library only, no daemon. The folders page has themes in `themes/`; to add one, read [themes/README.md](themes/README.md).

## Setup

```sh
git clone https://github.com/ttcat/ccstay && cd ccstay
./install.sh
python3 -m unittest discover -s tests
pipx run ruff check .
```

Tests drive a real tmux with a fake claude, so you need tmux but no account.

## Pull requests

- Keep Python 3.9 compatibility
- Add a test that fails without your change
- Pass arguments as lists; never build a shell string from a title or a path without `shlex.quote`
- Update `CHANGELOG.md` and both READMEs when behaviour changes
- A new theme: everything in the checklist at the end of `themes/README.md`

## Reporting bugs

Include the output of `ccstay doctor`. Check it first for Claude Code internals that have changed.
