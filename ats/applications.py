"""Application log (CSV) + duplicate-application detection."""
import csv

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
    "output_dir",
]


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


def find_prior_applications(company: str, role: str) -> list[dict]:
    """Prior applications to the same company + role (case/space-insensitive).

    Powers the "you already applied for this job" alert.
    """
    c, r = _norm(company), _norm(role)
    return [
        a
        for a in read_applications()
        if _norm(a.get("company", "")) == c and _norm(a.get("role", "")) == r
    ]
