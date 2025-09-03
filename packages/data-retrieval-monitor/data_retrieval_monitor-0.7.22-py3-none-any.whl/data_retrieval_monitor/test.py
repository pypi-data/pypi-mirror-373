# test.py
# Feeder for the app (posts to /feed). Exact statuses; includes empties and missing logs.
import argparse
import random
import time
import requests
from datetime import datetime, timezone
import os

DEFAULT_BASE   = "http://127.0.0.1:8060"
OWNERS_DEFAULT = ["QSG", "dg"]
MODES_DEFAULT  = ["live", "backfill"]
N_DATASETS     = 24
SLEEP_SEC      = 3.0

STAGES   = ["archive", "stage", "enrich", "consolidate"]
STATUSES = ["waiting", "retrying", "running", "failed", "overdue", "manual", "succeeded"]

random.seed(11)

# Point some logs under LOG_ROOT, some outside, some localhost URLs, some missing
LOG_ROOT = os.environ.get("LOG_ROOT", "/tmp/drm-logs")

def chunks_for_version(version, i, owner, mode, dn, stage):
    # number of chunks 0..4 to test empties and wrapping
    n = (i + len(stage)) % 5  # 0..4
    items = []

    # pool distribution
    if version == 0:
        pool = ["running","waiting","retrying","manual"]
        if i % 7 == 0: pool.append("overdue")
        if i % 11 == 0: pool.append("failed")
    else:
        pool = ["succeeded","running","waiting"]
        if i % 5 == 0: pool.append("retrying")
        if i % 13 == 0: pool.append("failed")

    for idx in range(n):
        st = random.choice(pool)
        cid = f"c{idx}"
        # Mix of log styles
        if idx % 4 == 0:
            log = f"{LOG_ROOT}/{owner}/{mode}/{dn}/{stage}/{cid}.log"             # under LOG_ROOT (may or may not exist)
        elif idx % 4 == 1:
            log = f"/var/tmp/outside/{owner}/{mode}/{dn}/{stage}/{cid}.log"       # outside LOG_ROOT (likely missing -> mem/no-link)
        elif idx % 4 == 2:
            log = f"http://localhost:8090{LOG_ROOT}/{owner}/{mode}/{dn}/{stage}/{cid}.log"  # localhost URL -> normalized to path
        else:
            log = f"https://logs.example/{owner}/{mode}/{dn}/{stage}/{cid}.log"   # external URL

        items.append({
            "id": cid,
            "status": st,
            "proc": f"https://proc.example/{owner}/{mode}/{dn}/{stage}/{cid}",
            "log":  log
        })

    # force some empties
    if (i + len(stage)) % 9 == 0:
        return []

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
                "chunks": chunks_for_version(version, i, owner, mode, dn, stg)
            })
    return items

def push(base, items):
    url = f"{base.rstrip('/')}/feed"
    payload = {
        "snapshot": items,
        "ingested_at": datetime.now(timezone.utc).isoformat()
    }
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