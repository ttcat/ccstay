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
check "setup, answering at the prompt" '(sleep 3; printf "y\n"; sleep 10) | script -q /dev/null ccstay setup; launchctl print gui/$(id -u)/dev.ccstay.tick >/dev/null && grep -q ccstay ~/.claude/settings.json'
check "doctor with real claude" 'ccstay doctor | tee /tmp/doctor.txt; grep -q "timer: on" /tmp/doctor.txt && grep -q "hooks: on" /tmp/doctor.txt'
check "plist points at an existing ccstay" 'grep -c ccstay ~/Library/LaunchAgents/dev.ccstay.tick.plist && launchctl print gui/$(id -u)/dev.ccstay.tick | grep -E "state|last exit"'

# From here a stand-in plays Claude, which cannot log in on this machine.
export CCSTAY_CLAUDE="$repo/tests/fake_claude.py" CLAUDE_CONFIG_DIR="$HOME/.claude" CCSTAY_TERMINAL=none CCSTAY_SUSPECT_SECONDS=0
mkdir -p ~/work/shop

check "new session" 'ccstay new ~/work/shop demo | tee /tmp/new.txt && grep -q shop/demo /tmp/new.txt && grep -q https://claude.ai/code/session_ /tmp/new.txt'
check "ls shows it idle" 'ccstay ls | tee /dev/stderr | grep -q idle'
check "sleep" 'ccstay sleep shop && ccstay ls | tee /dev/stderr | grep -q asleep'
check "wake" 'ccstay wake shop && sleep 2 && ccstay ls | tee /dev/stderr | grep -q idle'
check "timer ran by itself, twice, without errors" 'for i in $(seq 1 30); do s=$(launchctl print gui/$(id -u)/dev.ccstay.tick); r=$(echo "$s" | awk "/runs =/{print \$3}"); [ "${r:-0}" -ge 2 ] && { echo "$s" | grep -E "runs =|last exit"; echo "$s" | grep -q "last exit code = 0"; exit; }; sleep 5; done; echo "$s" | grep -E "state|runs =|last exit"; exit 1'
check "hooks noticed nothing broke, timer log clean" 'test ! -s ~/.local/state/ccstay/ccstay.log || tail -20 ~/.local/state/ccstay/ccstay.log; ! grep -qi traceback ~/.local/state/ccstay/*.log 2>/dev/null'
check "a crash, then restore" 'tmux -L ccstay kill-server; sleep 1; ccstay ls | tee /dev/stderr | grep -q "waiting for"; ccstay restore -n; ccstay restore; sleep 2; ccstay ls | tee /dev/stderr | grep -q idle'
check "folders page, both themes" 'ccstay folders -o /tmp/a.html && ccstay folders --theme mates -o /tmp/b.html && test -s /tmp/a.html && test -s /tmp/b.html'
check "close, closed, reopen" 'ccstay close shop && ccstay closed | tee /dev/stderr | grep -q shop && ccstay reopen shop && sleep 2 && ccstay ls | tee /dev/stderr | grep -q idle && ccstay close shop'
check "uninstall leaves nothing" 'ccstay uninstall --purge && ! test -e ~/Library/LaunchAgents/dev.ccstay.tick.plist && ! test -e ~/.local/state/ccstay && ! grep -s ccstay ~/.claude/settings.json'
[ "$how" = brew ] && check "brew uninstall" 'brew uninstall --cask ccstay && ! command -v ccstay'

echo; echo "$fails failed"
exit $((fails > 0))
