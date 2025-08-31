"""
Data Retrieval Monitor — side-by-side (no wrap) with pie placeholders,
repeatable table groups, and local log viewer (string-safe for leading zeros).

Endpoints:
  POST /ingest_snapshot  (or /feed)  -> replace all state
  POST /store/reset?seed=1           -> clear store (tiny seed optional)
  GET  /logview/<token>              -> serve cached log text (read once from local path)

Env:
  DEFAULT_OWNER (default "QSG")
  DEFAULT_MODE  (default "live")
  REFRESH_MS (default 1000)
  STORE_BACKEND=memory|file, STORE_PATH
  APP_TIMEZONE (default Europe/London)
  LOG_ROOT is NOT required (we read the exact local path provided in payload)
  MAX_PAGE_WIDTH (default 2400), MAX_LEFT_WIDTH (default 360),
  MAX_GRAPH_WIDTH (default 440), MAX_KPI_WIDTH (default 220)
"""

import os, json, tempfile, pathlib, threading, secrets
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import pytz
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from flask import request, jsonify, Response, abort

# ---------------- Config ----------------
BASE_GROUP_MIN_PX = int(os.getenv("BASE_GROUP_MIN_PX", "560"))  # min px per 5-column group
APP_TITLE     = "Data Retrieval Monitor"
TIMEZONE      = os.getenv("APP_TIMEZONE", "Europe/London")
_DEF_TZ       = pytz.timezone(TIMEZONE)
REFRESH_MS    = int(os.getenv("REFRESH_MS", "1000"))
STORE_BACKEND = os.getenv("STORE_BACKEND", "memory")  # memory | file
STORE_PATH    = os.getenv("STORE_PATH", "status_store.json")

DEFAULT_OWNER = os.getenv("DEFAULT_OWNER", "QSG")
DEFAULT_MODE  = os.getenv("DEFAULT_MODE",  "live")

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

# ---------------- Log cache (read local path once, serve via /logview/<token>) ----------------
LOG_CACHE: Dict[str, str] = {}         # token -> text
LOG_TOKEN_BY_PATH: Dict[str, str] = {} # normalized path -> token
LOG_LOCK = threading.RLock()

def _is_http_url(s: str) -> bool:
    return isinstance(s, str) and (s.startswith("http://") or s.startswith("https://"))

def _to_str_safe(v) -> str:
    try:
        return str(v)
    except Exception:
        return ""

def _normalize_path(p: str) -> str:
    # no real normalization beyond making it a consistent string
    return _to_str_safe(p)

def cache_log_once(local_path: str) -> str:
    """Read text from a local path once and return a stable token."""
    pnorm = _normalize_path(local_path)
    with LOG_LOCK:
        if pnorm in LOG_TOKEN_BY_PATH:
            return LOG_TOKEN_BY_PATH[pnorm]
        token = secrets.token_urlsafe(16)
        # try to read; if not accessible, store a friendly message
        try:
            txt = pathlib.Path(pnorm).read_text("utf-8", errors="replace")
        except Exception as e:
            txt = f"(log unavailable)\npath: {pnorm}\nerror: {e}\n"
        LOG_CACHE[token] = txt
        LOG_TOKEN_BY_PATH[pnorm] = token
        return token

# ---------------- Job tree helpers ----------------
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
        st = (ch.get("status") or "waiting").lower()
        if st in leaf["counts"]:
            leaf["counts"][st] += 1

def reset_jobs(store: dict):
    store["jobs"] = {}
    store.setdefault("logs", []).append({"ts": utc_now_iso(), "level":"INFO", "msg":"[SNAPSHOT] reset"})

def apply_snapshot(store: dict, items: List[dict]):
    """Replace entire state with items; coerce log values to strings and cache local logs."""
    reset_jobs(store)
    labels = store.setdefault("meta", {}).setdefault("owner_labels", {})
    for it in items or []:
        owner_raw = (it.get("owner") or DEFAULT_OWNER).strip()
        owner_key = owner_raw.lower()
        mode_raw  = (it.get("mode")  or DEFAULT_MODE).strip()
        mode_key  = mode_raw.lower()
        dn        = it.get("data_name") or "unknown"
        stg       = (it.get("stage") or "stage").lower()
        labels.setdefault(owner_key, owner_raw)

        leaf = _ensure_leaf(store, owner_key, mode_key, dn, stg)
        # Make a copy; coerce log to string and rewrite to /logview/<token> for local files
        chunks = list(it.get("chunks", []))
        for ch in chunks:
            if "log" in ch:
                lv_str = _to_str_safe(ch.get("log"))
                if lv_str and not _is_http_url(lv_str):
                    token = cache_log_once(lv_str)
                    ch["log"] = f"/logview/{token}"
                else:
                    ch["log"] = lv_str
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
    owner_sel = (owner or "").lower()
    mode_sel  = (mode  or "").lower()
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
    owner_keys = set(jobs.keys()) | {DEFAULT_OWNER.lower()}
    owners = sorted(owner_keys)
    owner_opts = [{"label": "All", "value": "All"}]
    for k in owners:
        owner_opts.append({"label": labels.get(k, k), "value": k})
    modes_keys = set()
    for o_map in jobs.values():
        modes_keys.update(o_map.keys())
    modes_keys |= {"live", "backfill", DEFAULT_MODE.lower()}
    modes = sorted(modes_keys)
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

def chunk_grid(chunks: List[dict], per_line: int):
    """Render chunk badges + links with fixed number per line."""
    per = max(1, int(per_line or 5))
    if not chunks:
        return html.I("—", className="text-muted")
    rows = []
    line = []
    for idx, ch in enumerate(chunks):
        cid  = ch.get("id") or f"c{idx}"
        st   = (ch.get("status") or "waiting").lower()
        proc = ch.get("proc")
        log  = ch.get("log")  # may be http(s) or /logview/<token>

        bits = [html.Span(
            cid,
            style={"display":"inline-block","padding":"2px 6px","borderRadius":"8px",
                   "fontSize":"12px","marginRight":"6px", **shade_for_status(st, 0.35)}
        )]
        if proc: bits.append(html.A("proc", href=str(proc), target="_blank", style={"marginRight":"6px"}))
        if log:  bits.append(html.A("log",  href=str(log),  target="_blank", style={"marginRight":"10px"}))

        line.extend(bits)

        # line break
        if (idx + 1) % per == 0:
            rows.append(html.Div(line, style={"whiteSpace":"nowrap"}))
            line = []
    if line:
        rows.append(html.Div(line, style={"whiteSpace":"nowrap"}))
    return html.Div(rows, style={"display":"inline-flex","flexDirection":"column","gap":"2px"})

# -------- table: build list of groups, then pack N groups per row --------
def gather_dataset_groups(store: dict, owner: Optional[str], mode: Optional[str],
                          stage_filter: List[str], status_filter: List[str]) -> List[Tuple[str, List[str], Dict[str,dict]]]:
    """
    Returns a list of tuples (title, stages_order, stage_leaves)
    where stage_leaves[stg] is the leaf dict for that stage (or default).
    """
    owner_sel = (owner or "").lower()
    mode_sel  = (mode  or "").lower()
    want_owner = None if owner_sel in ("", "all") else owner_sel
    want_mode  = None if mode_sel  in ("", "all") else mode_sel

    sel_stages = [s for s in (stage_filter or []) if s in STAGES] or STAGES[:]
    sel_status = [s for s in (status_filter or []) if s in JOB_STATUS_ORDER]
    filter_by_status = len(sel_status) > 0

    groups = []
    labels = store.get("meta", {}).get("owner_labels", {})

    for own in sorted(store.get("jobs", {}).keys()):
        if want_owner and own != want_owner: continue
        o_map = store["jobs"][own]
        for md in sorted(o_map.keys()):
            if want_mode and md != want_mode: continue
            m_map = o_map[md]
            for dn in sorted(m_map.keys()):
                d_map = m_map[dn]
                stage_leaves = {}
                stage_status = {}
                for stg in STAGES:
                    leaf = d_map.get(stg, {"counts":{s:0 for s in JOB_STATUS_ORDER}, "chunks":[]})
                    stage_leaves[stg] = leaf
                    stage_status[stg] = best_status(leaf["counts"])

                if filter_by_status and not any((stage_status.get(stg) in sel_status) for stg in sel_stages):
                    continue

                owner_label = labels.get(own, own)
                title = f"{owner_label} / {dn}" if not want_owner else dn
                groups.append((title, STAGES[:], stage_leaves))
    return groups

def chunked(iterable: List, n: int) -> List[List]:
    return [iterable[i:i+n] for i in range(0, len(iterable), n)]

def build_table_component(groups: List[Tuple[str, List[str], Dict[str,dict]]],
                          groups_per_row: int, chunks_per_line: int) -> dbc.Table:
    gpr = max(1, min(int(groups_per_row or 1), 4))  # clamp 1..4

    # header
    head_cells = []
    for _ in range(gpr):
        head_cells.extend([
            html.Th("Dataset", style={"whiteSpace":"nowrap"}),
            html.Th("Stage"), html.Th("Archive"), html.Th("Enrich"), html.Th("Consolidate")
        ])
    head = html.Thead(html.Tr(head_cells))

    # rows
    body_rows = []
    for row_groups in chunked(groups, gpr):
        tds: List[html.Td] = []
        for (title, order, leaves) in row_groups:
            # dataset cell
            tds.append(html.Td(title, style={"fontWeight":"600","whiteSpace":"nowrap"}))
            # 4 stage cells
            for stg in order:
                leaf = leaves.get(stg, {"counts":{s:0 for s in JOB_STATUS_ORDER}, "chunks":[]})
                status = best_status(leaf["counts"])
                style = {"verticalAlign":"top","padding":"6px 10px", **shade_for_status(status, 0.18)}
                tds.append(html.Td(chunk_grid(leaf.get("chunks", []), chunks_per_line), style=style))
        if len(row_groups) < gpr:
            for _ in range(gpr - len(row_groups)):
                tds.extend([html.Td(""), html.Td(""), html.Td(""), html.Td(""), html.Td("")])
        body_rows.append(html.Tr(tds))

    if not body_rows:
        body_rows = [html.Tr(html.Td("No data", colSpan=5*gpr, className="text-muted"))]

    # dynamic min width (only scroll if window narrower)
    min_width_px = BASE_GROUP_MIN_PX * gpr
    return dbc.Table(
        [head, html.Tbody(body_rows)],
        bordered=True, hover=False, size="sm", className="mb-1",
        style={"tableLayout": "auto", "width": "100%", "minWidth": f"{min_width_px}px"}
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
        _ = _ensure_leaf(store, DEFAULT_OWNER.lower(), DEFAULT_MODE.lower(), "dataset-000", "stage")
    save_store(store)
    return jsonify({"ok": True, "seeded": seed})

@server.get("/logview/<token>")
def route_logview(token: str):
    txt = LOG_CACHE.get(token)
    if txt is None:
        return abort(404)
    # simple text content; opens cleanly in new tab
    return Response(txt, mimetype="text/plain; charset=utf-8")

# ---------------- Controls & KPIs ----------------
controls_card = dbc.Card(
    dbc.CardBody([
        html.Div("Owner", className="text-muted small"),
        dcc.Dropdown(
            id="owner-filter",
            options=[{"label":"All", "value":"All"},
                     {"label": DEFAULT_OWNER, "value": DEFAULT_OWNER.lower()}],
            value=DEFAULT_OWNER.lower(),
            clearable=False, className="mb-2", style={"minWidth":"180px"},
        ),
        html.Div("Mode", className="text-muted small"),
        dcc.Dropdown(
            id="mode-filter",
            options=[{"label":"All", "value":"All"},
                     {"label":"Live", "value":"live"},
                     {"label":"Backfill", "value":"backfill"}],
            value=DEFAULT_MODE.lower(),
            clearable=False, className="mb-2", style={"minWidth":"180px"},
        ),
        html.Div("Stage filter (ANY of)", className="text-muted small"),
        dcc.Dropdown(
            id="stage-filter",
            options=[{"label": s.title(), "value": s} for s in STAGES],
            value=STAGES, multi=True, className="mb-2",
        ),
        html.Div("Status filter (ANY of)", className="text-muted small"),
        dcc.Dropdown(
            id="status-filter",
            options=[{"label": s.title(), "value": s} for s in JOB_STATUS_ORDER],
            value=[], multi=True, placeholder="(none)",
        ),
        html.Div("Table groups per row", className="text-muted small mt-2"),
        dcc.Dropdown(
            id="table-groups",
            options=[{"label": str(n), "value": n} for n in (1,2,3,4)],
            value=1, clearable=False, style={"width":"120px"},
        ),
        html.Div("Chunks per line", className="text-muted small mt-2"),
        dcc.Dropdown(
            id="chunks-per-line",
            options=[{"label": str(n), "value": n} for n in (3,4,5,6,8,10)],
            value=5, clearable=False, style={"width":"120px"},
        ),
    ]),
    style={"margin":"0"}
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

# Side-by-side, no wrap
two_col_nowrap = html.Div([
    # Left fixed pane
    html.Div([controls_card, kpi_row_top, kpi_row_bottom, pies_block],
             style={"width": _px(MAX_LEFT_WIDTH), "minWidth": _px(MAX_LEFT_WIDTH),
                    "maxWidth": _px(MAX_LEFT_WIDTH), "flex":"0 0 auto"}),
    # Right growing pane (title + table inline)
    html.Div([
        html.Div([
            html.H4("Datasets", className="fw-semibold", style={"margin":"0","whiteSpace":"nowrap"}),
            html.Div(id="table-scroll", children=html.Div(id="table-container"),
                     style={"overflowX":"auto","flex":"1 1 auto","minWidth":"0","paddingLeft":"8px"})
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
    # 7 KPI
    Output("kpi-waiting","children"),
    Output("kpi-retrying","children"),
    Output("kpi-running","children"),
    Output("kpi-failed","children"),
    Output("kpi-overdue","children"),
    Output("kpi-manual","children"),
    Output("kpi-succeeded","children"),
    # dropdown options (owner/mode)
    Output("owner-filter","options"),
    Output("mode-filter","options"),
    # four pies
    Output("pie-stage","figure"),
    Output("pie-archive","figure"),
    Output("pie-enrich","figure"),
    Output("pie-consolidate","figure"),
    # table + now + interval
    Output("table-container","children"),
    Output("now-indicator","children"),
    Output("interval","interval"),
    # Inputs
    Input("interval","n_intervals"),
    Input("owner-filter","value"),
    Input("mode-filter","value"),
    Input("stage-filter","value"),
    Input("status-filter","value"),
    Input("table-groups","value"),
    Input("chunks-per-line","value"),
    State("interval","interval"),
)
def refresh(_n, owner_sel, mode_sel, stage_filter, status_filter, groups_per_row, chunks_per_line, cur_interval):
    interval_ms = int(cur_interval or REFRESH_MS)
    store = load_store()

    # KPIs (global)
    k = aggregate_counts(store)
    kpi_vals = [str(k[s]) for s in ["waiting","retrying","running","failed","overdue","manual","succeeded"]]

    # Filters
    owner_opts, mode_opts = list_filters(store)

    # Pies (owner/mode filtered)
    figs = []
    for stg in STAGES:
        c = filtered_stage_counts(store, owner_sel, mode_sel, stg)
        figs.append(pie_figure(stg.title(), c))

    # Table groups + component
    groups = gather_dataset_groups(store, owner_sel, mode_sel, stage_filter or [], status_filter or [])
    table_comp = build_table_component(groups, groups_per_row or 1, chunks_per_line or 5)

    now_local = datetime.now(_DEF_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    return (*kpi_vals, owner_opts, mode_opts, *figs, table_comp, f"Refreshed: {now_local}", interval_ms)

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)