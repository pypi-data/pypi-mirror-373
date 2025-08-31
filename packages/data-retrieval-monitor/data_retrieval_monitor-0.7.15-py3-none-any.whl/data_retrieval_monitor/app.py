"""
Data Retrieval Monitor — side-by-side (no wrap) with:
- Placeholder pies (render even with zero data).
- Repeatable table groups (1..4 groups per row).
- Table widths size to content (no table-level horizontal scrollbar).
- In-memory log cache + safe on-disk fallback; missing/permission logs show message.
- Log links open a tiny HTML viewer page (/logview/...) so Dash doesn't intercept.

Endpoints:
  POST /ingest_snapshot  (or /feed)  -> replace all state
  POST /store/reset?seed=1           -> clear store (tiny seed optional)
  GET  /logview/<path:rel>           -> HTML page rendering cached log text
  GET  /logmem/<path:rel>            -> raw text (debug)

Env:
  DEFAULT_OWNER (default "QSG")
  DEFAULT_MODE  (default "live")
  REFRESH_MS (default 1000)
  STORE_BACKEND=memory|file, STORE_PATH
  APP_TIMEZONE (default Europe/London)
  LOG_ROOT (default "/tmp/drm-logs")
  LOG_GLOBS (default "*.log,*.txt")
  MAX_PAGE_WIDTH (default 2400), MAX_LEFT_WIDTH (default 360),
  MAX_GRAPH_WIDTH (default 440), MAX_KPI_WIDTH (default 220)
"""

import os, json, tempfile, pathlib, threading
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import quote
from html import escape as html_escape

import pytz
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from flask import request, jsonify, Response, abort

# ---------------- Config ----------------
APP_TITLE     = "Data Retrieval Monitor"
TIMEZONE      = os.getenv("APP_TIMEZONE", "Europe/London")
_DEF_TZ       = pytz.timezone(TIMEZONE)
REFRESH_MS    = int(os.getenv("REFRESH_MS", "1000"))
STORE_BACKEND = os.getenv("STORE_BACKEND", "memory")  # memory | file
STORE_PATH    = os.getenv("STORE_PATH", "status_store.json")

DEFAULT_OWNER = os.getenv("DEFAULT_OWNER", "QSG")
DEFAULT_MODE  = os.getenv("DEFAULT_MODE",  "live")

LOG_ROOT      = pathlib.Path(os.getenv("LOG_ROOT", "/tmp/drm-logs")).resolve()
LOG_GLOBS     = [g.strip() for g in os.getenv("LOG_GLOBS", "*.log,*.txt").split(",") if g.strip()]

# Layout caps (px)
MAX_PAGE_WIDTH  = int(os.getenv("MAX_PAGE_WIDTH",  "2400"))
MAX_LEFT_WIDTH  = int(os.getenv("MAX_LEFT_WIDTH",  "360"))
MAX_GRAPH_WIDTH = int(os.getenv("MAX_GRAPH_WIDTH", "440"))
MAX_KPI_WIDTH   = int(os.getenv("MAX_KPI_WIDTH",   "220"))
def _px(n: int) -> str: return f"{int(n)}px"

# Stages (fixed)
STAGES = ["stage", "archive", "enrich", "consolidate"]

# Statuses (worst → best)
JOB_STATUS_ORDER = ["failed", "overdue", "manual", "retrying", "running", "waiting", "succeeded"]
JOB_COLORS = {
    "waiting":   "#F0E442",
    "retrying":  "#E69F00",
    "running":   "#56B4E9",
    "failed":    "#D55E00",
    "overdue":   "#A50E0E",
    "manual":    "#808080",
    "succeeded": "#009E73",
}
def _hex_to_rgb(h): h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
JOB_RGB = {k: _hex_to_rgb(v) for k, v in JOB_COLORS.items()}
def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def norm(v): return str(v or "").strip().lower()

# ---------------- Store ----------------
STORE_LOCK = threading.RLock()
_MEM_STORE = None
_STORE_CACHE = None
_STORE_MTIME = None

def _init_store():
    return {"jobs": {}, "logs": [], "meta": {"owner_labels": {}}, "updated_at": utc_now_iso()}

def ensure_store():
    global _MEM_STORE
    if STORE_BACKEND == "memory":
        if _MEM_STORE is None:
            _MEM_STORE = _init_store()
        return
    p = pathlib.Path(STORE_PATH)
    if not p.exists():
        p.write_text(json.dumps(_init_store(), indent=2))

def load_store():
    ensure_store()
    if STORE_BACKEND == "memory":
        return _MEM_STORE
    global _STORE_CACHE, _STORE_MTIME
    with STORE_LOCK:
        mtime = os.path.getmtime(STORE_PATH)
        if _STORE_CACHE is not None and _STORE_MTIME == mtime:
            return _STORE_CACHE
        with open(STORE_PATH, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
        _STORE_CACHE, _STORE_MTIME = data, mtime
        return data

def save_store(store):
    store["updated_at"] = utc_now_iso()
    logs = store.setdefault("logs", [])
    if len(logs) > 2000:
        store["logs"] = logs[-2000:]
    if STORE_BACKEND == "memory":
        global _MEM_STORE
        with STORE_LOCK:
            _MEM_STORE = store
        return
    with STORE_LOCK:
        dir_ = os.path.dirname(os.path.abspath(STORE_PATH)) or "."
        fd, tmp = tempfile.mkstemp(prefix="store.", suffix=".tmp", dir=dir_)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as w:
                json.dump(store, w, indent=2)
                w.flush()
                os.fsync(w.fileno())
            os.replace(tmp, STORE_PATH)
            global _STORE_CACHE, _STORE_MTIME
            _STORE_CACHE = store
            _STORE_MTIME = os.path.getmtime(STORE_PATH)
        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass

def _ensure_leaf(store, owner: str, mode: str, data_name: str, stage: str) -> Dict:
    jobs = store.setdefault("jobs", {})
    o = jobs.setdefault(owner, {})
    m = o.setdefault(mode, {})
    d = m.setdefault(data_name, {})
    return d.setdefault(stage, {"chunks": [], "counts": {s:0 for s in JOB_STATUS_ORDER}, "errors": []})

def _zero_counts(leaf: Dict):
    leaf["counts"] = {s:0 for s in JOB_STATUS_ORDER}

def _recount_from_chunks(leaf: Dict):
    _zero_counts(leaf)
    for ch in leaf.get("chunks", []):
        st = norm(ch.get("status") or "waiting")
        if st in leaf["counts"]:
            leaf["counts"][st] += 1

def reset_jobs(store: dict):
    store["jobs"] = {}
    store.setdefault("logs", []).append({"ts": utc_now_iso(), "level":"INFO", "msg":"[SNAPSHOT] reset"})

# ---------------- Log cache (memory with safe fallback) ----------------
LOG_MEM: Dict[str, str] = {}
LOG_MEM_LOCK = threading.RLock()

def _read_file_safely(path: pathlib.Path) -> Optional[str]:
    try:
        return path.read_text("utf-8", errors="replace")
    except PermissionError:
        return "(permission denied)"
    except Exception:
        try:
            return path.read_bytes().decode("utf-8", errors="replace")
        except Exception:
            return None

def preload_logs():
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    with LOG_MEM_LOCK:
        for pat in LOG_GLOBS:
            for p in LOG_ROOT.rglob(pat):
                rel = str(p.relative_to(LOG_ROOT)).replace("\\", "/")
                if rel in LOG_MEM:
                    continue
                txt = _read_file_safely(p)
                if txt is None:
                    continue  # missing/unreadable silently skipped
                LOG_MEM[rel] = txt  # may be "(permission denied)"

def _safe_rel(path_like: str) -> Optional[str]:
    if not path_like:
        return None
    v = str(path_like).strip()
    if v.startswith("file://"):
        v = v[len("file://"):]
    p = pathlib.Path(v)
    try:
        p_abs = (LOG_ROOT / p).resolve() if not p.is_absolute() else p.resolve()
    except Exception:
        return None
    try:
        rel = str(p_abs.relative_to(LOG_ROOT)).replace("\\", "/")
    except Exception:
        return None
    if ".." in rel or rel.startswith("/"):
        return None
    return rel

def cache_log_if_available(rel: str):
    with LOG_MEM_LOCK:
        if rel in LOG_MEM:
            return
    p = (LOG_ROOT / rel).resolve()
    try:
        p.relative_to(LOG_ROOT)
    except Exception:
        return
    if not p.exists():
        return
    txt = _read_file_safely(p)
    if txt is None:
        return
    with LOG_MEM_LOCK:
        LOG_MEM[rel] = txt

# ---------------- Apply snapshot (rewrite 'log' → /logview/<rel>) ----------------
def apply_snapshot(store: dict, items: List[dict]):
    reset_jobs(store)
    labels = store.setdefault("meta", {}).setdefault("owner_labels", {})
    for it in items or []:
        owner_raw = (it.get("owner") or DEFAULT_OWNER).strip()
        owner_key = norm(owner_raw)
        mode_raw  = (it.get("mode")  or DEFAULT_MODE).strip()
        mode_key  = norm(mode_raw)
        dn        = it.get("data_name") or "unknown"
        stg       = norm(it.get("stage") or "stage")
        labels.setdefault(owner_key, owner_raw)  # keep original casing once

        leaf = _ensure_leaf(store, owner_key, mode_key, dn, stg)

        chunks: List[dict] = []
        for ch in (it.get("chunks") or []):
            ch = dict(ch or {})
            raw_log = ch.get("log")
            rel = _safe_rel(str(raw_log)) if raw_log else None
            if rel:
                cache_log_if_available(rel)           # non-fatal if missing/unreadable
                ch["log"] = f"/logview/{quote(rel)}"  # viewer page; may show not-found/denied
            else:
                # keep http(s) or None as-is
                ch["log"] = raw_log
            chunks.append(ch)

        leaf["chunks"] = chunks
        leaf["errors"] = list(it.get("errors", []))[-50:] if isinstance(it.get("errors"), list) else []
        _recount_from_chunks(leaf)

# ---------------- Aggregation ----------------
def aggregate_counts(store: dict) -> Dict[str, int]:
    tot = {s:0 for s in JOB_STATUS_ORDER}
    for o_map in store.get("jobs", {}).values():
        for m_map in o_map.values():
            for d_map in m_map.values():
                for leaf in d_map.values():
                    for s, v in leaf["counts"].items():
                        tot[s] += int(v or 0)
    return tot

def filtered_stage_counts(store: dict, owner: Optional[str], mode: Optional[str], stage: str) -> Dict[str,int]:
    owner_sel = norm(owner)
    mode_sel  = norm(mode)
    want_owner = None if owner_sel in ("", "all") else owner_sel
    want_mode  = None if mode_sel  in ("", "all") else mode_sel
    tot = {s:0 for s in JOB_STATUS_ORDER}
    for own, o_map in store.get("jobs", {}).items():
        if want_owner and own != want_owner: continue
        for md, m_map in o_map.items():
            if want_mode and md != want_mode: continue
            for d_map in m_map.values():
                leaf = d_map.get(stage)
                if not leaf: continue
                for s, v in leaf["counts"].items():
                    tot[s] += int(v or 0)
    return tot

def list_filters(store: dict):
    jobs   = store.get("jobs", {})
    labels = store.get("meta", {}).get("owner_labels", {})
    owner_keys = sorted(jobs.keys())                 # *only* owners present in data
    owner_opts = [{"label": "All", "value": "All"}] + [
        {"label": labels.get(k, k), "value": k} for k in owner_keys
    ]
    modes_keys = set()
    for o_map in jobs.values():
        modes_keys.update(o_map.keys())
    modes = sorted(modes_keys or {"live", "backfill"})
    mode_opts = [{"label": "All", "value": "All"}] + [{"label": m.title(), "value": m} for m in modes]
    return owner_opts, mode_opts

def best_status(counts: Dict[str,int]) -> Optional[str]:
    for s in JOB_STATUS_ORDER:
        if int(counts.get(s, 0) or 0) > 0:
            return s
    return None

# ---------------- UI helpers ----------------
def shade_for_status(status: Optional[str], alpha=0.18):
    if not status: return {"backgroundColor":"#FFFFFF"}
    r,g,b = JOB_RGB[status]
    return {"backgroundColor": f"rgba({r},{g},{b},{alpha})"}

def chunk_line(chunks: List[dict]):
    if not chunks:
        return html.I("—", className="text-muted")
    nodes = []
    for idx, ch in enumerate(chunks):
        cid  = ch.get("id") or f"c{idx}"
        st   = norm(ch.get("status") or "waiting")
        proc = ch.get("proc")
        log  = ch.get("log")  # already /logview/... for local logs (or http)
        nodes.append(html.Span(
            cid,
            style={"display":"inline-block","padding":"2px 6px","borderRadius":"8px",
                   "fontSize":"12px","marginRight":"6px", **shade_for_status(st, 0.35)}
        ))
        if proc: nodes.append(html.A("proc", href=proc, target="_blank", style={"marginRight":"6px"}))
        if log:  nodes.append(html.A("log",  href=log,  target="_blank", style={"marginRight":"10px"}))
        nodes.append(html.Span(" ", style={"marginRight":"6px"}))
    return html.Div(nodes, style={"whiteSpace":"nowrap", "paddingBottom":"2px"})

# -------- table: collect groups, then pack N groups per row (width = content) --------
def gather_dataset_groups(store: dict, owner: Optional[str], mode: Optional[str],
                          stage_filter: List[str], status_filter: List[str]) -> List[List[html.Td]]:
    owner_sel = norm(owner)
    mode_sel  = norm(mode)
    want_owner = None if owner_sel in ("", "all") else owner_sel
    want_mode  = None if mode_sel  in ("", "all") else mode_sel

    sel_stages = [norm(s) for s in (stage_filter or []) if norm(s) in STAGES] or STAGES[:]
    sel_status = [norm(s) for s in (status_filter or []) if norm(s) in JOB_STATUS_ORDER]
    filter_by_status = len(sel_status) > 0

    groups: List[List[html.Td]] = []
    labels = store.get("meta", {}).get("owner_labels", {})

    for own in sorted(store.get("jobs", {}).keys()):
        if want_owner and own != want_owner: continue
        o_map = store["jobs"][own]
        for md in sorted(o_map.keys()):
            if want_mode and md != want_mode: continue
            m_map = o_map[md]
            for dn in sorted(m_map.keys()):
                d_map = m_map[dn]
                stage_status = {stg: best_status((d_map.get(stg) or {"counts":{}})["counts"])
                                for stg in STAGES}
                if filter_by_status and not any((stage_status.get(stg) in sel_status) for stg in sel_stages):
                    continue

                owner_label = labels.get(own, own)
                title = f"{owner_label} / {dn}" if not want_owner else dn
                cells: List[html.Td] = [html.Td(title, style={"fontWeight":"600","whiteSpace":"nowrap"})]
                for stg in STAGES:
                    leaf = d_map.get(stg, {"counts":{s:0 for s in JOB_STATUS_ORDER}, "chunks":[]})
                    status = stage_status[stg]
                    style = {"verticalAlign":"top","padding":"6px 10px", **shade_for_status(status, 0.18)}
                    cells.append(html.Td(chunk_line(leaf.get("chunks", [])), style=style))
                groups.append(cells)
    return groups

def chunked(iterable: List, n: int) -> List[List]:
    return [iterable[i:i+n] for i in range(0, len(iterable), n)]

def build_table_component(groups: List[List[html.Td]], groups_per_row: int) -> dbc.Table:
    gpr = max(1, min(int(groups_per_row or 1), 4))  # clamp 1..4

    # header
    head_cells = []
    for _ in range(gpr):
        head_cells.extend([
            html.Th("Dataset", style={"whiteSpace":"nowrap"}),
            html.Th("Stage"), html.Th("Archive"), html.Th("Enrich"), html.Th("Consolidate")
        ])
    head = html.Thead(html.Tr(head_cells))

    # body rows
    body_rows = []
    for row_groups in chunked(groups, gpr):
        tds: List[html.Td] = []
        for grp in row_groups:
            tds.extend(grp)
        if len(row_groups) < gpr:
            for _ in range(gpr - len(row_groups)):
                tds.extend([html.Td(""), html.Td(""), html.Td(""), html.Td(""), html.Td("")])
        body_rows.append(html.Tr(tds))

    if not body_rows:
        body_rows = [html.Tr(html.Td("No data", colSpan=5*gpr, className="text-muted"))]

    # Size-to-content; never stretch to full viewport width; no table-level h-scroll.
    return dbc.Table(
        [head, html.Tbody(body_rows)],
        bordered=True, hover=False, size="sm", className="mb-1",
        style={"tableLayout": "auto", "width": "auto", "display": "inline-block", "maxWidth": "none"}
    )

# ---------------- Pies ----------------
def pie_figure(title_text: str, counts: Dict[str,int]):
    labels = [s.title() for s in JOB_STATUS_ORDER]
    raw_values = [int(counts.get(s, 0) or 0) for s in JOB_STATUS_ORDER]
    total = sum(raw_values)

    colors, values, texttempl = [], [], []
    if total == 0:
        for s in JOB_STATUS_ORDER:
            r, g, b = JOB_RGB[s]
            colors.append(f"rgba({r},{g},{b},0.12)")
            values.append(1)
            texttempl.append("%{label}")
        hover = "%{label}: 0<extra></extra>"
    else:
        for s, v in zip(JOB_STATUS_ORDER, raw_values):
            r, g, b = JOB_RGB[s]
            colors.append(f"rgba({r},{g},{b},{0.9 if v>0 else 0.0})")
            values.append(v)
            texttempl.append("" if v == 0 else "%{label} %{percent}")
        hover = "%{label}: %{value}<extra></extra>"

    trace = {
        "type": "pie",
        "labels": labels,
        "values": values,
        "hole": 0.45,
        "marker": {"colors": colors, "line": {"width": 0}},
        "texttemplate": texttempl,
        "textposition": "outside",
        "hovertemplate": hover,
        "showlegend": True,
    }

    return {
        "data": [trace],
        "layout": {
            "annotations": [{
                "text": title_text,
                "xref": "paper", "yref": "paper",
                "x": 0.5, "y": 1.12,
                "xanchor": "center", "yanchor": "top",
                "showarrow": False, "font": {"size": 13}
            }],
            "margin": {"l": 10, "r": 10, "t": 26, "b": 10},
            "legend": {"orientation": "h"},
            "title": {"text": ""}
        }
    }

# ---------------- App + Routes ----------------
external_styles = [dbc.themes.FLATLY]
app = Dash(__name__, external_stylesheets=external_styles, title=APP_TITLE)
server = app.server

@server.post("/ingest_snapshot")
def route_ingest_snapshot():
    try:
        body = request.get_json(force=True, silent=False)
        items = body["snapshot"] if isinstance(body, dict) and "snapshot" in body else body
        if not isinstance(items, list):
            return jsonify({"ok": False, "error": "Send {snapshot:[...]} or a JSON array."}), 400
        store = load_store()
        apply_snapshot(store, items)
        save_store(store)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@server.post("/feed")
def route_feed():
    return route_ingest_snapshot()

@server.post("/store/reset")
def route_reset():
    seed = request.args.get("seed", "0") == "1"
    store = _init_store()
    if seed:
        _ = _ensure_leaf(store, norm(DEFAULT_OWNER), norm(DEFAULT_MODE), "dataset-000", "stage")
    save_store(store)
    return jsonify({"ok": True, "seeded": seed})

# Raw text (debug)
@server.get("/logmem/<path:rel>")
def route_logmem(rel: str):
    clean = rel.lstrip("/").replace("\\", "/")
    if ".." in clean:
        return abort(400)
    with LOG_MEM_LOCK:
        txt = LOG_MEM.get(clean)
    if txt is None:
        p = (LOG_ROOT / clean).resolve()
        try:
            p.relative_to(LOG_ROOT)
        except Exception:
            return abort(404)
        if not p.exists():
            return Response(f"(log not found: {clean})", mimetype="text/plain", status=404)
        txt = _read_file_safely(p) or "(unable to read log)"
        with LOG_MEM_LOCK:
            LOG_MEM[clean] = txt
    return Response(txt, mimetype="text/plain")

# HTML viewer (new tab) — shows missing/permission messages too
@server.get("/logview/<path:rel>")
def route_logview(rel: str):
    clean = rel.lstrip("/").replace("\\", "/")
    if ".." in clean:
        return abort(400)
    with LOG_MEM_LOCK:
        txt = LOG_MEM.get(clean)
    if txt is None:
        p = (LOG_ROOT / clean).resolve()
        try:
            p.relative_to(LOG_ROOT)
        except Exception:
            return abort(404)
        if not p.exists():
            txt = f"(log not found: {clean})"
        else:
            txt = _read_file_safely(p) or "(unable to read log: permission denied?)"
        with LOG_MEM_LOCK:
            LOG_MEM[clean] = txt

    title = f"Log: {clean}"
    body  = html_escape(txt)
    html_doc = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{html_escape(title)}</title>
    <style>
      body {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; margin: 16px; }}
      pre  {{ white-space: pre-wrap; word-wrap: break-word; }}
    </style>
  </head>
  <body>
    <h3>{html_escape(title)}</h3>
    <pre>{body}</pre>
  </body>
</html>"""
    return Response(html_doc, mimetype="text/html")

# ---------------- Controls & KPIs ----------------
controls_card = dbc.Card(
    dbc.CardBody([
        html.Div("Owner", className="text-muted small"),
        dcc.Dropdown(id="owner-filter", options=[{"label":"All","value":"All"}],
                     value="All", clearable=False, className="mb-2", style={"minWidth":"180px"}),
        html.Div("Mode", className="text-muted small"),
        dcc.Dropdown(id="mode-filter",
                     options=[{"label":"All","value":"All"}],
                     value="All", clearable=False, className="mb-2", style={"minWidth":"180px"}),
        html.Div("Stage filter (ANY of)", className="text-muted small"),
        dcc.Dropdown(id="stage-filter",
                     options=[{"label": s.title(), "value": s} for s in STAGES],
                     value=STAGES, multi=True, className="mb-2"),
        html.Div("Status filter (ANY of)", className="text-muted small"),
        dcc.Dropdown(id="status-filter",
                     options=[{"label": s.title(), "value": s} for s in JOB_STATUS_ORDER],
                     value=[], multi=True, placeholder="(none)"),
        html.Div("Table groups per row", className="text-muted small mt-2"),
        dcc.Dropdown(id="table-groups",
                     options=[{"label": str(n), "value": n} for n in (1,2,3,4)],
                     value=1, clearable=False, style={"width":"120px"}),
    ])
)

def kpi_card(title, comp_id):
    return dbc.Card(
        dbc.CardBody([html.Div(title, className="text-muted small"), html.H4(id=comp_id, className="mb-0")]),
        style={"maxWidth": _px(MAX_KPI_WIDTH), "margin":"0"}
    )

kpi_row_top = html.Div([
    kpi_card("Waiting",  "kpi-waiting"),
    kpi_card("Retrying", "kpi-retrying"),
    kpi_card("Running",  "kpi-running"),
    kpi_card("Failed",   "kpi-failed"),
], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginTop":"8px"})

kpi_row_bottom = html.Div([
    kpi_card("Overdue",   "kpi-overdue"),
    kpi_card("Manual",    "kpi-manual"),
    kpi_card("Succeeded", "kpi-succeeded"),
], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginTop":"8px"})

def pie_holder(comp_id, title_text):
    return dcc.Graph(
        id=comp_id,
        figure={"layout":{"title":{"text": title_text}}},
        style={"height":"320px", "maxWidth": _px(MAX_GRAPH_WIDTH), "margin":"0"}
    )

pies_block = html.Div(
    [
        pie_holder("pie-stage", "Stage"),
        pie_holder("pie-archive", "Archive"),
        pie_holder("pie-enrich", "Enrich"),
        pie_holder("pie-consolidate", "Consolidate"),
    ],
    className="mb-2",
    style={"display":"flex","gap":"12px","flexWrap":"wrap","paddingBottom":"8px"}
)

# Side-by-side, no wrap; header with timestamp pushed far right
two_col_nowrap = html.Div([
    html.Div([controls_card, kpi_row_top, kpi_row_bottom, pies_block],
             style={"width": _px(MAX_LEFT_WIDTH), "minWidth": _px(MAX_LEFT_WIDTH),
                    "maxWidth": _px(MAX_LEFT_WIDTH), "flex":"0 0 auto"}),
    html.Div([
        html.Div([
            html.H4("Datasets", className="fw-semibold", style={"margin":"0","whiteSpace":"nowrap"}),
            html.Div(id="table-container", style={"flex":"0 0 auto"})
        ], style={"display":"flex","alignItems":"flex-start","gap":"8px","width":"100%"}),
    ], style={"flex":"1 1 auto","minWidth":"0"}),
], style={"display":"flex","flexWrap":"nowrap","alignItems":"flex-start",
          "gap":"16px","maxWidth":_px(MAX_PAGE_WIDTH),"margin":"0 auto"})

app.layout = dbc.Container([
    html.Div([
        html.Div(APP_TITLE, className="h2 fw-bold"),
        html.Div(id="now-indicator", className="text-muted", style={"marginLeft":"auto"})
    ], style={"display":"flex","alignItems":"center","gap":"12px",
              "maxWidth": _px(MAX_PAGE_WIDTH), "margin":"0 auto"}),

    two_col_nowrap,

    dcc.Interval(id="interval", interval=REFRESH_MS, n_intervals=0)
], fluid=True, className="pt-3 pb-4", style={"maxWidth": _px(MAX_PAGE_WIDTH), "margin":"0 auto"})

# ---------------- Callback ----------------
@app.callback(
    Output("kpi-waiting","children"),
    Output("kpi-retrying","children"),
    Output("kpi-running","children"),
    Output("kpi-failed","children"),
    Output("kpi-overdue","children"),
    Output("kpi-manual","children"),
    Output("kpi-succeeded","children"),
    Output("owner-filter","options"),
    Output("mode-filter","options"),
    Output("pie-stage","figure"),
    Output("pie-archive","figure"),
    Output("pie-enrich","figure"),
    Output("pie-consolidate","figure"),
    Output("table-container","children"),
    Output("now-indicator","children"),
    Output("interval","interval"),
    Input("interval","n_intervals"),
    Input("owner-filter","value"),
    Input("mode-filter","value"),
    Input("stage-filter","value"),
    Input("status-filter","value"),
    Input("table-groups","value"),
    State("interval","interval"),
)
def refresh(_n, owner_sel, mode_sel, stage_filter, status_filter, groups_per_row, cur_interval):
    interval_ms = int(cur_interval or REFRESH_MS)
    store = load_store()

    # KPIs (global)
    k = aggregate_counts(store)
    kpi_vals = [str(k[s]) for s in ["waiting","retrying","running","failed","overdue","manual","succeeded"]]

    # Filters options reflect *all* data actually present
    owner_opts, mode_opts = list_filters(store)

    # Pies (owner/mode filtered)
    figs = []
    for stg in STAGES:
        c = filtered_stage_counts(store, owner_sel, mode_sel, stg)
        figs.append(pie_figure(stg.title(), c))

    # Table (groups per row ; width = content)
    groups = gather_dataset_groups(store, owner_sel, mode_sel, stage_filter or [], status_filter or [])
    table_comp = build_table_component(groups, groups_per_row or 1)

    now_local = datetime.now(_DEF_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    return (*kpi_vals, owner_opts, mode_opts, *figs, table_comp, f"Refreshed: {now_local}", interval_ms)

# ---------------- Run ----------------
if __name__ == "__main__":
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    preload_logs()  # initial preload (skips missing/unreadable), viewer handles the rest
    app.run(host="0.0.0.0", port=8080, debug=False)