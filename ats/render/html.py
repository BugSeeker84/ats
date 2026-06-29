"""Render validated content (ats.schema) into HTML via Jinja templates.

All styling lives in the templates, so the LLM never controls layout. Bullet strings
may use **double asterisks** for bold; everything else is HTML-escaped.
"""
import html
import re

from jinja2 import Environment
from markupsafe import Markup

from .. import config

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _mdbold(text: str) -> Markup:
    """Escape HTML, then turn **bold** into <strong>bold</strong> (safe markup)."""
    escaped = html.escape(text or "")
    return Markup(_BOLD_RE.sub(r"<strong>\1</strong>", escaped))


# autoescape=True: every {{ var }} is escaped unless explicitly marked safe (via mdbold).
_env = Environment(autoescape=True, trim_blocks=True, lstrip_blocks=True)
_env.filters["mdbold"] = _mdbold


def _default(name: str) -> str:
    return (config.TEMPLATES_DIR / name).read_text(encoding="utf-8")


def render_resume(template_str: str | None, name: str, contact: dict, resume) -> str:
    template = template_str or _default("base.html")
    # Pass the pydantic objects (not model_dump dicts): `group.items` must resolve to the
    # SkillGroup.items field, not dict.items (a builtin method) under Jinja attribute lookup.
    return _env.from_string(template).render(
        name=name,
        contact=contact,
        title=resume.title,
        summary=resume.summary,
        skills=resume.skills,
        experience=resume.experience,
        education=resume.education,
        certifications=resume.certifications,
    )


def render_cover_letter(name: str, title: str, contact: dict, jd: dict, cover) -> str:
    template = _default("cover-letter.html")
    return _env.from_string(template).render(
        name=name,
        title=title,
        contact=contact,
        company=jd.get("company", ""),
        role=jd.get("role", ""),
        greeting=cover.greeting,
        paragraphs=cover.paragraphs,
        closing=cover.closing,
    )
