# Data Retrieval Monitor

A Plotly Dash app to visualize data-retrieval health: validation failures (amber), delays (yellow), overdue/retrieve-failed (red), and healthy (green).

## Install
```bash
pip install data-retrieval-monitor
```
## Run
```bash
data-retrieval-monitor --host 0.0.0.0 --port 8050```

# Defaults: STORE_BACKEND=memory, MOCK_MODE=1.

# Open http://127.0.0.1:8050

## Example injector (5s loop)
```bash
drm-injector --url http://127.0.0.1:8050/ingest_status --batch-size 25 --sleep 5
```
Env knobs
	•	STORE_BACKEND = memory | file
	•	STORE_PATH (when file)
	•	MOCK_MODE 0/1
	•	APP_TIMEZONE, REFRESH_MS, LOG_DIR
---

## Build, install, publish


# from project root
```bash
python -m pip install --upgrade pip setuptools wheel build twine``

# build
```bash
rm -rf dist
python -m build
ls -lh dist
```

# local install
```bash
python -m pip install dist/*.whl```

# run
```bash data-retrieval-monitor --host 0.0.0.0 --port 8050```
# (optional) injector
```bash drm-injector --url http://127.0.0.1:8050/ingest_status --batch-size 25 --sleep 5```






