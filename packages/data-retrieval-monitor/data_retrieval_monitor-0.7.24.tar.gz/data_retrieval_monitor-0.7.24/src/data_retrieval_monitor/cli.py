import os
import argparse
from .app import build_app

def main():
    parser = argparse.ArgumentParser(description="Run Data Retrieval Monitor (Dash).")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8050")))

    # Defaults requested: memory + mock
    parser.add_argument("--store-backend", default=os.getenv("STORE_BACKEND", "memory"),
                        choices=["file", "memory"])
    parser.add_argument("--store-path", default=os.getenv("STORE_PATH", "status_store.json"))
    parser.add_argument("--mock", type=int, default=int(os.getenv("MOCK_MODE", "1")))
    parser.add_argument("--refresh-ms", type=int, default=int(os.getenv("REFRESH_MS", "30000")))
    parser.add_argument("--timezone", default=os.getenv("APP_TIMEZONE", "Europe/London"))
    parser.add_argument("--log-dir", default=os.getenv("LOG_DIR", "source_logs"))
    args = parser.parse_args()

    # Normalize to env (the app reads env at import)
    os.environ["STORE_BACKEND"] = args.store_backend
    os.environ["STORE_PATH"] = args.store_path
    os.environ["MOCK_MODE"] = str(args.mock)
    os.environ["REFRESH_MS"] = str(args.refresh_ms)
    os.environ["APP_TIMEZONE"] = args.timezone
    os.environ["LOG_DIR"] = args.log_dir

    app = build_app()
    # Dash >= 2.17
    app.run(host=args.host, port=args.port, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()