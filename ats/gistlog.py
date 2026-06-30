"""Optional GitHub Gist backend for the application log (no S3 needed).

When GIST_TOKEN + GIST_ID are set, applications.csv is read from / written to a
(private) gist via the GitHub API on each generation, so the apply history survives
Render's ephemeral disk. Persists the LOG only — generated PDFs stay local/ephemeral.

Token: a GitHub PAT with the "gist" scope (classic) or Gists read+write (fine-grained).
Create an (empty) private gist first; its id goes in GIST_ID.
"""
import json
import os
import urllib.request

_TOKEN = os.getenv("GIST_TOKEN", "").strip()
_GIST_ID = os.getenv("GIST_ID", "").strip()
_FILENAME = os.getenv("GIST_FILENAME", "applications.csv").strip() or "applications.csv"
# Overridable for GitHub Enterprise or local testing; defaults to public GitHub.
_API_BASE = os.getenv("GIST_API_BASE", "https://api.github.com").rstrip("/")


def enabled() -> bool:
    return bool(_TOKEN and _GIST_ID)


def _request(method: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(f"{_API_BASE}/gists/{_GIST_ID}", data=data, method=method)
    req.add_header("Authorization", f"Bearer {_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "ats-bidder")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def read_text() -> str | None:
    """Return the gist file's content, or None if the gist exists but has no such file yet.

    Raises on a real API error (bad token/id, network) so callers don't silently
    overwrite the log from an empty read. read_applications() tolerates the raise.
    """
    payload = _request("GET")
    file = (payload.get("files") or {}).get(_FILENAME)
    if not file:
        return None
    # The log is tiny and never truncated; honor raw_url defensively if it ever is.
    if file.get("truncated") and file.get("raw_url"):
        with urllib.request.urlopen(file["raw_url"], timeout=15) as r:
            return r.read().decode("utf-8")
    return file.get("content")


def write_text(text: str) -> None:
    """Create/update the log file in the gist (one small commit). Raises on auth/API error."""
    _request("PATCH", {"files": {_FILENAME: {"content": text}}})
