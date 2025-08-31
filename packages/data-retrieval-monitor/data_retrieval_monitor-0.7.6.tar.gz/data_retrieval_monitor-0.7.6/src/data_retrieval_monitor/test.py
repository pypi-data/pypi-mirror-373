# test.py
# Feeder for the app (posts to /feed). No aliases — uses the exact statuses:
# waiting, retrying, running, failed, overdue, manual, succeeded

import argparse
import random
import time
import requests

# ---------- Easy-to-tweak defaults ----------
DEFAULT_BASE   = "http://127.0.0.1:8070"
OWNERS_DEFAULT = ["QSG", "team-b"]     # change here (and/or via --owners ...)
MODES_DEFAULT  = ["live", "backfill"]
N_DATASETS     = 60
SLEEP_SEC      = 3

STAGES = ["stage", "archive", "enrich", "consolidate"]
STATUSES = ["waiting", "retrying", "running", "failed", "overdue", "manual", "succeeded"]

random.seed(11)

def chunks_for_version(version, i, owner, mode, dn, stage):
    """
    Build a chunk list for (dataset i, stage) that changes with version.
    Ensures we hit the full status set (no aliases) and includes proc/log links.
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

    # build chunks
    for idx in range(n):
        st = random.choice(pool)
        cid = f"c{idx}"
        items.append({
            "id": cid,
            "status": st,
            "proc": f"https://proc.example/{owner}/{mode}/{dn}/{stage}/{cid}",
            "log":  f"https://logs.example/{owner}/{mode}/{dn}/{stage}/{cid}.log"
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
    print(f"Interval: {args.sleep}s\n")

    reset(args.base)

    ver = 0
    while True:
        items = build_feed(ver, args.owners, args.modes, args.n)
        push(args.base, items)
        ver ^= 1
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()