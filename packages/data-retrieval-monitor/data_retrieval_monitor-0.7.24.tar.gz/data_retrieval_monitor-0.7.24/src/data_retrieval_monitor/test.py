# test.py — feeder for the app (posts to /feed).
# Sends exact statuses: waiting, retrying, running, failed, overdue, manual, succeeded
# Includes meta: ingested_at (UTC ISO) and env (from --env).
# Also mixes:
#   - empty chunks for some stage/dataset
#   - log paths that may not exist
#   - http logs
#
# Example:
#   python test.py --base http://127.0.0.1:8080 --env dev --owners QSG DG --modes live backfill

import argparse
import random
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

# ---------- Easy-to-tweak defaults ----------
DEFAULT_BASE   = "http://127.0.0.1:8080"
OWNERS_DEFAULT = ["QSG", "DG"]
MODES_DEFAULT  = ["live", "backfill"]
N_DATASETS     = 40
SLEEP_SEC      = 3
ENV_DEFAULT    = "dev"

STAGES   = ["archive", "stage", "enrich", "consolidate"]
STATUSES = ["waiting", "retrying", "running", "failed", "overdue", "manual", "succeeded"]

random.seed(11)

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def maybe_empty_chunks(i, stg):
    # Produce empty chunk list occasionally
    return ((i + len(stg)) % 17) == 0

def choose_pool(version, i, stage):
    if version == 0:
        pref = {
            "stage":        ["running", "waiting", "retrying", "manual"],
            "archive":      ["waiting", "running", "manual"],
            "enrich":       ["waiting", "running", "retrying"],
            "consolidate":  ["waiting", "manual"],
        }.get(stage, ["waiting", "running"])
        if i % 10 == 0: pref.append("overdue")
        if i % 16 == 0: pref.append("failed")
    else:
        pref = {
            "stage":        ["succeeded", "running", "manual"],
            "archive":      ["running", "succeeded"],
            "enrich":       ["running", "succeeded", "retrying"],
            "consolidate":  ["succeeded", "running"],
        }.get(stage, ["succeeded", "running"])
        if i % 7 == 0:  pref.append("overdue")
        if i % 11 == 0: pref.append("failed")
    return pref

def build_log_paths(owner, mode, dn, stage, cid, i):
    """
    Return a tuple of:
      - maybe-existing filesystem path under /tmp/drm-logs (or not)
      - sometimes an http URL
    We'll mostly provide filesystem paths so raw mode can copy them.
    """
    # Most: local path that *might* exist
    fs_path = f"/tmp/drm-logs/workspaces/{owner}/{mode}/{dn}/{stage}/{cid}.log"
    # Occasionally, give a non-existent or external URL:
    if i % 13 == 0 and stage == "enrich":
        return None, f"https://logs.example/{owner}/{mode}/{dn}/{stage}/{cid}.log"
    return fs_path, None

def chunks_for(version, i, owner, mode, dn, stage):
    if maybe_empty_chunks(i, stage):
        return []
    n = 1 + ((i + len(stage)) % 4)  # 1..4
    pool = choose_pool(version, i, stage)
    items = []
    for idx in range(n):
        st  = random.choice(pool)
        cid = f"c{idx}"
        fs, http_url = build_log_paths(owner, mode, dn, stage, cid, i)
        log_value = http_url if http_url else fs
        items.append({
            "id": cid,
            "status": st,
            "proc": f"https://proc.example/{owner}/{mode}/{dn}/{stage}/{cid}",
            "log":  log_value
        })
    return items

def build_feed(version, owners, modes, n):
    items = []
    for i in range(n):
        dn     = f"dataset-{i:03d}"
        owner  = owners[i % len(owners)]
        mode   = modes[i % len(modes)]
        for stg in STAGES:
            items.append({
                "owner": owner,
                "mode": mode,
                "data_name": dn,
                "stage": stg,
                "chunks": chunks_for(version, i, owner, mode, dn, stg)
            })
    return items

def push(base, items, env):
    payload = {
        "snapshot": items,
        "meta": {
            "ingested_at": utc_now_iso(),
            "env": env
        }
    }
    url = f"{base.rstrip('/')}/feed"
    r = requests.post(url, json=payload, timeout=30)
    if r.status_code >= 400:
        url2 = f"{base.rstrip('/')}/ingest_snapshot"
        r = requests.post(url2, json=payload, timeout=30)
    r.raise_for_status()
    print(f"pushed {len(items)} stage entries → {r.json()}")

def reset(base):
    try:
        r = requests.post(f"{base.rstrip('/')}/store/reset", timeout=10)
        print("reset:", r.status_code, r.text)
    except Exception as e:
        print("reset failed (continuing):", e)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE, help="App base URL")
    ap.add_argument("--owners", nargs="*", default=OWNERS_DEFAULT, help="Owner list")
    ap.add_argument("--modes",  nargs="*", default=MODES_DEFAULT,  help="Mode list")
    ap.add_argument("--n", type=int, default=N_DATASETS, help="Number of datasets")
    ap.add_argument("--sleep", type=float, default=SLEEP_SEC, help="Seconds between pushes")
    ap.add_argument("--env", default=ENV_DEFAULT, help="Environment label to send (e.g. dev, staging, prod)")
    args = ap.parse_args()

    print(f"Base: {args.base}")
    print(f"Owners: {args.owners}")
    print(f"Modes: {args.modes}")
    print(f"Datasets: {args.n}")
    print(f"Env: {args.env}")
    print(f"Interval: {args.sleep}s\n")

    reset(args.base)

    ver = 0
    while True:
        items = build_feed(ver, args.owners, args.modes, args.n)
        push(args.base, items, args.env)
        ver ^= 1
        time.sleep(args.sleep)

if __name__ == "__main__":
    main()