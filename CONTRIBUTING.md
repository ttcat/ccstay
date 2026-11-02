# Contributing

ccstay stays small on purpose: one Python file, standard library only, no daemon. The folders page has themes in `themes/`; to add one, read [themes/README.md](themes/README.md).

Pull requests written with Claude or another AI are welcome. [CLAUDE.md](CLAUDE.md) tells it how to work here. You are the author, so read the change before you send it.

## Setup

```sh
git clone https://github.com/ttcat/ccstay && cd ccstay
./install.sh
python3 -m unittest discover -s tests
pipx run ruff check .
```

Tests drive a real tmux with a fake claude, so you need tmux but no account.

## Pull requests

- One problem per pull request
- Keep Python 3.9 compatibility
- Add a test that fails without your change
- Pass arguments as lists; never build a shell string from a title or a path without `shlex.quote`
- Update `CHANGELOG.md` and both READMEs when behaviour changes
- A new theme: everything in the checklist at the end of `themes/README.md`
- Leave out session titles, private paths and conversation text

## Reporting bugs

Include the output of `ccstay doctor`. Check it first for Claude Code internals that have changed, and remove anything private.
