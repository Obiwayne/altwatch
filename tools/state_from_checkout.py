"""Build an Altwatch state file from a RepoQuarry checkout, as the catalogue
stood at whatever commit is checked out. Used to test Altwatch against the
live site: start from last week's catalogue, then run today's check.

    python tools/state_from_checkout.py <path to data/> --tools notion,zapier --date 2026-11-09 > state.json

Reads `first_seen`-agnostic: it lists every project file whose `alternatives`
name the tool. No PyYAML needed.
"""
import argparse
import glob
import json
import os
import re
import sys

p = argparse.ArgumentParser()
p.add_argument("data")
p.add_argument("--tools", required=True, help="comma-separated product ids, e.g. notion,zapier")
p.add_argument("--date", required=True)
a = p.parse_args()

tools = [t.strip() for t in a.tools.split(",") if t.strip()]
state = {"version": 1, "tools": {t: {"name": t, "since": a.date, "seen": {}, "fails": 0} for t in tools},
         "feeds": {}, "runs": []}
for path in sorted(glob.glob(os.path.join(a.data, "projects", "*.yaml"))):
    text = open(path, encoding="utf-8").read()
    pid = os.path.basename(path)[:-5]
    for prod in re.findall(r"^\s*- product:\s*([a-z0-9._-]+)", text, re.M):
        if prod in state["tools"]:
            state["tools"][prod]["seen"][pid] = a.date
json.dump(state, sys.stdout, indent=1)
