"""Application log (CSV) + duplicate-application detection."""
import csv
import hashlib
import io
import sys

from . import config, gistlog

HEADER = [
    "number",     # running index, 1-based
    "date",       # MM-DD
    "profile",    # developer's display name
    "company",    # JD company
    "job_title",  # JD role
    "salary",     # JD salary range (blank if none stated)
    "jd_link",    # URL of the original job posting (optional)
    "folder",     # output subfolder name
    "jd_hash",    # for duplicate detection
]


def hash_jd(text: str) -> str:
    """Stable short hash of a JD's normalized text — catches the same JD even if the
    model extracts the company/role slightly differently between runs."""
    norm = " ".join((text or "").lower().split())
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]


def _rows_to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(HEADER)
    for r in rows:
        writer.writerow([r.get(k, "") for k in HEADER])
    return buf.getvalue()


def _parse_csv(text: str | None) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text))) if text else []


def _read_backend_text() -> str | None:
    """Raw CSV text from the active backend (gist > local file), or None if empty.

    Raises if the gist is unreachable/misconfigured — callers that rewrite the log
    rely on this so a failed read can't clobber it.
    """
    if gistlog.enabled():
        return gistlog.read_text()
    if not config.APPLICATIONS_CSV.exists():
        return None
    return config.APPLICATIONS_CSV.read_text(encoding="utf-8-sig")


def read_applications() -> list[dict]:
    # Tolerant: a broken/misconfigured external store must never break sign-in or the
    # applications table. Degrade to an empty list and surface the cause in the logs.
    try:
        return _parse_csv(_read_backend_text())
    except Exception as err:  # noqa: BLE001
        print(f"WARNING: could not read the application log: {err}", file=sys.stderr)
        return []


def append_application(app: dict) -> dict:
    """Append one row, assigning the next running number. Returns the stored row.

    Uses a strict read (raises on backend error) so a transient/misconfig failure
    can't clobber the stored log by rewriting it from an empty list. Generation is
    serialized by a lock upstream, so the read-modify-write is safe.
    """
    rows = _parse_csv(_read_backend_text())
    row = {**app, "number": len(rows) + 1}
    csv_text = _rows_to_csv([*rows, row])
    if gistlog.enabled():
        gistlog.write_text(csv_text)
    else:
        # Local file: rewrite the whole log (utf-8-sig BOM for Excel) so a schema change
        # (e.g. a new column) migrates existing rows instead of misaligning an append.
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        config.APPLICATIONS_CSV.write_text(csv_text, encoding="utf-8-sig")
    return row


def _norm(s: str) -> str:
    return " ".join((s or "").lower().split())


def find_prior_applications(company: str, profile_name: str) -> list[dict]:
    """Prior applications by the SAME profile to the SAME company — i.e. the output-folder
    identity (<Company> - <Name>). This is what we avoid repeating; different profiles may
    still apply to the same company.
    """
    c, p = _norm(company), _norm(profile_name)
    if not c or not p:
        return []
    return [
        a
        for a in read_applications()
        if _norm(a.get("company", "")) == c and _norm(a.get("profile", "")) == p
    ]


def has_applied(company: str, profile_name: str) -> bool:
    """True if this profile already has an application logged for this company."""
    return bool(find_prior_applications(company, profile_name))
