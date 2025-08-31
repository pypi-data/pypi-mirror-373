# test.py
# Feeder for the dashboard. Generates local log files and posts payloads to /feed.
# Statuses used are exactly: waiting, retrying, running, failed, overdue, manual, succeeded

import argparse
import random
import time
import requests
import os
from pathlib import Path
from datetime import datetime

# ---------- Easy-to-tweak defaults ----------
DEFAULT_BASE    = "http://127.0.0.1:8080"
OWNERS_DEFAULT  = ["QSG", "team-b"]      # change here or pass --owners QSG dg ...
MODES_DEFAULT   = ["live", "backfill"]
N_DATASETS_DEF  = 60
SLEEP_SEC_DEF   = 3.0
LOG_ROOT_DEF    = "/tmp/drm-logs"        # local absolute directory to write logs

STAGES   = ["stage", "archive", "enrich", "consolidate"]
STATUSES = ["waiting", "retrying", "running", "failed", "overdue", "manual", "succeeded"]

random.seed(11)

# ---------- Log helpers ----------
def log_path(log_root: Path, owner: str, mode: str, dn: str, stage: str, cid: str) -> Path:
    # Build absolute log path (the app expects absolute paths)
    p = (log_root / owner / mode / dn / stage / f"{cid}.log").resolve()
    return p

def write_log_if_needed(path: Path, status: str, version: int, allow_missing_prob: float):
    """
    Create/overwrite the log file with a small payload most of the time.
    With probability allow_missing_prob, deliberately don't create it (to test missing/permission).
    """
    if random.random() < allow_missing_prob:
        # ensure it's absent to test "(log not found)" viewer
        try:
            if path.exists():
                path.unlink()
        except Exception:
            pass
        return  # no file created

    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"[{now}] version={version} status={status}",
        f"Log file: {path}",
        "This is a synthetic log line to demonstrate the viewer.",
        "...\n"
    ]
    try:
        path.write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:
        # Fail silently; the app will show a readable message when it tries to cache/view
        print(f"warn: unable to write log {path}: {e}")

# ---------- Chunk builder ----------
def chunks_for_version(version: int, i: int, owner: str, mode: str, dn: str, stage: str,
                       log_root: Path, miss_prob: float):
    """
    Build a chunk list for (dataset i, stage) that changes with version.
    Ensures spread of the full status set and includes proc (URL) + log (absolute path).
    Occasionally returns [] to test empty chunks.
    """
    # Some rows intentionally empty
    if ((i + len(stage)) % 23) == 0:
        return []

    # Number of chunks varies by dataset+stage → 1..4
    n_chunks = 1 + ((i + len(stage)) % 4)

    if version == 0:
        stage_pref = {
            "stage":        ["running", "waiting", "retrying", "manual"],
            "archive":      ["waiting", "running", "manual"],
            "enrich":       ["waiting", "running", "retrying"],
            "consolidate":  ["waiting", "manual"],
        }.get(stage, ["waiting", "running"])
        # sprinkle some negatives
        if i % 10 == 0: stage_pref = stage_pref + ["overdue"]
        if i % 16 == 0: stage_pref = stage_pref + ["failed"]
    else:
        stage_pref = {
            "stage":        ["succeeded", "running", "manual"],
            "archive":      ["running", "succeeded"],
            "enrich":       ["running", "succeeded", "retrying"],
            "consolidate":  ["succeeded", "running"],
        }.get(stage, ["succeeded", "running"])
        if i % 7 == 0:  stage_pref = stage_pref + ["overdue"]
        if i % 11 == 0: stage_pref = stage_pref + ["failed"]

    items = []
    for idx in range(n_chunks):
        st  = random.choice(stage_pref)
        cid = f"c{idx}"
        lp  = log_path(log_root, owner, mode, dn, stage, cid)
        write_log_if_needed(lp, st, version, allow_missing_prob=miss_prob)
        items.append({
            "id": cid,
            "status": st,
            "proc": f"https://proc.example/{owner}/{mode}/{dn}/{stage}/{cid}",
            "log":  str(lp)  # absolute path → app will read & cache, then rewrite to /logview/<token>
        })
    return items

def build_feed(version: int, owners, modes, n: int, log_root: Path, miss_prob: float):
    """Return a list of stage objects for snapshot ingestion."""
    items = []
    for i in range(n):
        dn    = f"dataset-{i:03d}"
        owner = owners[i % len(owners)]
        mode  = modes[i % len(modes)]
        for stg in STAGES:
            items.append({
                "owner": owner,
                "mode": mode,
                "data_name": dn,
                "stage": stg,
                "chunks": chunks_for_version(version, i, owner, mode, dn, stg, log_root, miss_prob)
            })
    return items

# ---------- HTTP helpers ----------
def push(base, items):
    url = f"{base.rstrip('/')}/feed"
    r = requests.post(url, json=items, timeout=60)
    if r.status_code >= 400:
        # try the other form
        url2 = f"{base.rstrip('/')}/ingest_snapshot"
        r = requests.post(url2, json={"snapshot": items}, timeout=60)
    r.raise_for_status()
    try:
        print(f"pushed {len(items)} stage entries → {r.json()}")
    except Exception:
        print(f"pushed {len(items)} stage entries")

def reset(base):
    try:
        r = requests.post(f"{base.rstrip('/')}/store/reset", timeout=15)
        print("reset:", r.status_code, r.text)
    except Exception as e:
        print("reset failed (continuing):", e)

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base",    default=DEFAULT_BASE, help="App base URL")
    ap.add_argument("--owners",  nargs="*", default=OWNERS_DEFAULT, help="Owner list")
    ap.add_argument("--modes",   nargs="*", default=MODES_DEFAULT,  help="Mode list")
    ap.add_argument("--n",       type=int,  default=N_DATASETS_DEF, help="Number of datasets")
    ap.add_argument("--sleep",   type=float, default=SLEEP_SEC_DEF,  help="Seconds between pushes")
    ap.add_argument("--log-root", default=LOG_ROOT_DEF, help="Local directory to write logs")
    ap.add_argument("--miss-prob", type=float, default=0.15, help="Probability to omit a log file (0..1)")
    args = ap.parse_args()

    owners = args.owners
    modes  = [m.lower() for m in args.modes]  # app expects lowercase keys
    log_root = Path(args.log_root).expanduser().resolve()
    print(f"Base: {args.base}")
    print(f"Owners: {owners}")
    print(f"Modes: {modes}")
    print(f"Datasets: {args.n}")
    print(f"Log root: {log_root}")
    print(f"Missing-log probability: {args.miss_prob}")
    print(f"Interval: {args.sleep}s\n")

    # Ensure base log directory exists; per-file parents are created on demand
    try:
        log_root.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"warn: could not create log root {log_root}: {e}")

    reset(args.base)

    ver = 0
    while True:
        items = build_feed(ver, owners, modes, args.n, log_root, args.miss_prob)
        push(args.base, items)
        ver ^= 1
        time.sleep(args.sleep)

if __name__ == "__main__":
    main()