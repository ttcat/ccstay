#!/usr/bin/env python3
"""Stands in for claude: registers itself the way the real one does and waits."""
import json
import os
import re
import signal
import sys
import time
import uuid

VERSION = os.environ.get("FAKE_VERSION", "2.0.0")
args = sys.argv[1:]
if args == ["--version"]:
    print(f"{VERSION} (Claude Code)")
    sys.exit()
if args == ["update"] or args[:1] == ["agents"]:
    print("[]")
    sys.exit()
root = os.environ["CLAUDE_CONFIG_DIR"]
if os.path.exists(f"{root}/ask-trust"):  # the folder trust prompt, which comes before claude registers
    import termios
    import tty
    tty.setcbreak(sys.stdin.fileno(), termios.TCSANOW)
    choice = 0
    while True:
        print("\033[2J\033[H" + ("❯ No, exit\n  Yes, I trust this folder" if choice == 0 else "  No, exit\n❯ Yes, I trust this folder"), flush=True)
        key = os.read(sys.stdin.fileno(), 8)
        if key == b"\033[B":
            choice = 1
        elif key in (b"\r", b"\n"):
            if choice == 0:
                sys.exit()
            break
sid = args[args.index("-r") + 1] if "-r" in args else str(uuid.uuid4())
path = f"{root}/sessions/{os.getpid()}.json"
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path + ".tmp", "w") as f:
    json.dump(dict(pid=os.getpid(), sessionId=sid, cwd=os.getcwd(), status=os.environ.get("FAKE_STATUS", "idle"),
                   name="fake", nameSource="derived", version=VERSION, kind="interactive",
                   bridgeSessionId="session_" + sid[:8], updatedAt=int(time.time() * 1000)), f)


os.replace(path + ".tmp", path)  # the real one never shows a half-written file


def bye(*_):
    os.remove(path)
    sys.exit()


signal.signal(signal.SIGTERM, signal.SIG_IGN if os.environ.get("FAKE_SLOW_EXIT") else bye)
signal.signal(signal.SIGHUP, bye)
log = f"{root}/projects/{re.sub('[^A-Za-z0-9]', '-', os.getcwd())}/{sid}.jsonl"
if not os.environ.get("FAKE_EMPTY"):
    os.makedirs(os.path.dirname(log), exist_ok=True)
    open(log, "a").close()
print(f"fake claude {sid}", flush=True)
while True:
    time.sleep(60)
