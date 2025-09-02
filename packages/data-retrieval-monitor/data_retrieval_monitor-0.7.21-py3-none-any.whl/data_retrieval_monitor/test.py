# test.py
# Feeder for the app (posts to /feed). Uses exact statuses:
# waiting, retrying, running, failed, overdue, manual, succeeded
# Writes example logs under LOG_ROOT by default, and also demonstrates an absolute-path log.

import argparse
import random
import time
import requests
import pathlib
import os 

DEFAULT_BASE   = "http://127.0.0.1:8080"
OWNERS_DEFAULT = ["QSG", "dg"]
MODES_DEFAULT  = ["live", "backfill"]
N_DATASETS     = 40
SLEEP_SEC      = 3

STAGES   = ["stage", "archive", "enrich", "consolidate"]
STATUSES = ["waiting", "retrying", "running", "failed", "overdue", "manual", "succeeded"]

random.seed(42)

def write_demo_log(base_dir: pathlib.Path, owner: str, mode: str, dn: str, stage: str, cid: str) -> str:
    """
    Create a small log under base_dir/workspaces/... and return ABSOLUTE path.
    The app will read this from disk (if under LOG_ROOT) or cache in memory (if outside).
    """
    p = base_dir / "workspaces" / owner / mode / dn / stage
    p.mkdir(parents=True, exist_ok=True)
    f = p / f"{cid}.log"
    f.write_text(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] demo log for {owner}/{mode}/{dn}/{stage}/{cid}\n", encoding="utf-8")
    return str(f.resolve())

def chunks_for_version(version, i, owner, mode, dn, stage, logs_base: pathlib.Path):
    # different number of chunks by dataset/stage to visualize variety
    n = 1 + ((i + len(stage)) % 4)  # 1..4
    items = []

    if version == 0:
        stage_pref = {
            "stage":        ["running", "waiting", "retrying", "manual"],
            "archive":      ["waiting", "running", "manual"],
            "enrich":       ["waiting", "running", "retrying"],
            "consolidate":  ["waiting", "manual"],
        }.get(stage, ["waiting", "running"])
        if i % 10 == 0: stage_pref.append("overdue")
        if i % 16 == 0: stage_pref.append("failed")
        pool = stage_pref
    else:
        stage_pref = {
            "stage":        ["succeeded", "running", "manual"],
            "archive":      ["running", "succeeded"],
            "enrich":       ["running", "succeeded", "retrying"],
            "consolidate":  ["succeeded", "running"],
        }.get(stage, ["succeeded", "running"])
        if i % 7 == 0:  stage_pref.append("overdue")
        if i % 11 == 0: stage_pref.append("failed")
        pool = stage_pref

    for idx in range(n):
        st  = random.choice(pool)
        cid = f"c{idx}"
        # create a local log file path (under logs_base/workspaces/...)
        local_log = write_demo_log(logs_base, owner, mode, dn, stage, cid)
        items.append({
            "id": cid,
            "status": st,
            "proc": f"https://proc.example/{owner}/{mode}/{dn}/{stage}/{cid}",
            # IMPORTANT: provide the FILE PATH (string) — the app will transform to /logview/...
            "log":  local_log
        })

    # sometimes produce an empty chunk list to validate UI
    if (i + len(stage)) % 23 == 0:
        return []

    return items

def build_feed(version, owners, modes, n, logs_base: pathlib.Path):
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
                "chunks": chunks_for_version(version, i, owner, mode, dn, stg, logs_base)
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
    ap.add_argument("--base",    default=DEFAULT_BASE, help="App base URL")
    ap.add_argument("--owners",  nargs="*", default=OWNERS_DEFAULT, help="Owner list")
    ap.add_argument("--modes",   nargs="*", default=MODES_DEFAULT,  help="Mode list")
    ap.add_argument("--n",       type=int, default=N_DATASETS, help="Number of datasets")
    ap.add_argument("--sleep",   type=float, default=SLEEP_SEC, help="Seconds between pushes")
    ap.add_argument("--logroot", default=os.environ.get("LOG_ROOT", "/tmp/drm-logs"),
                    help="Where to create example log files (should match app LOG_ROOT for disk-backed demo)")
    args = ap.parse_args()

    logs_base = pathlib.Path(args.logroot).resolve()
    logs_base.mkdir(parents=True, exist_ok=True)

    print(f"Base:     {args.base}")
    print(f"Owners:   {args.owners}")
    print(f"Modes:    {args.modes}")
    print(f"Datasets: {args.n}")
    print(f"LOG_ROOT: {logs_base}")
    print(f"Interval: {args.sleep}s\n")

    reset(args.base)
    ver = 0
    while True:
        items = build_feed(ver, args.owners, args.modes, args.n, logs_base)
        push(args.base, items)
        ver ^= 1
        time.sleep(args.sleep)

if __name__ == "__main__":
    main()