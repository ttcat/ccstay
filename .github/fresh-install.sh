#!/bin/bash
# Walk the README on a clean Mac: install, set up, then use a session from start to finish.
how=$1
repo=$PWD
fails=0
check() { # label, command
  echo; echo "=== $1"
  if bash -c "$2" 2>&1; then echo "PASS $1"; else echo "FAIL $1"; fails=$((fails + 1)); fi
}
export PATH="$HOME/.local/bin:$PATH"

check "no ccstay, tmux or claude before install" '! command -v ccstay && ! command -v tmux && ! command -v claude && ! test -e ~/.claude'
if [ "$how" = brew ]; then
  check "brew install" 'brew install ttcat/tap/ccstay'
else
  check "install.sh" 'brew install tmux && ./install.sh'
fi
check "real Claude Code installs" 'curl -fsSL https://claude.ai/install.sh | bash && claude --version'
check "version and tmux" 'ccstay --version && tmux -V'
check "themes found" 'ccstay themes | grep -q bento && ccstay themes | grep -q mates'
check "setup, answering at the prompt" 'printf "y\n" | script -q /dev/null ccstay setup'
check "doctor with real claude" 'ccstay doctor'
check "plist points at an existing ccstay" 'grep -c ccstay ~/Library/LaunchAgents/dev.ccstay.tick.plist && launchctl print gui/$(id -u)/dev.ccstay.tick | grep -E "state|last exit"'

# From here a stand-in plays Claude, which cannot log in on this machine.
export CCSTAY_CLAUDE="$repo/tests/fake_claude.py" CLAUDE_CONFIG_DIR="$HOME/.claude" CCSTAY_TERMINAL=none CCSTAY_SUSPECT_SECONDS=0
mkdir -p ~/work/shop

check "new session" 'ccstay new ~/work/shop demo | tee /tmp/new.txt && grep -q shop/demo /tmp/new.txt && grep -q https://claude.ai/code/session_ /tmp/new.txt'
check "ls shows it idle" 'ccstay ls | tee /dev/stderr | grep -q idle'
check "sleep" 'ccstay sleep shop && ccstay ls | tee /dev/stderr | grep -q asleep'
check "wake" 'ccstay wake shop && sleep 2 && ccstay ls | tee /dev/stderr | grep -q idle'
check "timer ran by itself" 'for i in $(seq 1 24); do grep -q . ~/.local/state/ccstay/sessions.json 2>/dev/null && [ ~/.local/state/ccstay/sessions.json -nt ~/work/shop ] && { launchctl print gui/$(id -u)/dev.ccstay.tick | grep -E "runs|last exit"; exit 0; }; sleep 5; done; exit 1'
check "a crash, then restore" 'tmux -L ccstay kill-server; sleep 1; ccstay ls | tee /dev/stderr | grep -q "waiting for"; ccstay restore -n; ccstay restore; sleep 2; ccstay ls | tee /dev/stderr | grep -q idle'
check "folders page, both themes" 'ccstay folders -o /tmp/a.html && ccstay folders --theme mates -o /tmp/b.html && test -s /tmp/a.html && test -s /tmp/b.html'
check "close, closed, reopen" 'ccstay close shop && ccstay closed | tee /dev/stderr | grep -q shop && ccstay reopen shop && sleep 2 && ccstay ls | tee /dev/stderr | grep -q idle && ccstay close shop'
check "uninstall leaves nothing" 'ccstay uninstall --purge && ! test -e ~/Library/LaunchAgents/dev.ccstay.tick.plist && ! test -e ~/.local/state/ccstay && ! grep -s ccstay ~/.claude/settings.json'
[ "$how" = brew ] && check "brew uninstall" 'brew uninstall --cask ccstay && ! command -v ccstay'

echo; echo "$fails failed"
exit $((fails > 0))
