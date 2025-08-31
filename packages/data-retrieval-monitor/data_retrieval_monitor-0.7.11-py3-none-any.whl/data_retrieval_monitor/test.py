# test.py
# Feeder for the app (posts to /feed). Statuses are exact:
# waiting, retrying, running, failed, overdue, manual, succeeded
# It also WRITES .log files under LOG_ROOT (default /tmp/drm-logs) on the server
# and sets "log" to a RELATIVE path so the app can serve it via /logs/<rel>.

import argparse
import random
import time
import requests
import os
from pathlib import Path

# ---------- Easy-to-tweak defaults ----------
DEFAULT_BASE   = "http://127.0.0.1:8080"
OWNERS_DEFAULT = ["QSG", "team-b"]     # change here (and/or via --owners ...)
MODES_DEFAULT  = ["live", "backfill"]
N_DATASETS     = 60
SLEEP_SEC      = 3
LOG_ROOT       = os.getenv("LOG_ROOT", "./drm-logs")  # must match the app

STAGES   = ["stage", "archive", "enrich", "consolidate"]
STATUSES = ["waiting", "retrying", "running", "failed", "overdue", "manual", "succeeded"]

random.seed(11)

def write_log(rel_path: str, content: str):
    """
    Write a text log under LOG_ROOT at rel_path (no leading slash).
    Returns the relative path passed in (for app's /logs/<rel>).
    """
    rel = rel_path.lstrip("/").replace("\\", "/")
    base = Path(LOG_ROOT).resolve()
    path = (base / rel).resolve()
    if not str(path).startswith(str(base)):
        # avoid path traversal
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(content, encoding="utf-8")
    except Exception as e:
        print("log write failed:", e)
        return None
    return rel

def chunks_for_version(version, i, owner, mode, dn, stage):
    """
    Build a chunk list for (dataset i, stage) that changes with version.
    Ensures we hit the full status set and includes proc/log links.
    """
    # different number of chunks by dataset/stage to visualize variety
    n = 1 + ((i + len(stage)) % 4)  # 1..4
    items = []

    if version == 0:
        # Earlier pipeline emphasis per stage
        stage_pref = {
            "stage":        ["running", "waiting", "retrying", "manual"],
            "archive":      ["waiting", "running", "manual"],
            "enrich":       ["waiting", "running", "retrying"],
            "consolidate":  ["waiting", "manual"],
        }.get(stage, ["waiting", "running"])
        # add occasional negatives
        if i % 10 == 0: stage_pref.append("overdue")
        if i % 16 == 0: stage_pref.append("failed")
        pool = stage_pref
    else:
        # Later pipeline: more succeeded, but keep a spread
        stage_pref = {
            "stage":        ["succeeded", "running", "manual"],
            "archive":      ["running", "succeeded"],
            "enrich":       ["running", "succeeded", "retrying"],
            "consolidate":  ["succeeded", "running"],
        }.get(stage, ["succeeded", "running"])
        if i % 7 == 0: stage_pref.append("overdue")
        if i % 11 == 0: stage_pref.append("failed")
        pool = stage_pref

    for idx in range(n):
        st  = random.choice(pool)
        cid = f"c{idx}"
        # Build a RELATIVE log path under LOG_ROOT
        rel_log = f"{owner}/{mode}/{dn}/{stage}/{cid}.log"
        log_msg = f"[{owner} {mode} {dn} {stage} {cid}] status={st}\n"
        rel_written = write_log(rel_log, log_msg)
        items.append({
            "id": cid,
            "status": st,
            "proc": f"https://proc.example/{owner}/{mode}/{dn}/{stage}/{cid}",
            # IMPORTANT: give the relative path (for /logs/<rel>)
            "log":  rel_written or rel_log
        })

    # some empty-chunk leaves to test UI
    if (i + len(stage)) % 23 == 0:
        return []

    return items

def build_feed(version, owners, modes, n):
    """Return a list of stage objects for snapshot ingestion."""
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
                "chunks": chunks_for_version(version, i, owner, mode, dn, stg)
            })
    return items

def push(base, items):
    url = f"{base.rstrip('/')}/feed"
    r = requests.post(url, json=items, timeout=30)
    if r.status_code >= 400:
        url2 = f"{base.rstrip('/')}/ingest_snapshot"
        r = requests.post(url2, json={"snapshot": items}, timeout=30)
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
    ap.add_argument("--base", default=DEFAULT_BASE, help="App base URL (default: %(default)s)")
    ap.add_argument("--owners", nargs="*", default=OWNERS_DEFAULT, help="Owner list")
    ap.add_argument("--modes",  nargs="*", default=MODES_DEFAULT,  help="Mode list")
    ap.add_argument("--n", type=int, default=N_DATASETS, help="Number of datasets")
    ap.add_argument("--sleep", type=float, default=SLEEP_SEC, help="Seconds between pushes")
    args = ap.parse_args()

    print(f"Base: {args.base}")
    print(f"Owners: {args.owners}")
    print(f"Modes: {args.modes}")
    print(f"Datasets: {args.n}")
    print(f"Interval: {args.sleep}s")
    print(f"LOG_ROOT: {LOG_ROOT}\n")

    # Ensure LOG_ROOT exists
    Path(LOG_ROOT).mkdir(parents=True, exist_ok=True)

    reset(args.base)

    ver = 0
    while True:
        items = build_feed(ver, args.owners, args.modes, args.n)
        push(args.base, items)
        ver ^= 1
        time.sleep(args.sleep)

if __name__ == "__main__":
    main()