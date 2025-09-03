import os
import json
import time
import random
from datetime import datetime, timedelta, timezone
import argparse
import requests
from requests.exceptions import RequestException

KINDS = [
    ("stream", 5, 2),
    ("hourly", 60, 10),
    ("daily", 1440, 60),
]

def make_payloads(n: int):
    now = datetime.now(timezone.utc)
    payloads = []
    for i in range(n):
        kind, expected_m, grace_m = random.choice(KINDS)

        skew = random.random()
        if skew < 0.55:
            minutes_ago = random.randint(0, max(1, expected_m // 2))             # Healthy-ish
        elif skew < 0.85:
            minutes_ago = expected_m + grace_m + random.randint(1, 120)          # Delayed/Overdue
        else:
            minutes_ago = expected_m + random.randint(1, grace_m)                # Close to grace

        last_received_at = (now - timedelta(minutes=minutes_ago)).isoformat()

        # ~15% “pure validation failure” (retrieval success)
        run_status = "failed" if random.random() < 0.12 else "success"
        last_validation_passed = False if (run_status == "success" and random.random() < 0.15) else True

        # Sometimes specify absolute expected/grace; sometimes intervals
        if random.random() < 0.4:
            expected_at = (now + timedelta(minutes=random.randint(1, expected_m))).isoformat()
            if random.random() < 0.5:
                grace_until = (datetime.fromisoformat(expected_at) + timedelta(minutes=random.randint(1, max(2, grace_m)))).isoformat()
                grace_minutes = None
            else:
                grace_until = None
                grace_minutes = grace_m
            expected_every_minutes = None
        else:
            expected_at = None
            grace_until = None
            grace_minutes = grace_m
            expected_every_minutes = expected_m

        data_reset_at = None
        if random.random() < 0.15:
            data_reset_at = (now - timedelta(minutes=random.randint(0, expected_m))).isoformat()

        error_message = "" if (run_status == "success" and last_validation_passed) else random.choice(
            ["Timeout from vendor API", "ValidationError: NaNs detected", "File missing in S3", "HTTP 500 from upstream"]
        )

        sid = f"beta_factors_{random.randint(0, 99999):05d}"
        name = f"Beta Factors {sid[-4:]} ({kind.title()})"

        meta = {
            "rows": random.randint(1_000, 120_000),
            "file": f"{sid}_{now.date()}.parquet",
            "docs": f"https://example.com/{sid}",
            "log": f"/logs/{sid}.log",
        }

        payloads.append({
            "source_id": sid,
            "name": name,
            "expected_every_minutes": expected_every_minutes,
            "expected_at": expected_at,
            "data_reset_at": data_reset_at,
            "grace_minutes": grace_minutes,
            "grace_until": grace_until,
            "last_received_at": last_received_at,
            "last_validation_passed": last_validation_passed,
            "validation_errors": [] if last_validation_passed else ["Auto-check failed"],
            "run_status": run_status,
            "error_message": error_message,
            "meta": meta
        })
    return payloads

def main():
    p = argparse.ArgumentParser(description="Looping injector for Data Retrieval Monitor.")
    p.add_argument("--url", default=os.getenv("INGEST_URL", "http://127.0.0.1:8050/ingest_status"))
    p.add_argument("--batch-size", type=int, default=25)
    p.add_argument("--sleep", type=float, default=5.0, help="Seconds between batches")
    p.add_argument("--max-batches", type=int, default=0, help="0 = infinite")
    args = p.parse_args()

    print(f"Looping inject to {args.url} (batch={args.batch_size}, every {args.sleep}s). Ctrl+C to stop.")
    i = 0
    try:
        while True:
            payloads = make_payloads(args.batch_size)
            try:
                r = requests.post(args.url,
                                  headers={"Content-Type": "application/json"},
                                  data=json.dumps(payloads),
                                  timeout=20)
                print(time.strftime("%H:%M:%S"), r.status_code, r.text[:200])
            except RequestException as e:
                print(time.strftime("%H:%M:%S"), "inject failed:", e)

            i += 1
            if args.max-batches and i >= args.max_batches:
                break
            time.sleep(args.sleep)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()