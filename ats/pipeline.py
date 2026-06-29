"""Reusable JD -> bid pipeline shared by the CLI and the web backend.

One function does the whole flow (match -> gateway -> dedup/auto-switch -> generate ->
save -> log) and returns a structured result, so the CLI and the API behave identically.
"""
from datetime import datetime, timezone
from pathlib import Path

from .applications import append_application, has_applied, hash_jd
from .generate import run_generate, save_docs
from .match import run_match
from .profiles import get_profile, load_profiles


def _today_short() -> str:
    return datetime.now(timezone.utc).strftime("%m-%d")


def process_jd(
    jd_text: str,
    profile_id: str | None = None,
    force: bool = False,
    pdf: bool = True,
    fix_attempts: int = 0,
) -> dict:
    """Run one JD end-to-end. Returns a dict with a 'status':

    - "generated": resume + cover written; includes profile, files, folder, ranking.
    - "skipped":   duplicate (same profile+company) and no alternative / forced.
    - "blocked":   gateway filter (clearance / on-site).
    - "error":     misconfiguration (no profiles, unknown id).
    """
    jd_text = (jd_text or "").strip()
    if not jd_text:
        return {"status": "error", "message": "JD text is empty."}

    profiles = load_profiles()
    if not profiles:
        return {"status": "error", "message": "No profiles configured on the server."}

    result = run_match(profiles, jd_text)
    jd = result["jd"]
    ranking = [
        {"id": s["id"], "name": s["name"], "overall": s["overall"], "industry": s["industry"]}
        for s in result["ranked"]
    ]

    if result["gateway"]["blocked"]:
        return {
            "status": "blocked",
            "jd": jd,
            "message": result["gateway"]["reason"] or "JD requires clearance or on-site work.",
            "ranking": ranking,
        }

    chosen_id = profile_id or result["recommended_id"]
    chosen = get_profile(chosen_id)
    if not chosen:
        return {"status": "error", "message": f"Unknown profile id: {chosen_id}"}

    company = jd["company"]
    forced_profile = bool(profile_id)
    switched_from = None

    # Avoid sending the SAME profile to the SAME company twice; auto-switch to next-best.
    if not force and has_applied(company, chosen.meta["name"]):
        if forced_profile:
            return {
                "status": "skipped",
                "jd": jd,
                "profile": chosen.meta["name"],
                "message": f"{chosen.meta['name']} already applied to {company} (use force to repeat).",
                "ranking": ranking,
            }
        alt = next((s for s in result["ranked"] if not has_applied(company, s["name"])), None)
        if alt:
            switched_from = chosen.meta["name"]
            chosen_id = alt["id"]
            chosen = get_profile(chosen_id)
        else:
            return {
                "status": "skipped",
                "jd": jd,
                "message": f"All candidates already applied to {company} — nothing generated.",
                "ranking": ranking,
            }

    docs = run_generate(chosen, jd_text, jd, fix_attempts=fix_attempts)
    out = save_docs(docs, chosen, jd, jd_text, pdf=pdf)
    row = append_application(
        {
            "date": _today_short(),
            "profile": chosen.meta["name"],
            "company": company,
            "job_title": jd["role"],
            "salary": jd.get("salary", ""),
            "folder": Path(out["dir"]).name,
            "jd_hash": hash_jd(jd_text),
        }
    )

    return {
        "status": "generated",
        "jd": jd,
        "profile": chosen.meta["name"],
        "profile_id": chosen_id,
        "switched_from": switched_from,
        "folder": Path(out["dir"]).name,
        "files": {k: (Path(v).name if v else None) for k, v in out.items() if k != "dir"},
        "issues": docs.get("issues") or [],
        "ranking": ranking,
        "row": row,
    }