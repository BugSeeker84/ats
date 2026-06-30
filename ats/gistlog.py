"""Optional GitHub Gist backend for the application log (no S3 needed).

When GIST_TOKEN + GIST_ID are set, applications.csv is read from / written to a
(private) gist via the GitHub API on each generation, so the apply history survives
Render's ephemeral disk. Persists the LOG only — generated PDFs stay local/ephemeral.

Token: a GitHub PAT with the "gist" scope (classic) or Gists read+write (fine-grained).
Create an (empty) private gist first; its id goes in GIST_ID.
"""
import json
import os
import urllib.error
import urllib.request


def _clean_gist_id(raw: str) -> str:
    """Tolerate common paste mistakes: full gist URL, the 'gist:<id>' title form, slashes."""
    gid = (raw or "").strip().strip("/")
    if "/" in gid:                       # pasted the whole URL -> keep the last segment
        gid = gid.rsplit("/", 1)[-1]
    if gid.startswith("gist:"):          # pasted the page-title form "gist:<id>"
        gid = gid[len("gist:"):]
    # A gist id may carry a "<user>/<hash>" form in some copies; keep just the hash.
    return gid.split("#", 1)[0].strip()


_TOKEN = os.getenv("GIST_TOKEN", "").strip()
_GIST_ID = _clean_gist_id(os.getenv("GIST_ID", ""))
_FILENAME = os.getenv("GIST_FILENAME", "applications.csv").strip() or "applications.csv"
# Overridable for GitHub Enterprise or local testing; defaults to public GitHub.
_API_BASE = os.getenv("GIST_API_BASE", "https://api.github.com").rstrip("/")

# Actionable hints mapped from GitHub's API status codes (the raw 404 is useless on its own).
_ERR_HINTS = {
    401: "GIST_TOKEN is invalid or expired.",
    403: "GIST_TOKEN is missing the 'gist' scope (classic PAT) or lacks write access.",
    404: ("gist not found — verify GIST_ID is the BARE hash (no 'gist:' prefix / URL), and "
          "that GIST_TOKEN belongs to the account that OWNS this gist (secret gists are "
          "owner-only via the API)."),
}


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
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        hint = _ERR_HINTS.get(err.code, "")
        raise RuntimeError(
            f"GitHub gist API returned {err.code} for gist '{_GIST_ID}'. {hint}".strip()
        ) from err


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
