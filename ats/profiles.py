"""Load developer profiles from profiles/<id>/ folders."""
from dataclasses import dataclass

import frontmatter

from . import config


@dataclass
class Profile:
    id: str
    meta: dict
    profile_body: str  # full body of profile.md (generation source)
    prompt: str  # prompt.md — this dev's resume/cover-letter + tailoring prompt
    template: str | None = None  # optional template.html


def _as_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value]
    if isinstance(value, str):
        return [s.strip() for s in value.split(",") if s.strip()]
    return []


def _coerce_meta(pid: str, data: dict) -> dict:
    return {
        "name": data.get("name") or pid,
        "current_company": data.get("current_company"),
        "location": data.get("location"),
        "years_experience": data.get("years_experience"),
        "target_industries": _as_list(data.get("target_industries")),
        "primary_skills": _as_list(data.get("primary_skills")),
        "summary": data.get("summary"),
        "contact": data.get("contact") if isinstance(data.get("contact"), dict) else {},
    }


def load_profiles() -> list[Profile]:
    """Every profile folder under profiles/ (ignores names starting with '_')."""
    if not config.PROFILES_DIR.exists():
        return []
    profiles: list[Profile] = []
    for d in sorted(config.PROFILES_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        profile_md = d / "profile.md"
        if not profile_md.exists():
            continue
        post = frontmatter.load(profile_md)
        # The resume prompt lives in prompt.md (older profiles may still use rules.md).
        prompt_file = d / "prompt.md"
        if not prompt_file.exists():
            prompt_file = d / "rules.md"
        template_file = d / "template.html"
        profiles.append(
            Profile(
                id=d.name,
                meta=_coerce_meta(d.name, post.metadata),
                profile_body=post.content.strip(),
                prompt=prompt_file.read_text(encoding="utf-8").strip()
                if prompt_file.exists()
                else "",
                template=template_file.read_text(encoding="utf-8").strip()
                if template_file.exists()
                else None,
            )
        )
    return profiles


def get_profile(pid: str) -> Profile | None:
    return next((p for p in load_profiles() if p.id == pid), None)


def summarize_for_match(p: Profile) -> dict:
    """What the matcher sees: structured fields + the full experience body.

    Deliberately excludes the build rules (rules.md / basic_rule.md) — selection
    is based on who the candidate is, not how their resume would be styled.
    """
    m = p.meta
    return {
        "id": p.id,
        "name": m["name"],
        "current_company": m.get("current_company"),
        "location": m.get("location"),
        "years_experience": m.get("years_experience"),
        "target_industries": m.get("target_industries") or [],
        "primary_skills": m.get("primary_skills") or [],
        "summary": m.get("summary"),
        "experience": p.profile_body,
    }
