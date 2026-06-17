"""Application log (CSV) + duplicate-application detection."""
import csv
import hashlib

from . import config

HEADER = [
    "date",
    "profile_id",
    "profile_name",
    "company",
    "role",
    "salary",
    "location",
    "jd_url",
    "jd_hash",
    "output_dir",
]


def hash_jd(text: str) -> str:
    """Stable short hash of a JD's normalized text — catches the same JD even if the
    model extracts the company/role slightly differently between runs."""
    norm = " ".join((text or "").lower().split())
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]


def _ensure_file() -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not config.APPLICATIONS_CSV.exists():
        with config.APPLICATIONS_CSV.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADER)


def read_applications() -> list[dict]:
    if not config.APPLICATIONS_CSV.exists():
        return []
    with config.APPLICATIONS_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_application(app: dict) -> None:
    _ensure_file()
    with config.APPLICATIONS_CSV.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([app.get(k, "") for k in HEADER])


def _norm(s: str) -> str:
    return " ".join((s or "").lower().split())


def find_prior_applications(company: str, role: str, jd_hash: str = "") -> list[dict]:
    """Prior applications to the same job — matched by exact JD-hash OR by the same
    company + role (case/space-insensitive). Powers the "already applied" alert.
    """
    c, r = _norm(company), _norm(role)
    out = []
    for a in read_applications():
        same_jd = bool(jd_hash) and a.get("jd_hash", "") == jd_hash
        same_cr = bool(c) and bool(r) and _norm(a.get("company", "")) == c and _norm(a.get("role", "")) == r
        if same_jd or same_cr:
            out.append(a)
    return out
