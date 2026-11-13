"""End-to-end tests: a real tmux on a private socket, a fake claude, no terminal."""
import argparse
import contextlib
import glob
import io
import json
import os
import plistlib
import pty
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ccstay  # noqa: E402
CCSTAY = os.path.join(HERE, "..", "ccstay.py")


THEMES = os.path.join(HERE, "..", "themes")


def page_data(page):
    """The JSON the page embeds; what every theme renders from."""
    return json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', page, re.S).group(1))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ccstay")
        self.project = f"{self.tmp}/project"
        os.makedirs(self.project)
        self.socket = f"ccstay-test-{os.getpid()}"
        self.env = dict(os.environ, CCSTAY_SOCKET=self.socket, CCSTAY_CLAUDE=f"{HERE}/fake_claude.py",
                        CCSTAY_TERMINAL="none", CCSTAY_SUSPECT_SECONDS="0", CCSTAY_NATIVE="0", CCSTAY_SCHEDULED="1", CLAUDE_CONFIG_DIR=f"{self.tmp}/claude",
                        XDG_STATE_HOME=f"{self.tmp}/state", XDG_CONFIG_HOME=f"{self.tmp}/config")
        self.env.pop("TMUX", None)
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.addCleanup(self.tmux, "kill-server")

    def run_cc(self, *args, **env):
        r = subprocess.run([sys.executable, CCSTAY, *args], capture_output=True, text=True,
                           env={**self.env, **env}, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        return r.stdout

    def tmux(self, *args):
        return subprocess.run(["tmux", "-L", self.socket, *args], capture_output=True, text=True, env=self.env)

    def registered(self):
        d = f"{self.tmp}/claude/sessions"
        out = []
        for name in [n for n in os.listdir(d) if n.endswith(".json")] if os.path.isdir(d) else []:
            with open(f"{d}/{name}") as f:
                out.append(json.load(f))
        return out

    def wait(self, fn):
        for _ in range(100):
            if fn():
                return
            time.sleep(0.1)
        self.fail("timed out")

    def snapshot(self):
        with open(f"{self.tmp}/state/ccstay/sessions.json") as f:
            return json.load(f)


class Lifecycle(Base):
    def test_new_lists_with_url(self):
        out = self.run_cc("new", self.project, "demo")
        self.assertIn("project/demo", out)
        self.assertIn("https://claude.ai/code/session_", out)
        self.assertIn("idle", self.run_cc("ls"))

    def test_sleep_asks_before_using_a_conversation_from_a_moved_folder(self):
        self.run_cc("new", self.project)
        sid = self.registered()[0]["sessionId"]
        old = f"{self.tmp}/claude/projects/-old-place"
        os.makedirs(old)
        shutil.move(glob.glob(f"{self.tmp}/claude/projects/*/{sid}.jsonl")[0], f"{old}/{sid}.jsonl")
        r = subprocess.run([sys.executable, CCSTAY, "sleep", "project"], capture_output=True, text=True, env=self.env,
                           stdin=subprocess.DEVNULL)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("-old-place", r.stdout)
        self.assertIn("add -y", r.stderr)
        self.assertEqual(len(self.registered()), 1)
        self.run_cc("sleep", "project", "-y")
        self.assertIn("asleep", self.run_cc("ls"))
        self.run_cc("wake", "project")
        self.wait(self.registered)
        self.assertEqual(self.registered()[0]["sessionId"], sid)

    def test_sleep_still_refuses_a_session_with_no_conversation_anywhere(self):
        self.run_cc("new", self.project, FAKE_EMPTY="1")
        r = subprocess.run([sys.executable, CCSTAY, "sleep", "project", "-y"], capture_output=True, text=True, env=self.env)
        self.assertIn("no conversation to resume yet", r.stderr)

    def test_a_closed_session_whose_folder_moved_is_not_gone(self):
        self.run_cc("new", self.project)
        sid = self.registered()[0]["sessionId"]
        self.run_cc("close", "project")
        old = f"{self.tmp}/claude/projects/-old-place"
        os.makedirs(old)
        shutil.move(glob.glob(f"{self.tmp}/claude/projects/*/{sid}.jsonl")[0], f"{old}/{sid}.jsonl")
        self.assertIn("closed", self.run_cc("closed"))

    def test_sleep_frees_claude_and_wake_resumes_same_conversation(self):
        self.run_cc("new", self.project)
        sid = self.registered()[0]["sessionId"]
        self.run_cc("sleep", "project")
        self.assertEqual(self.registered(), [])
        self.assertIn("asleep", self.run_cc("ls"))
        self.wait(lambda: "asleep, press Enter" in self.tmux("capture-pane", "-p", "-t", "=project:").stdout)
        self.assertIn(f"fake claude {sid}", self.tmux("capture-pane", "-p", "-t", "=project:").stdout)
        self.run_cc("wake", "project")
        self.wait(self.registered)
        self.assertEqual(self.registered()[0]["sessionId"], sid)

    def test_a_slow_exit_still_sleeps_and_keeps_the_tab(self):
        self.run_cc("new", self.project, FAKE_SLOW_EXIT="1")
        self.run_cc("sleep", "project", CCSTAY_STOP_SECONDS="0.5")
        self.wait(lambda: "asleep, press Enter" in self.tmux("capture-pane", "-p", "-t", "=project:").stdout)
        self.assertEqual(self.registered(), [])

    def test_enter_in_the_tab_wakes_too(self):
        self.run_cc("new", self.project)
        sid = self.registered()[0]["sessionId"]
        self.run_cc("sleep", "project")
        self.wait(lambda: "asleep, press Enter" in self.tmux("capture-pane", "-p", "-t", "=project:").stdout)
        self.tmux("send-keys", "-t", "=project:", "Enter")
        self.wait(self.registered)
        self.assertEqual(self.registered()[0]["sessionId"], sid)

    def test_refuses_to_sleep_a_working_session(self):
        self.run_cc("new", self.project)
        path = f"{self.tmp}/claude/sessions/{self.registered()[0]['pid']}.json"
        with open(path) as f:
            m = json.load(f)
        m["status"] = "busy"
        with open(path, "w") as f:
            json.dump(m, f)
        r = subprocess.run([sys.executable, CCSTAY, "sleep", "project"], capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(self.registered()), 1)

    def test_refuses_to_sleep_before_the_first_message(self):
        self.run_cc("new", self.project, FAKE_EMPTY="1")
        r = subprocess.run([sys.executable, CCSTAY, "sleep", "project"], capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 1)
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0.00001")
        self.assertEqual(len(self.registered()), 1)

    def test_tick_sleeps_idle_sessions_except_kept(self):
        self.run_cc("new", self.project, "a")
        self.run_cc("new", self.project, "b")
        self.run_cc("keep", "project/b")
        time.sleep(0.2)
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0.00001")
        self.assertEqual(len(self.registered()), 1)
        self.assertEqual(sum("asleep" in r for r in self.run_cc("ls").splitlines()), 1)

    def test_session_survives_detached_client_gone(self):
        self.run_cc("new", self.project)
        self.assertEqual(self.tmux("list-clients").stdout, "")
        self.assertEqual(len(self.registered()), 1)


class Scrolling(Base):
    def test_config_loads_and_a_key_leaves_scrollback(self):
        self.run_cc("new", self.project)
        conf = f"{self.tmp}/state/ccstay/tmux.conf"
        self.assertEqual(self.tmux("source-file", conf).stderr, "")
        self.tmux("copy-mode", "-eH", "-t", "=project:")

        def mode():
            return self.tmux("display-message", "-p", "-t", "=project:", "#{pane_in_mode}").stdout.strip()

        self.assertEqual(mode(), "1")
        pid, master = pty.fork()  # keys only reach the copy-mode table from a real client
        if pid == 0:
            os.execvpe("tmux", ["tmux", "-L", self.socket, "attach", "-t", "=project"], {**self.env, "TERM": "xterm"})
        self.addCleanup(os.close, master)
        self.addCleanup(os.waitpid, pid, 0)
        self.addCleanup(self.tmux, "detach-client", "-s", "=project")
        self.wait(lambda: self.tmux("list-clients").stdout)
        os.write(master, b"\x1b[<66;5;5M\x1b[<35;5;5M")  # sideways scroll and pointer motion stay in scrollback
        time.sleep(0.3)
        self.assertEqual(mode(), "1")
        os.write(master, b"a")
        self.wait(lambda: mode() == "0")

    def test_resize_drops_only_a_short_history(self):
        self.run_cc("new", self.project)
        for name, lines, kept in (("short", 1, False), ("long", 60, True)):
            self.tmux("new-session", "-d", "-s", name, "-x", "100", "-y", "24",
                      f"seq 1 {lines}; printf '%0100d\\n' 0; sleep 30")

            def size(session=name):
                return int(self.tmux("display", "-p", "-t", f"={session}:", "#{history_size}").stdout)

            self.wait(lambda: self.tmux("capture-pane", "-p", "-t", f"={name}:").stdout.strip())
            self.tmux("resize-window", "-t", f"={name}:", "-x", "50")
            self.wait(lambda keep=kept: (size() > 20) == keep and (keep or size() == 0))


class Reboot(Base):
    def reboot(self):
        for m in self.registered():
            os.kill(m["pid"], signal.SIGTERM)
        self.tmux("kill-server")
        self.wait(lambda: not self.registered())
        time.sleep(1.1)  # a server is identified by its start time, in seconds

    def two_sessions(self):
        self.run_cc("new", self.project, "awake")
        self.run_cc("new", self.project, "dozing")
        self.run_cc("sleep", "project/dozing")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        return set(self.snapshot())

    def test_restore_brings_back_each_in_its_state(self):
        ids = self.two_sessions()
        self.reboot()
        self.assertIn("2 session(s) waiting", self.run_cc("ls"))
        self.run_cc("restore")
        self.wait(self.registered)
        self.assertEqual(len(self.registered()), 1)
        self.assertEqual(set(self.snapshot()), ids)
        listing = self.run_cc("ls")
        self.assertIn("asleep", listing)
        self.assertIn("idle", listing)

    def test_first_session_after_reboot_keeps_the_rest(self):
        ids = self.two_sessions()
        self.reboot()
        self.run_cc("new", self.project, "fresh")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.assertTrue(ids < set(self.snapshot()))
        self.assertIn("restored 2", self.run_cc("restore"))

    def test_restore_starts_the_most_recent_last(self):
        for name in ("a", "b", "c"):
            self.run_cc("new", self.project, name)
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        sids = {e["name"]: sid for sid, e in self.snapshot().items()}
        self.reboot()
        for age, name in ((100, "project/a"), (300, "project/b"), (200, "project/c")):
            log = glob.glob(f"{self.tmp}/claude/projects/*/{sids[name]}.jsonl")[0]
            os.utime(log, (time.time() - age,) * 2)
        self.run_cc("restore")
        started = sorted(self.registered(), key=lambda m: m["updatedAt"])
        self.assertEqual([m["sessionId"] for m in started], [sids["project/b"], sids["project/c"], sids["project/a"]])

    def test_restore_twice_does_not_duplicate(self):
        self.two_sessions()
        self.reboot()
        self.run_cc("restore")
        self.wait(self.registered)
        self.assertIn("nothing to restore", self.run_cc("restore"))

    def test_exited_session_is_closed_and_can_be_reopened(self):
        self.run_cc("new", self.project, "keepme")
        self.run_cc("new", self.project, "gone")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        sid = next(e["sid"] for e in self.snapshot().values() if e["name"] == "project/gone")
        self.tmux("kill-session", "-t", "=project/gone")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.assertEqual(self.snapshot()[sid]["state"], "closed")
        self.assertIn("closed", self.run_cc("closed", "gone"))
        self.assertIn("nothing to restore", self.run_cc("restore"))
        self.run_cc("reopen", sid[:8])
        self.wait(lambda: sum(m["sessionId"] == sid for m in self.registered()) == 1)
        self.assertEqual(self.snapshot()[sid]["state"], "open")

    def test_close_command_needs_no_second_look(self):
        self.run_cc("new", self.project)
        self.run_cc("close", "project")
        states = [e["state"] for e in self.snapshot().values()]
        self.assertEqual(states, ["closed"])
        self.assertEqual(self.registered(), [])

    def test_deleted_conversation_is_gone(self):
        self.run_cc("new", self.project)
        self.run_cc("close", "project")
        shutil.rmtree(f"{self.tmp}/claude/projects")
        self.assertIn("gone", self.run_cc("closed"))

    def test_last_session_exiting_is_forgotten(self):
        self.run_cc("new", self.project)
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.tmux("kill-session", "-t", "=project")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.assertEqual([e["state"] for e in self.snapshot().values()], ["closed"])
        self.assertIn("no sessions", self.run_cc("ls"))

    def test_missing_folder_is_reported(self):
        self.run_cc("new", self.project)
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.reboot()
        shutil.rmtree(self.project)
        self.assertIn("folder is gone", self.run_cc("restore"))


class Hooks(Base):
    def hook(self, sid, reason):
        subprocess.run([sys.executable, CCSTAY, "hook"], env=self.env, check=True, timeout=5, text=True,
                       input=json.dumps({"session_id": sid, "reason": reason}))

    def test_exit_closes_at_once_but_other_reasons_wait(self):
        self.run_cc("new", self.project, "a")
        self.run_cc("new", self.project, "b")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.env["CCSTAY_SUSPECT_SECONDS"] = "60"
        ids = {e["name"]: e["sid"] for e in self.snapshot().values()}
        self.tmux("kill-session", "-t", "=project/a")
        self.tmux("kill-session", "-t", "=project/b")
        self.hook(ids["project/a"], "prompt_input_exit")
        self.hook(ids["project/b"], "other")
        self.wait(lambda: self.snapshot()[ids["project/a"]]["state"] == "closed")
        self.assertEqual(self.snapshot()[ids["project/b"]]["state"], "suspect")

    def test_hooks_on_is_idempotent_and_off_leaves_others_alone(self):
        path = f"{self.tmp}/claude/settings.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        mine = {"hooks": [{"type": "command", "command": "other"}]}
        with open(path, "w") as f:
            json.dump({"theme": "dark", "hooks": {"SessionEnd": [mine]}}, f)
        self.run_cc("hooks", "on")
        self.run_cc("hooks", "on")
        with open(path) as f:
            on = json.load(f)
        self.assertEqual(len(on["hooks"]["SessionEnd"]), 2)
        self.assertEqual(len(on["hooks"]["SessionStart"]), 1)
        self.run_cc("hooks", "off")
        with open(path) as f:
            self.assertEqual(json.load(f), {"theme": "dark", "hooks": {"SessionEnd": [mine]}})


class Robustness(Base):
    def test_a_theme_cannot_reach_the_network(self):
        t = f"{self.tmp}/leaky"
        shutil.copytree(os.path.join(THEMES, "bento"), t)
        with open(f"{t}/theme.js", encoding="utf-8") as f:
            good = f.read()
        for bad in ("fetch('/x')", "new WebSocket('x')", "navigator.sendBeacon('x')", "eval('x')", "location.href='x'",
                    "'<img src=x>'", "a('//evil.example/x')", "document.createElement('script')"):
            with open(f"{t}/theme.js", "w", encoding="utf-8") as f:
                f.write(good + bad)
            self.assertTrue(ccstay.theme_problems(t), bad)

    def test_slash_command_is_ours_to_add_and_remove(self):
        path = f"{self.tmp}/commands/ccstay.md"
        with mock.patch.object(ccstay, "CLAUDE_DIR", self.tmp):
            ccstay.slash_command(True)
            self.assertIn("ccstay $ARGUMENTS", open(path).read())
            ccstay.slash_command(False)
            self.assertFalse(os.path.exists(path))
            with open(path, "w") as f:
                f.write("mine")
            ccstay.slash_command(True)
            ccstay.slash_command(False)
            self.assertEqual(open(path).read(), "mine")

    def test_popup_raises_the_tab_of_a_session(self):
        s = dict(name="a", tty="/dev/ttys001", herdr="", sid="x")
        with mock.patch.object(ccstay.sys, "platform", "darwin"), mock.patch.object(ccstay, "sessions", return_value=[s]), \
                mock.patch.object(ccstay, "raise_tab", return_value=True) as tab, mock.patch("subprocess.Popen"), \
                contextlib.redirect_stdout(io.StringIO()):
            ccstay.cmd_popup(argparse.Namespace(session="a", terminal=None))
        tab.assert_called_once_with("/dev/ttys001")

    def test_popup_opens_a_tab_for_a_session_with_no_window(self):
        s = dict(name="a", tty="", herdr="", sid="x")
        empty = subprocess.CompletedProcess("", 0, "", "")
        with mock.patch.object(ccstay.sys, "platform", "darwin"), mock.patch.object(ccstay, "sessions", return_value=[s]), \
                mock.patch.object(ccstay, "tmux", return_value=empty), mock.patch.object(ccstay, "open_tab") as tab, \
                mock.patch.object(ccstay, "pick_terminal", return_value="iterm"), mock.patch("subprocess.Popen"), \
                contextlib.redirect_stdout(io.StringIO()):
            ccstay.cmd_popup(argparse.Namespace(session="a", terminal=None))
        tab.assert_called_once()

    def test_raise_scripts_render(self):
        for script in (ccstay.RAISE_ITERM, ccstay.RAISE_TERMINAL):
            self.assertIn('"/dev/x"', script.format(tty="/dev/x"))

    def test_terminal_scripts_render_completely(self):
        for script in (ccstay.ITERM, ccstay.ITERM_SHELL, ccstay.GHOSTTY, ccstay.APPLE_TERMINAL):
            self.assertNotIn("{", script.format(c="x", new="false"))

    def test_hook_survives_bad_input(self):
        for stdin in ("not json", ""):
            r = subprocess.run([sys.executable, CCSTAY, "hook"], input=stdin, capture_output=True, text=True, env=self.env)
            self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_hook_survives_an_unusable_state_folder(self):
        env = {**self.env, "XDG_STATE_HOME": "/etc/hosts"}
        r = subprocess.run([sys.executable, CCSTAY, "hook"], input="{}", capture_output=True, text=True, env=env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_torn_event_line_does_not_stop_the_check(self):
        self.run_cc("ls")
        with open(f"{self.tmp}/state/ccstay/events.jsonl", "w") as f:
            f.write("{broken\n")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.assertEqual([x for x in os.listdir(f"{self.tmp}/state/ccstay") if x.startswith("events")], [])

    def test_tab_in_a_title_does_not_break_listing(self):
        self.run_cc("new", self.project)
        self.run_cc("sleep", "project")
        self.tmux("set-option", "-t", "=project:", "@title", "two\twords")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.assertEqual(next(iter(self.snapshot().values()))["title"], "two words")

    def test_private_state(self):
        self.run_cc("new", self.project)
        self.run_cc("sleep", "project")
        root = f"{self.tmp}/state/ccstay"
        os.chmod(f"{root}/sessions.json", 0o644)  # written by an older version
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        self.assertEqual(os.stat(root).st_mode & 0o777, 0o700)
        self.assertEqual(os.stat(f"{root}/sessions.json").st_mode & 0o777, 0o600)
        name = os.listdir(f"{root}/screens")[0]
        self.assertEqual(os.stat(f"{root}/screens/{name}").st_mode & 0o777, 0o600)

    def test_a_reused_pid_is_not_claude(self):
        table = {7: (1, "ttys1", "vim notes.txt")}
        self.assertFalse(ccstay.is_claude(7, table))
        self.assertFalse(ccstay.is_claude(8, table))


class MacOnly(Base):
    def compile(self, script):
        path = f"{self.tmp}/script.scpt"
        with tempfile.NamedTemporaryFile("w", suffix=".applescript", dir=self.tmp, delete=False) as f:
            f.write(script)
        return subprocess.run(["osacompile", "-o", path, f.name], capture_output=True, text=True)

    @unittest.skipUnless(os.path.isdir("/Applications/iTerm.app") and os.path.isdir("/Applications/Ghostty.app"),
                         "needs the terminals' scripting dictionaries")
    def test_scripts_compile_with_awkward_text(self):
        text = ccstay.quoted("""it's a "dir" \\ 中文""")
        scripts = [t.format(c=text, new="true") for t in (ccstay.ITERM, ccstay.ITERM_SHELL)]
        scripts += [ccstay.layout_script(app) for app in ("iTerm", "Ghostty")]
        for script in scripts:
            r = self.compile(script)
            self.assertEqual(r.returncode, 0, r.stderr)

    @unittest.skipUnless(sys.platform == "darwin", "macOS only")
    def test_timer_carries_settings_and_a_valid_plist(self):
        home = f"{self.tmp}/home"
        calls = []
        args = argparse.Namespace(state="on")
        with mock.patch.object(ccstay, "HOME", home), mock.patch.object(ccstay, "tmux_base", return_value=["tmux"]), \
                mock.patch.object(ccstay, "STATE_DIR", self.tmp), mock.patch.object(ccstay, "LAYOUT_ZSH", f"{self.tmp}/l"), \
                mock.patch.dict(os.environ, {"CCSTAY_IDLE_HOURS": "1"}), \
                mock.patch.object(ccstay.subprocess, "run", side_effect=lambda *a, **k: calls.append(a) or mock.Mock(returncode=0)):
            ccstay.cmd_timer(args)
        path = f"{home}/Library/LaunchAgents/{ccstay.TIMER_ID}.plist"
        with open(path) as f:
            self.assertIn("CCSTAY_IDLE_HOURS=1", f.read())
        self.assertEqual(subprocess.run(["plutil", "-lint", path], capture_output=True).returncode, 0)
        self.assertEqual(subprocess.run(["zsh", "-n", f"{self.tmp}/l"], capture_output=True).returncode, 0)


class TabFailure(Base):
    def test_a_session_starts_detached_when_no_tab_opens(self):
        with mock.patch.dict(os.environ, self.env), mock.patch.object(ccstay, "SOCKET", self.socket), \
                mock.patch.object(ccstay, "STATE_DIR", f"{self.tmp}/state/ccstay"), \
                mock.patch.object(ccstay, "TMUX_CONF", f"{self.tmp}/state/ccstay/tmux.conf"), \
                mock.patch.object(ccstay, "open_tab", side_effect=SystemExit(1)), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            self.assertIsNone(ccstay.start("project", self.project, [f"{HERE}/fake_claude.py"], "iterm"))
        self.assertIn("detached", out.getvalue())
        self.wait(self.registered)


class Native2(unittest.TestCase):
    def test_reopen_records_the_new_tab(self):
        e = dict(sid="a", title="t", cwd="/x", asleep=False, native=True)
        with mock.patch.object(ccstay, "start_native", return_value="/dev/ttys099"), \
                mock.patch.object(ccstay, "iterm_id", return_value="new"), mock.patch.object(ccstay, "boot_id", return_value="b"), \
                mock.patch.object(ccstay, "claude_exe", return_value="claude"):
            fields = ccstay.reopen(e, None)
        self.assertEqual((fields["tty"], fields["terminal"]), ("/dev/ttys099", "new"))

    def test_a_hold_is_not_claude_even_with_a_stale_session_file(self):
        command = "/bin/sh -c x ccstay-hold /x/screens/ab.txt t /y/claude -r ab"
        self.assertFalse(ccstay.is_claude(7, {7: (1, "ttys1", command)}))


class Setup(Base):
    def test_hooks_off_creates_nothing(self):
        self.run_cc("hooks", "off")
        self.assertFalse(os.path.exists(f"{self.tmp}/claude/settings.json"))

    def test_hooks_on_makes_the_folder(self):
        self.run_cc("hooks", "on")
        self.assertTrue(os.path.exists(f"{self.tmp}/claude/settings.json"))

    def test_doctor_uses_the_claude_sessions_run(self):
        self.assertIn("claude: 2.0.0", self.run_cc("doctor"))

    def test_timer_state_without_systemd(self):
        with mock.patch.object(ccstay.sys, "platform", "linux"), \
                mock.patch.object(ccstay.subprocess, "run", side_effect=FileNotFoundError):
            self.assertFalse(ccstay.timer_active())

    def settings(self):
        path = f"{self.tmp}/claude/settings.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def test_hooks_keep_a_symlink_mode_and_a_backup(self):
        path, real = self.settings(), f"{self.tmp}/dotfiles.json"
        with open(real, "w") as f:
            json.dump({"theme": "dark"}, f)
        os.chmod(real, 0o600)
        os.symlink(real, path)
        self.run_cc("hooks", "on")
        self.assertTrue(os.path.islink(path))
        self.assertEqual(os.stat(real).st_mode & 0o777, 0o600)
        with open(f"{real}.ccstay-backup") as f:
            self.assertEqual(json.load(f), {"theme": "dark"})

    def test_hooks_off_finds_an_old_path_and_leaves_no_empty_block(self):
        path = self.settings()
        hook = {"hooks": [{"type": "command", "command": "/old/place/ccstay hook"}]}
        with open(path, "w") as f:
            json.dump({"hooks": {"SessionEnd": [hook]}}, f)
        self.run_cc("hooks", "off")
        with open(path) as f:
            self.assertEqual(json.load(f), {})

    def test_uninstall_purge_refuses_while_sessions_run(self):
        self.run_cc("new", self.project)
        r = subprocess.run([sys.executable, CCSTAY, "uninstall", "--purge"], capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("still running", r.stderr)

    def test_doctor_reports_session_files(self):
        self.run_cc("new", self.project)
        self.assertIn("ok   session files", self.run_cc("doctor"))

    def test_doctor_fails_when_the_format_changes(self):
        self.run_cc("new", self.project)
        pid = self.registered()[0]["pid"]
        with open(f"{self.tmp}/claude/sessions/{pid}.json", "w") as f:
            json.dump({"pid": pid}, f)
        r = subprocess.run([sys.executable, CCSTAY, "doctor"], capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL session files", r.stdout)

    def test_remote_control_is_left_to_claude_unless_asked(self):
        self.assertNotIn("--remote-control", self.run_cc("new", self.project, "-n"))
        self.assertIn("--remote-control", self.run_cc("new", self.project, "-n", CCSTAY_REMOTE="1"))

    def test_rc_at_startup_gets_the_session_name(self):
        os.makedirs(f"{self.tmp}/claude", exist_ok=True)
        with open(f"{self.tmp}/claude/settings.json", "w") as f:
            json.dump({"remoteControlAtStartup": True}, f)
        self.assertIn("--remote-control", self.run_cc("new", self.project, "-n"))


class Reload(Base):
    def test_plan_then_restart_outdated_in_place(self):
        self.run_cc("new", self.project)
        before = self.registered()[0]
        out = self.run_cc("reload", FAKE_VERSION="2.0.1")
        self.assertIn("1 session(s) would restart", out)
        self.assertEqual(self.registered()[0]["pid"], before["pid"])
        self.run_cc("reload", "-y", FAKE_VERSION="2.0.1")
        self.wait(lambda: self.registered() and self.registered()[0]["pid"] != before["pid"])
        self.assertEqual(self.registered()[0]["sessionId"], before["sessionId"])

    def test_up_to_date_is_skipped(self):
        self.run_cc("new", self.project)
        self.assertIn("0 session(s) would restart", self.run_cc("reload"))


    def test_a_session_waiting_for_an_answer_is_left_alone(self):
        self.run_cc("new", self.project, FAKE_STATUS="waiting")
        self.assertIn("0 session(s) would restart", self.run_cc("reload", FAKE_VERSION="2.0.1"))


class Herdr(unittest.TestCase):
    """Sessions in herdr terminals, with herdr itself faked."""
    HOLDER = "/x/Herdr Core.app/Contents/MacOS/herdr-core hold --socket s"

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ccstay")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        os.makedirs(f"{self.tmp}/sessions")
        with open(f"{self.tmp}/sessions/30.json", "w") as f:
            json.dump(dict(pid=30, sessionId="abc", cwd="/w", status="idle", name="work"), f)
        self.table = {10: (1, "??", self.HOLDER), 20: (10, "ttys1", "-zsh"), 30: (20, "ttys1", "claude"),
                      40: (1, "??", "claude")}  # 40: a claude elsewhere, not in herdr

    def found(self, table):
        def fake(*args):
            return {"terminals": [{"address": "t5", "state": "live"}]} if args[0] == "ls" else {"pid": 20}
        with mock.patch.object(ccstay, "CLAUDE_DIR", self.tmp), mock.patch.object(ccstay, "hc_json", side_effect=fake), \
                mock.patch.object(ccstay, "same_process", return_value=True), mock.patch.dict(os.environ, {"CCSTAY_NATIVE": ""}), \
                mock.patch.object(ccstay, "read_snapshot", return_value={"def": {"title": "nap"}}):
            return ccstay.herdr_sessions([], table)

    def test_a_session_in_a_herdr_terminal_is_found_with_its_address(self):
        (s,) = self.found(self.table)
        self.assertEqual((s["sid"], s["herdr"], s["tty"], s["asleep"]), ("abc", "t5", "", False))

    def test_a_sleeping_session_in_herdr_is_found(self):
        table = {**self.table, 30: (20, "ttys1", "/bin/sh -c x ccstay-hold /s/screens/def.txt nap claude -r def")}
        (s,) = self.found(table)
        self.assertEqual((s["sid"], s["herdr"], s["title"], s["asleep"]), ("def", "t5", "nap", True))

    def test_herdr_is_not_asked_when_nothing_runs_in_it(self):
        with mock.patch.object(ccstay, "CLAUDE_DIR", self.tmp), mock.patch.object(ccstay, "hc_json") as asked, \
                mock.patch.dict(os.environ, {"CCSTAY_NATIVE": ""}):
            self.assertEqual(ccstay.herdr_sessions([], {40: (1, "??", "claude")}), [])
        asked.assert_not_called()

    def test_sleep_types_the_resume_into_the_herdr_shell(self):
        s = dict(name="work", pid=30, sid="abc", cwd="/w", tty="", herdr="t5")
        with mock.patch.object(ccstay, "parent_is_shell", return_value=True), mock.patch.object(ccstay, "stop", return_value=True), \
                mock.patch.object(ccstay, "hc", return_value=subprocess.CompletedProcess("hc", 0)) as hc, \
                mock.patch.object(ccstay, "process_table", return_value={}), mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": "/acct"}):
            self.assertTrue(ccstay.swap(s, ["claude", "-r", "abc"]))
        verb, address, line = hc.call_args.args
        self.assertEqual((verb, address), ("send", "t5"))
        self.assertIn("CLAUDE_CONFIG_DIR=/acct claude -r abc", line)

    def test_a_herdr_terminal_with_no_shell_is_left_alone(self):
        s = dict(name="work", pid=30, sid="abc", cwd="/w", tty="", herdr="t5")
        with mock.patch.object(ccstay, "parent_is_shell", return_value=False), mock.patch.object(ccstay, "stop") as stop, \
                mock.patch.object(ccstay, "process_table", return_value={}), mock.patch.object(ccstay, "log"):
            self.assertFalse(ccstay.swap(s, ["claude"]))
        stop.assert_not_called()

    def test_inside_herdr_new_sessions_open_in_herdr(self):
        with mock.patch.dict(os.environ, {"CCSTAY_TERMINAL": "", "HC_TERMINAL_ID": "t2", "TERM_PROGRAM": "ghostty"}), \
                mock.patch.object(ccstay, "TERMINAL_FILE", f"{self.tmp}/terminal"):
            self.assertEqual(ccstay.pick_terminal(None), "herdr")
        with mock.patch.dict(os.environ, {"CCSTAY_TERMINAL": "", "HC_TERMINAL_ID": "t2", "TERM_PROGRAM": "Apple_Terminal"}), \
                mock.patch.object(ccstay, "TERMINAL_FILE", f"{self.tmp}/terminal"):
            self.assertEqual(ccstay.pick_terminal(None), "terminal")  # a marker inherited from somewhere else

    def test_herdr_mode_is_kept_until_set_back_to_auto(self):
        path = f"{self.tmp}/terminal"
        env = {"CCSTAY_TERMINAL": "", "HC_TERMINAL_ID": "", "TERM_PROGRAM": "iTerm.app"}
        with mock.patch.object(ccstay, "TERMINAL_FILE", path), mock.patch.dict(os.environ, env), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            ccstay.cmd_terminal(argparse.Namespace(choice="herdr"))
            self.assertEqual(ccstay.pick_terminal(None), "herdr")  # from a phone or a tmux session too
            ccstay.cmd_terminal(argparse.Namespace(choice="auto"))
            self.assertEqual(ccstay.pick_terminal(None), "iterm")
            ccstay.cmd_terminal(argparse.Namespace(choice="auto"))  # already auto
        self.assertIn("new sessions open in herdr", out.getvalue())

    def test_a_herdr_session_is_recorded_against_herdr_and_reopens_there(self):
        s = dict(sid="abc", name="work", title="work", cwd="/w", asleep=False, tty="", herdr="t5")
        self.assertEqual(ccstay.record(s, "b", "tmux", "iterm", "herdr")["terminal"], "herdr")
        with mock.patch.object(ccstay, "start_herdr", return_value="t9") as start, \
                mock.patch.object(ccstay, "herdr_id", return_value="h2"), mock.patch.object(ccstay, "boot_id", return_value="b"), \
                mock.patch.object(ccstay, "claude_exe", return_value="claude"):
            fields = ccstay.reopen(ccstay.record(s, "b", "tmux", "iterm", "herdr"), None)
        self.assertEqual((fields["herdr"], fields["terminal"]), ("t9", "h2"))
        self.assertEqual(start.call_args.args[1][-2:], ["-r", "abc"])


class Native(unittest.TestCase):
    def test_only_processes_under_iterm_count(self):
        table = {1: (0, "??", "launchd"), 5: (1, "??", "/Applications/iTerm.app/Contents/MacOS/iTerm2"),
                 6: (5, "ttys1", "-zsh"), 7: (6, "ttys1", "claude"), 8: (1, "ttys2", "claude")}
        self.assertTrue(ccstay.in_iterm(7, table))
        self.assertFalse(ccstay.in_iterm(8, table))

    def test_a_missing_session_is_judged_after_the_fact(self):
        e = {"boot": "b", "terminal": "t", "state": "open"}
        self.assertEqual(ccstay.next_state(e, "b", "t", 100), "suspect")
        e.update(state="suspect", missing_since=100)
        self.assertEqual(ccstay.next_state(e, "b", "t", 110), "suspect")
        self.assertEqual(ccstay.next_state(e, "b", "t", 130), "closed")
        self.assertEqual(ccstay.next_state(e, "b2", "t", 130), "interrupted")  # rebooted
        self.assertEqual(ccstay.next_state(e, "b", "", 130), "interrupted")  # iTerm quit

    def test_tmux_client_is_not_a_held_session(self):
        hold = "ccstay-hold /x/screens/ab12.txt t claude -r ab12"
        table = {5: (1, "??", "/Applications/iTerm.app/Contents/MacOS/iTerm2"),
                 6: (5, "ttys1", f"tmux -L ccstay new-session -A /bin/sh -c f {hold}"),
                 7: (5, "ttys2", f"/bin/sh -c f {hold}")}
        with mock.patch.object(ccstay, "read_snapshot", return_value={}), \
                mock.patch.object(ccstay.sys, "platform", "darwin"), mock.patch.dict(os.environ, {"CCSTAY_NATIVE": "1"}):
            self.assertEqual([s["pid"] for s in ccstay.native_sessions([], table)], [7])

    def test_hold_is_one_line_so_it_can_be_typed(self):
        self.assertNotIn("\n", ccstay.HOLD)


    def test_start_time_reads_the_same_in_any_locale(self):
        with mock.patch.dict(os.environ, {"LC_ALL": "zh_TW.UTF-8", "LANG": "zh_TW.UTF-8", "TZ": "Asia/Taipei"}):
            self.assertRegex(ccstay.started(os.getpid()), r"^[A-Z][a-z]{2} [A-Z][a-z]{2} +\d+ [\d:]{8} \d{4}$")

    def test_a_reused_pid_with_another_start_time_is_not_the_session(self):
        self.assertTrue(ccstay.same_process(os.getpid(), {"procStart": ccstay.started(os.getpid())}))
        self.assertFalse(ccstay.same_process(os.getpid(), {"procStart": "Mon Jan  1 00:00:00 2001"}))
        self.assertTrue(ccstay.same_process(os.getpid(), {}))  # an older claude did not write it

    @unittest.skipUnless(shutil.which("zsh"), "needs zsh")
    def test_a_typed_line_survives_zsh_with_a_leading_equals(self):
        line = ccstay.shell_line("/", ["printf", "%s|", "=notes", "a b", "it's"])
        out = subprocess.run(["zsh", "-fc", line], capture_output=True, text=True)
        self.assertEqual(out.stdout, "=notes|a b|it's|", out.stderr)

    def test_project_folder_is_named_like_claude_names_it(self):
        with mock.patch.object(ccstay, "CLAUDE_DIR", "/c"), mock.patch("os.path.realpath", side_effect=lambda p: p):
            self.assertEqual(ccstay.transcript("/Users/x/\U0001F680app", "s"), "/c/projects/-Users-x---app/s.jsonl")
            self.assertEqual(ccstay.transcript("/a/b.c", "s"), "/c/projects/-a-b-c/s.jsonl")

    def test_a_long_folder_finds_the_shortened_name(self):
        root = tempfile.mkdtemp(prefix="ccstay")
        self.addCleanup(shutil.rmtree, root, True)
        cwd = "/" + "x" * 240
        folder = f"{root}/projects/-{'x' * 199}-1a2b3c"
        os.makedirs(folder)
        open(f"{folder}/s.jsonl", "w").close()
        with mock.patch.object(ccstay, "CLAUDE_DIR", root), mock.patch("os.path.realpath", side_effect=lambda p: p):
            self.assertEqual(ccstay.transcript(cwd, "s"), f"{folder}/s.jsonl")
            self.assertEqual(ccstay.transcript(cwd, "other"), "")

    def test_a_gone_session_is_not_searched_for_again(self):
        saved = {"s": dict(sid="s", cwd="/nowhere", state="gone", asleep=False, native=False)}
        with mock.patch.object(ccstay, "current_ids", return_value=("b", "t", "i", "")), \
                mock.patch.object(ccstay, "locked", contextlib.nullcontext), mock.patch.object(ccstay, "read_snapshot", return_value=saved), \
                mock.patch.object(ccstay, "take_events", return_value=[]), mock.patch.object(ccstay, "write_atomic"), \
                mock.patch.object(ccstay, "moved_transcript", return_value="") as search, mock.patch("glob.glob", return_value=[]):
            ccstay.reconcile([])
        search.assert_not_called()


class Tools(Base):
    def test_folders_page_links_sessions(self):
        project = tempfile.mkdtemp(prefix="ccstay", dir=os.path.dirname(HERE))  # the page leaves out /tmp
        self.addCleanup(shutil.rmtree, project, True)
        self.run_cc("new", project)
        with open(self.run_cc("folders").strip()) as f:
            page = f.read()
        self.assertTrue(page.startswith("<title>Sessions</title>"))
        data = page_data(page)
        session = data["folders"][0]["sessions"][0]
        self.assertTrue(session["url"].startswith("https://claude.ai/code/session_"))
        self.assertEqual(session["state"], "idle")
        self.assertEqual([t["id"] for t in data["themes"]], ["bento", "mates"])  # default first, then the rest
        self.assertIn('<script data-theme="bento">', page)
        self.assertIn('<script data-theme="mates">', page)

    def test_page_auto_republishes_when_the_sessions_change(self):
        projects = [tempfile.mkdtemp(prefix="ccstay", dir=os.path.dirname(HERE)) for _ in range(2)]  # the page leaves out /tmp
        for p in projects:
            self.addCleanup(shutil.rmtree, p, True)

        def helper(*args):
            return subprocess.run(["tmux", "-L", f"{self.socket}-page", *args], capture_output=True, text=True, env=self.env)

        self.addCleanup(helper, "kill-server")
        self.run_cc("page", "on")
        self.assertEqual(helper("has-session", "-t", "=page").returncode, 0)
        self.run_cc("new", projects[0])

        def sent():
            self.run_cc("tick", CCSTAY_PAGE_SECONDS="0")
            return helper("capture-pane", "-p", "-t", "=page:").stdout.count("publish")

        self.assertEqual(sent(), 1)
        with open(f"{self.tmp}/state/ccstay/folders.html") as f:
            rows = [s for g in page_data(f.read())["folders"] for s in g["sessions"]]
        self.assertEqual(len(rows), 1)  # the helper itself is not on the page
        self.assertEqual(sent(), 1)  # nothing changed, nothing sent
        self.run_cc("new", projects[1])
        self.assertEqual(sent(), 2)
        self.run_cc("page", "off")
        self.assertNotEqual(helper("has-session", "-t", "=page").returncode, 0)

    def test_folders_page_keeps_a_title_inside_the_data(self):
        row = dict(key="s1", ts=1000.0, title="</script><script>alert(1)</script>", url="https://claude.ai/code/session_x",
                   cwd=f"{ccstay.HOME}/p", root=f"{ccstay.HOME}/p", state="idle")
        page = ccstay.folders_page([row], [], 1000.0)
        self.assertNotIn("</script><script>alert", page)
        self.assertEqual(page_data(page)["folders"][0]["sessions"][0]["title"], row["title"])

    def test_folders_page_picks_the_default_theme(self):
        with open(self.run_cc("folders", "--theme", "mates").strip()) as f:
            self.assertEqual([t["id"] for t in page_data(f.read())["themes"]], ["mates", "bento"])
        r = subprocess.run([sys.executable, CCSTAY, "folders", "--theme", "nope"], capture_output=True, text=True, env=self.env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("nope", r.stderr)

    def test_broken_personal_theme_is_left_out_by_name(self):
        bad = f"{self.tmp}/config/ccstay/themes/broken"
        os.makedirs(bad)
        for name in ("theme.css", "theme.js"):
            with open(f"{bad}/{name}", "w") as f:
                f.write("x")
        r = subprocess.run([sys.executable, CCSTAY, "folders"], capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("theme broken", r.stderr)
        self.assertIn("missing theme.json", r.stderr)
        with open(r.stdout.strip()) as f:
            self.assertEqual([t["id"] for t in page_data(f.read())["themes"]], ["bento", "mates"])
        self.assertNotIn("broken", self.run_cc("themes"))

    def test_themes_lists_the_shipped_ones(self):
        out = self.run_cc("themes")
        self.assertIn("bento", out)
        self.assertIn("Desk Mates / 桌友", out)

    def test_no_command_shows_next_steps(self):
        self.assertIn("ccstay setup", self.run_cc())

    def test_setup_asks_then_turns_everything_on(self):
        with mock.patch.object(ccstay, "cmd_timer") as timer, mock.patch.object(ccstay, "cmd_hooks") as hooks, \
                mock.patch.object(ccstay, "cmd_doctor") as doctor, mock.patch("sys.stdin") as stdin, \
                mock.patch("builtins.input", side_effect=["n", "", "", "", "n"]), mock.patch.object(ccstay, "ask_terminal"), \
                mock.patch.object(ccstay, "cmd_autorestore") as auto, mock.patch.object(ccstay.sys, "platform", "darwin"):
            stdin.isatty.return_value = True
            ccstay.cmd_setup(argparse.Namespace(yes=False))
            timer.assert_not_called()
            ccstay.cmd_setup(argparse.Namespace(yes=False))
            timer.assert_called_once()
            hooks.assert_called_once()
            doctor.assert_called_once()
            self.assertEqual(auto.call_args.args[0].state, "on")  # Enter takes the default
            ccstay.cmd_setup(argparse.Namespace(yes=False))
            self.assertEqual(auto.call_args.args[0].state, "off")

    def test_autorestore_waits_for_the_next_login(self):
        with mock.patch.object(ccstay, "HOME", self.tmp), mock.patch.object(ccstay.sys, "platform", "darwin"), \
                mock.patch("subprocess.run") as run:
            ccstay.cmd_autorestore(argparse.Namespace(state="on"))
            path = f"{self.tmp}/Library/LaunchAgents/{ccstay.RESTORE_ID}.plist"
            with open(path) as f:
                plist = plistlib.loads(f.read().encode())
            self.assertTrue(plist["RunAtLoad"])
            self.assertTrue(plist["ProgramArguments"][2].endswith("restore --tabs; :"))
            self.assertNotIn("bootstrap", str(run.call_args_list))  # loading it now would open tabs at once
            ccstay.cmd_autorestore(argparse.Namespace(state="off"))
            self.assertFalse(os.path.exists(path))

    def test_setup_cancelled_at_the_prompt_changes_nothing(self):
        for quit_with in (EOFError, KeyboardInterrupt):
            with mock.patch.object(ccstay, "cmd_timer") as timer, mock.patch.object(ccstay, "cmd_hooks") as hooks, \
                    mock.patch("sys.stdin") as stdin, mock.patch("builtins.input", side_effect=quit_with):
                stdin.isatty.return_value = True
                ccstay.cmd_setup(argparse.Namespace(yes=False))
                timer.assert_not_called()
                hooks.assert_not_called()

    def test_folders_page_offers_closed_sessions(self):
        project = tempfile.mkdtemp(prefix="ccstay", dir=os.path.dirname(HERE))
        self.addCleanup(shutil.rmtree, project, True)
        self.run_cc("new", project, "kept")
        self.run_cc("close", "kept")
        with open(self.run_cc("folders").strip()) as f:
            closed = page_data(f.read())["closed"]
        self.assertEqual(len(closed), 1)
        self.assertTrue(closed[0]["cmd"].startswith("ccstay reopen "))
        self.run_cc(*closed[0]["cmd"].split()[1:])
        self.assertIn("kept", self.run_cc("ls"))

    def test_folders_page_wakes_asleep_sessions(self):
        project = tempfile.mkdtemp(prefix="ccstay", dir=os.path.dirname(HERE))
        self.addCleanup(shutil.rmtree, project, True)
        self.run_cc("new", project, "nap")
        self.run_cc("sleep", "nap")
        self.run_cc("tick", CCSTAY_IDLE_HOURS="0")
        with open(self.run_cc("folders").strip()) as f:
            asleep = [s for g in page_data(f.read())["folders"] for s in g["sessions"] if s["state"] == "asleep"]
        self.assertEqual(len(asleep), 1)
        self.assertTrue(asleep[0]["cmd"].startswith("ccstay wake "))
        self.assertIn("awake", self.run_cc(*asleep[0]["cmd"].split()[1:]))
        self.assertNotIn("asleep", self.run_cc("ls"))

    def test_last_worked_prefers_the_conversation_time(self):
        with tempfile.NamedTemporaryFile() as f, mock.patch.object(ccstay, "transcript", return_value=f.name):
            os.utime(f.name, (1000, 1000))
            self.assertEqual(ccstay.last_worked({"cwd": "/x", "sid": "a", "ended_at": 2000}), 1000)
        with mock.patch.object(ccstay, "transcript", return_value="/nonexistent"):
            self.assertEqual(ccstay.last_worked({"cwd": "/x", "sid": "a", "ended_at": 2000}), 2000)

    def test_setup_remembers_the_terminal(self):
        path = f"{self.tmp}/terminal"
        with mock.patch.object(ccstay, "TERMINAL_FILE", path), mock.patch("os.path.exists", return_value=True), \
                mock.patch("builtins.input", return_value="g"), mock.patch.dict(os.environ, {"CCSTAY_TERMINAL": ""}):
            ccstay.ask_terminal()
            self.assertEqual(ccstay.pick_terminal(None), "ghostty")
            self.assertEqual(ccstay.pick_terminal("iterm"), "iterm")

    def test_apple_terminal_is_recognised(self):
        with mock.patch.dict(os.environ, {"CCSTAY_TERMINAL": "", "TERM_PROGRAM": "Apple_Terminal"}), \
                mock.patch.object(ccstay, "TERMINAL_FILE", f"{self.tmp}/terminal"):
            self.assertEqual(ccstay.pick_terminal(None), "terminal")

    def test_warp_is_not_mistaken_for_apple_terminal(self):
        with mock.patch.dict(os.environ, {"CCSTAY_TERMINAL": "", "TERM_PROGRAM": "WarpTerminal"}), \
                mock.patch.object(ccstay, "TERMINAL_FILE", f"{self.tmp}/terminal"), mock.patch.object(ccstay.sys, "platform", "linux"):
            self.assertIsNone(ccstay.pick_terminal(None))

    def test_memory_pressure_comes_from_the_kernel_not_the_swap_share(self):
        with mock.patch.object(ccstay.sys, "platform", "darwin"), \
                mock.patch("subprocess.run", return_value=subprocess.CompletedProcess("", 0, "2\n", "")):
            self.assertEqual(ccstay.pressure(.5), "high")
        with mock.patch.object(ccstay.sys, "platform", "linux"):
            self.assertEqual(ccstay.pressure(.5), "ok")

    def test_apple_terminal_commands_survive_the_login_shell(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess("", 0)) as run:
            ccstay.open_tab("terminal", ["tmux", "attach-session", "-t", "=a/b"])
        script = run.call_args.kwargs["input"]
        self.assertIn("exec /bin/sh -c", script)
        self.assertIn("exec tmux attach-session -t =a/b", script)

    def test_doctor_failure_invites_a_fix(self):
        out = io.StringIO()
        with mock.patch("shutil.which", return_value=None), mock.patch.dict(os.environ, {"CCSTAY_CLAUDE": ""}), \
                mock.patch.object(ccstay, "timer_active", return_value=False), contextlib.redirect_stdout(out), \
                self.assertRaises(SystemExit):
            ccstay.cmd_doctor(argparse.Namespace())
        self.assertIn(ccstay.FIX_IT, out.getvalue())

    def test_a_crash_invites_a_fix_but_a_scheduled_run_stays_quiet(self):
        def boom(a):
            raise ValueError("boom")
        for cmd, caught in (("ls", SystemExit), ("tick", ValueError)):
            err = io.StringIO()
            with mock.patch.object(ccstay, "parser") as parser, contextlib.redirect_stderr(err), self.assertRaises(caught):
                parser.return_value.parse_args.return_value = argparse.Namespace(cmd=cmd, fn=boom)
                ccstay.main()
            self.assertEqual(ccstay.FIX_IT in err.getvalue(), cmd == "ls")

    def test_folders_page_lists_every_closed_session(self):
        rows = [dict(sid=f"{i:08d}", state="closed", cwd="/x", title="t") for i in range(40)]
        with mock.patch.object(ccstay, "reconcile", return_value={r["sid"]: r for r in rows}), \
                mock.patch.object(ccstay, "sessions", return_value=[]):
            self.assertEqual(len(ccstay.closed_rows(0)), 40)

    def test_folders_remembers_the_theme(self):
        def default():
            with open(self.run_cc("folders").strip()) as f:
                return page_data(f.read())["default"]
        self.assertEqual(default(), "bento")
        self.run_cc("folders", "--theme", "mates")
        self.assertEqual(default(), "mates")
        with open(f"{self.tmp}/state/ccstay/theme", "w") as f:
            f.write("removed-later\n")
        self.assertEqual(default(), "bento")

    def test_mem_reports_totals_and_sessions(self):
        self.run_cc("new", self.project)
        out = self.run_cc("mem")
        for heading in ("RAM", "Swap", "TERMINALS", "Claude Code", "iTerm", "Ghostty", "tmux", "Total", "SESSIONS", "1 awake", "OTHER APPS", "SLEEP FIRST"):
            self.assertIn(heading, out)

    def test_sleep_first_ranks_idle_big_sessions_and_skips_busy_and_kept(self):
        rows = [dict(name=n, pid=p, status=st, sid=sid, meta={}, cwd="/x") for n, p, st, sid in
                (("small", 1, "idle", "a"), ("big", 2, "idle", "b"), ("busy", 3, "busy", "c"), ("kept", 4, "idle", "d"))]
        with mock.patch.object(ccstay, "keep_ids", return_value={"d"}), mock.patch.object(ccstay, "own_session", return_value=""), \
                mock.patch.object(ccstay, "idle_seconds", return_value=7200), mock.patch.object(ccstay, "has_conversation", return_value=True):
            self.assertEqual([s["name"] for s in ccstay.sleep_first(rows, {1: 100, 2: 900, 3: 2000, 4: 3000})], ["big", "small"])

    def test_mem_sorts_the_terminal_stack(self):
        self.assertEqual(ccstay.stack_of("/Applications/iTerm.app/Contents/MacOS/iTerm2"), "iTerm")
        self.assertEqual(ccstay.stack_of("/Users/x/Library/Application Support/iTerm2/iTermServer-3.7.1 a"), "iTerm")
        self.assertEqual(ccstay.stack_of("/Applications/Ghostty.app/Contents/MacOS/ghostty"), "Ghostty")
        self.assertEqual(ccstay.stack_of("/opt/homebrew/bin/tmux -L ccstay"), "tmux")
        self.assertEqual(ccstay.stack_of("claude --remote-control"), "Claude Code")
        self.assertEqual(ccstay.stack_of("/usr/bin/python3 claude.py"), "")

    def test_board_runs_without_history(self):
        self.assertIn("FOLDER", self.run_cc("board"))

    def test_name_is_tmux_safe(self):
        d = f"{self.tmp}/my.app"
        os.makedirs(d)
        self.assertIn("my-app", self.run_cc("new", d))


class Themes(unittest.TestCase):
    """Every theme in themes/ meets the file contract in themes/README.md, so CI catches a bad pull request."""

    def test_every_shipped_theme_meets_the_contract(self):
        names = sorted(n for n in os.listdir(THEMES) if os.path.isdir(os.path.join(THEMES, n)))
        self.assertIn("bento", names)
        self.assertIn("mates", names)
        for name in names:
            with self.subTest(theme=name):
                self.assertEqual(ccstay.theme_problems(os.path.join(THEMES, name)), [])

    def test_themes_render_the_shared_hooks(self):
        for name in ("bento", "mates"):
            with open(os.path.join(THEMES, name, "theme.js")) as f:
                js = f.read()
            with self.subTest(theme=name):
                for hook in ('data-st="', "data-grp", "data-closed", "data-empty", "data-copy=", 'target="_blank" rel="noopener"',
                             "c.switcher", "c.chips", "c.summary", "c.generated", "c.assign("):
                    self.assertIn(hook, js)

    def test_problems_are_named(self):
        d = tempfile.mkdtemp(prefix="ccstay-theme")
        self.addCleanup(shutil.rmtree, d, True)
        bad = os.path.join(d, "Bad_Name")
        os.makedirs(bad)
        self.assertIn("folder name must be lowercase letters, digits and dashes", ccstay.theme_problems(bad)[0])
        t = os.path.join(d, "ok")
        os.makedirs(t)
        with open(f"{t}/theme.json", "w") as f:
            json.dump({"name": {"en": "Ok"}, "author": "me"}, f)
        with open(f"{t}/theme.css", "w") as f:
            f.write("@import url(https://evil.example/x.css);")
        with open(f"{t}/theme.js", "w") as f:
            f.write("ccstayTheme({render: function () { return '</script>'; }});")
        problems = ccstay.theme_problems(t)
        self.assertTrue(any('"zh"' in p for p in problems))
        self.assertTrue(any("evil.example" in p for p in problems))
        self.assertTrue(any("</script" in p for p in problems))
        self.assertEqual(ccstay.theme_problems(os.path.join(THEMES, "bento")), [])


class AccountFolder(unittest.TestCase):
    def test_sessions_get_the_config_folder_the_command_was_run_with(self):
        with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": "/x/backup"}):
            self.assertEqual(ccstay.account_env(["claude"]), ["-e", "CLAUDE_CONFIG_DIR=/x/backup", "claude"])
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(ccstay.account_env(["claude"]), ["/usr/bin/env", "-u", "CLAUDE_CONFIG_DIR", "claude"])


if __name__ == "__main__":
    unittest.main()
