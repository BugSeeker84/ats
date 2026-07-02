"""FastAPI backend: bidders paste a JD and get a tailored resume + cover letter.

The LLM API key stays server-side. Access is gated by a shared token (ACCESS_TOKEN in
.env). Generation is serialized with a lock so concurrent bids don't clash on the browser
or the CSV log. Run with:

    uvicorn backend.app:app --host 0.0.0.0 --port 8000
"""
import os
import sys
import threading
import traceback
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ats import config
from ats.applications import read_applications
from ats.pipeline import process_jd
from ats.profiles import load_profiles

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if not ACCESS_TOKEN:
    print(
        "WARNING: ACCESS_TOKEN is not set — the platform is OPEN (no auth). "
        "Set ACCESS_TOKEN in .env (or the environment) before exposing it publicly.",
        file=sys.stderr,
    )

app = FastAPI(title="ATS Bidder Platform")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # gated by token anyway; tighten if you split frontend hosting
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serialize generation: Playwright + the CSV append are not safe to run concurrently.
_lock = threading.Lock()


def require_auth(x_access_token: str = Header(default="")) -> bool:
    if ACCESS_TOKEN and x_access_token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing access token.")
    return True


class BidIn(BaseModel):
    jd_text: str
    jd_link: str | None = None
    profile_id: str | None = None
    force: bool = False


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "auth_required": bool(ACCESS_TOKEN)}


@app.post("/api/bid")
def bid(body: BidIn, _: bool = Depends(require_auth)) -> dict:
    if not (body.jd_text or "").strip():
        raise HTTPException(status_code=400, detail="JD text is empty.")
    try:
        with _lock:
            return process_jd(
                body.jd_text,
                profile_id=body.profile_id,
                force=body.force,
                jd_link=body.jd_link or "",
            )
    except HTTPException:
        raise
    except Exception as err:
        # Full traceback to the server logs; concise cause back to the UI so a failed
        # generation isn't an opaque blank 500.
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Generation failed — {type(err).__name__}: {err}")


@app.get("/api/applications")
def applications(_: bool = Depends(require_auth)) -> list[dict]:
    # Newest first (LIFO): #3, #2, #1 …
    return sorted(read_applications(), key=lambda a: int(a.get("number") or 0), reverse=True)


@app.get("/api/profiles")
def profiles(_: bool = Depends(require_auth)) -> list[dict]:
    return [
        {
            "id": p.id,
            "name": p.meta["name"],
            "current_company": p.meta.get("current_company"),
            "industries": p.meta.get("target_industries") or [],
        }
        for p in load_profiles()
    ]


@app.get("/api/files/{folder}/{filename}")
def get_file(folder: str, filename: str, _: bool = Depends(require_auth)) -> FileResponse:
    root = config.OUTPUT_DIR.resolve()
    path = (root / folder / filename).resolve()
    if root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(str(path), filename=filename)


# Serve the static frontend at "/" (defined after the API routes so /api/* wins).
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")