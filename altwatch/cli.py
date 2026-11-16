"""Command line: python -m altwatch check | status"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

from . import core


def _read_watch(path: str) -> core.Watch:
    try:
        with open(path, encoding="utf-8") as f:
            return core.load_watch(json.load(f))
    except FileNotFoundError:
        raise core.WatchError(f"No watch file at {path}. Copy watch.example.json and edit it.") from None
    except json.JSONDecodeError as e:
        raise core.WatchError(f"{path} isn't valid JSON: {e}") from None


def cmd_check(a: argparse.Namespace) -> int:
    watch = _read_watch(a.watch)
    if a.base:
        watch.base = a.base.rstrip("/")
    state = core.load_state(a.state)
    today = date.fromisoformat(a.today) if a.today else date.today()
    run = core.check(watch, state, today)
    message = core.compose(run)
    core.save_state(a.state, state)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "altwatch.log"), "a", encoding="utf-8") as f:
        f.write(f"{run.day} requests={run.requests} message={'yes' if message else 'no'}\n")
        f.writelines(f"  {line}\n" for line in run.log)
    if message:
        with open(os.path.join(a.out, f"message-{run.day}.txt"), "w", encoding="utf-8") as f:
            f.write(message + "\n")
        print(message)
    elif a.verbose:
        print(f"Nothing new on {run.day}. No message. ({run.requests} requests)")
    if a.verbose:
        for line in run.log:
            print("  " + line, file=sys.stderr)
    return 0


def cmd_status(a: argparse.Namespace) -> int:
    state = core.load_state(a.state)
    if not state["tools"] and not state["feeds"]:
        print("Nothing watched yet. Run 'check' first.")
        return 0
    for slug, t in sorted(state["tools"].items()):
        if t.get("missing"):
            print(f"{t['name']}: no RepoQuarry page")
        else:
            print(f"{t['name']}: {len(t['seen'])} alternatives known, watching since {t['since']}")
    for url, f in state["feeds"].items():
        print(f"{url}: {len(f['seen'])} posts seen, watching since {f['since']}")
    runs = state.get("runs") or []
    said = sum(1 for r in runs if r["message"])
    print(f"{len(runs)} runs recorded, {said} with a message, {len(runs) - said} silent.")
    return 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(prog="altwatch", description="One message when a new open-source "
                                "alternative to a tool you pay for appears. Silent otherwise.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="run today's check")
    c.add_argument("--watch", default="watch.json")
    c.add_argument("--state", default="altwatch-state.json")
    c.add_argument("--out", default="altwatch-out")
    c.add_argument("--base", help="read RepoQuarry pages from another address (for testing)")
    c.add_argument("--today", help="pretend today is YYYY-MM-DD (for testing)")
    c.add_argument("--verbose", action="store_true", help="say so when there is nothing new")
    c.set_defaults(fn=cmd_check)
    s = sub.add_parser("status", help="show what is watched")
    s.add_argument("--state", default="altwatch-state.json")
    s.set_defaults(fn=cmd_status)
    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except core.WatchError as e:
        print(f"Altwatch: {e}", file=sys.stderr)
        return 2
