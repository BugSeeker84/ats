"""Rank developer profiles against a JD (industry-weighted)."""
import json

from . import config, llm
from .profiles import Profile, summarize_for_match

SYSTEM = """You are a senior technical recruiter at a software outsourcing firm.
You match a job description (JD) to the best-fit developer from a fixed roster.

The firm's rule of thumb: INDUSTRY MATCH matters most, then SKILL MATCH, then LOCATION.
Company prestige and raw years of experience carry little weight on their own - do NOT
reward a candidate just for big-name employers or a high year count. Only treat years as
relevant if the JD states a specific minimum requirement.
Skill / tech-stack overlap is a MINOR factor: the firm tailors each candidate's stack to
the JD, so do NOT heavily penalize a thin or mismatched stored stack - weigh industry/domain
fit far above it.

GATEWAY FILTER - also decide whether this JD should be skipped entirely:
- Set "blocked" true if the JD requires a security clearance / public trust, OR requires
  on-site, hybrid, in-person, or relocation work (i.e., it is NOT fully remote).
- A "must reside / be authorized to work in the US" line is normal and does NOT block.
- Otherwise "blocked" is false. Give a short "reason".

For each developer, judge three things on a 0-100 scale:
- industry: how well the developer's real industry experience matches the JD's industry/domain.
- skill: how well their primary skills + stack overlap the JD's required and preferred skills.
- location: how well their location fits the JD (remote-friendly JDs should score high for everyone; on-site JDs reward co-located candidates).

Be honest and discriminating - do not flatten everyone to similar scores.
Only reason from the data given; never invent experience a developer does not have.

Also extract JD metadata. If a field is absent, use an empty string (for salary) or your best inference from the text (company/role/location).

Respond with ONLY a JSON object of this exact shape:
{
  "jd": { "company": string, "role": string, "location": string, "salary": string },
  "gateway": { "blocked": boolean, "reason": string },
  "scores": [
    { "id": string, "industry": number, "skill": number, "location": number, "reasoning": string }
  ]
}
Include one scores entry for every developer id provided."""


def _clamp(n) -> int:
    try:
        n = round(float(n))
    except (TypeError, ValueError):
        n = 0
    return max(0, min(100, n))


def run_match(profiles: list[Profile], jd_text: str) -> dict:
    roster = [summarize_for_match(p) for p in profiles]
    user = (
        f"ROSTER (developers):\n{json.dumps(roster, indent=2)}\n\n"
        f'JOB DESCRIPTION:\n"""\n{jd_text}\n"""'
    )
    # temperature=0 → deterministic scoring, so the same JD selects the same candidate.
    text = llm.complete(config.MATCH_MODEL, SYSTEM, user, temperature=0)
    raw = llm.extract_json(text)

    w = config.weights()
    by_id = {p.id: p for p in profiles}

    ranked = []
    for s in raw.get("scores", []):
        if s.get("id") not in by_id:
            continue
        industry = _clamp(s.get("industry"))
        skill = _clamp(s.get("skill"))
        location = _clamp(s.get("location"))
        overall = round(
            industry * w["industry"] + skill * w["skill"] + location * w["location"]
        )
        ranked.append(
            {
                "id": s["id"],
                "name": by_id[s["id"]].meta["name"],
                "industry": industry,
                "skill": skill,
                "location": location,
                "overall": overall,
                "reasoning": str(s.get("reasoning", "")),
            }
        )

    ranked.sort(key=lambda x: x["overall"], reverse=True)
    jd = raw.get("jd", {}) or {}
    gateway = raw.get("gateway", {}) or {}
    return {
        "jd": {
            "company": jd.get("company", ""),
            "role": jd.get("role", ""),
            "location": jd.get("location", ""),
            "salary": jd.get("salary", ""),
        },
        "gateway": {
            "blocked": bool(gateway.get("blocked")),
            "reason": str(gateway.get("reason", "")),
        },
        "ranked": ranked,
        "recommended_id": ranked[0]["id"] if ranked else "",
    }
