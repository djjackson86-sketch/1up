from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import os

app = FastAPI()

# CORS settings: allow all origins for simplicity; adjust as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your GitHub Pages domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TURSO_URL = os.environ.get("TURSO_DATABASE_URL")
if not TURSO_URL:
    raise RuntimeError("TURSO_DATABASE_URL environment variable not set")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")
if TURSO_URL.startswith("libsql://") and not TURSO_TOKEN:
    raise RuntimeError("TURSO_AUTH_TOKEN environment variable not set for libSQL URL")

def turso_exec(sql, params=None):
    stmt = {"sql": sql}
    if params is not None:
        stmt["args"] = params  # plain array, not wrapped
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
        resp = urlopen(req, timeout=30)
        data = json.load(resp)
        return data.get("results", [{}])[0].get("response", {}).get("result", {})
    except HTTPError as e:
        # Read error body for debugging
        error_body = e.read().decode("utf-8", "ignore")
        raise RuntimeError(f"Turso HTTP error {e.code}: {error_body}") from e

@app.get("/")
async def root():
    return {"message": "Turso proxy for 1up app"}

@app.post("/api/query")
async def query(payload: dict):
    sql = payload.get("sql")
    params = payload.get("params", [])
    if not sql:
        return {"error": "Missing sql"}
    try:
        result = turso_exec(sql, params)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/run")
async def run_stmt(payload: dict):
    sql = payload.get("sql")
    params = payload.get("params", [])
    if not sql:
        return {"error": "Missing sql"}
    try:
        result = turso_exec(sql, params)
        return result
    except Exception as e:
        return {"error": str(e)}
