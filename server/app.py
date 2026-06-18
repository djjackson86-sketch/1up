from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

TURSO_URL = os.environ.get("TURSO_DATABASE_URL", "")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "") or os.environ.get("TURSO_TOKEN", "")
if TURSO_URL.startswith("libsql://"):
    TURSO_URL = TURSO_URL.replace("libsql://", "https://", 1).rstrip("/") + "/v2/pipeline"
if not TURSO_URL:
    raise RuntimeError("TURSO_DATABASE_URL environment variable not set")
if not TURSO_TOKEN:
    raise RuntimeError("TURSO_AUTH_TOKEN environment variable not set")


def params_to_turso_args(params):
    args = []
    for value in params or []:
        if value is None:
            args.append({"type": "null", "value": None})
        elif isinstance(value, bool):
            args.append({"type": "integer", "value": "1" if value else "0"})
        elif isinstance(value, int):
            args.append({"type": "integer", "value": str(value)})
        elif isinstance(value, float):
            args.append({"type": "float", "value": value})
        else:
            args.append({"type": "text", "value": str(value)})
    return args


def coerce_cell(cell):
    if not isinstance(cell, dict):
        return cell
    if cell.get("type") == "null":
        return None
    value = cell.get("value")
    typ = cell.get("type")
    if typ == "integer":
        try:
            return int(value)
        except Exception:
            return value
    if typ == "float":
        try:
            return float(value)
        except Exception:
            return value
    return value


def result_to_rows(result):
    cols = result.get("cols", []) or []
    out = []
    for row in result.get("rows", []) or []:
        obj = {}
        for index, col in enumerate(cols):
            name = col.get("name", f"col{index}") if isinstance(col, dict) else f"col{index}"
            cell = row[index] if index < len(row) else {"type": "null", "value": None}
            obj[name] = coerce_cell(cell)
        out.append(obj)
    return out


def turso_exec(sql, params=None):
    stmt = {"sql": sql}
    args = params_to_turso_args(params or [])
    if args:
        stmt["args"] = args
    body = json.dumps({"requests": [{"type": "execute", "stmt": stmt}]}).encode()
    req = Request(
        TURSO_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {TURSO_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.load(resp)
    except HTTPError as e:
        error_body = e.read().decode("utf-8", "ignore")
        raise RuntimeError(f"Turso HTTP error {e.code}: {error_body}") from e
    result_item = (data.get("results") or [{}])[0]
    if result_item.get("type") != "ok":
        raise RuntimeError(f"Turso error: {result_item}")
    result = result_item.get("response", {}).get("result", {})
    return {
        "ok": True,
        "rows": result_to_rows(result),
        "row_count": len(result.get("rows", []) or []),
        "affected_row_count": result.get("affected_row_count", 0),
        "last_insert_rowid": result.get("last_insert_rowid"),
        "query_duration_ms": result.get("query_duration_ms"),
    }


@app.get("/")
async def root():
    return {"ok": True, "message": "1up Turso proxy"}


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/api/query")
async def query(payload: dict):
    sql = payload.get("sql")
    params = payload.get("params", [])
    if not sql:
        return {"ok": False, "error": "Missing sql"}
    try:
        return turso_exec(sql, params)
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/run")
async def run_stmt(payload: dict):
    sql = payload.get("sql")
    params = payload.get("params", [])
    if not sql:
        return {"ok": False, "error": "Missing sql"}
    try:
        return turso_exec(sql, params)
    except Exception as e:
        return {"ok": False, "error": str(e)}
