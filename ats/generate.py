"""Generate a tailored resume + cover letter as raw HTML for a chosen profile."""
import re

from . import config, llm
from .profiles import Profile

RESUME_DELIM = "===RESUME_HTML==="
COVER_DELIM = "===COVER_LETTER_HTML==="

SYSTEM = f"""You are an expert resume and cover-letter writer for senior software engineers.
You produce ATS-friendly, tailored documents as complete, standalone raw HTML.

Hard rules:
- Follow the developer's BUILD RULES exactly - they govern structure, tone, length, and styling.
- Never invent employers, dates, titles. You can only tailor skills and experience.
- Tailor by selecting, ordering, and emphasizing the developer's real experience toward the JD; surface the most JD-relevant work first.
- Each document must be a complete HTML document (<!doctype html> ... </html>) with self-contained inline CSS, ready to open in a browser or print to PDF.
- If a TEMPLATE is provided, match its structure and visual style.

Output format - return EXACTLY this, with no commentary before, between, or after:
{RESUME_DELIM}
<the full resume HTML>
{COVER_DELIM}
<the full cover letter HTML>"""


def run_generate(profile: Profile, jd_text: str, jd: dict) -> dict:
    template_block = (
        f'\nTEMPLATE (match this structure/style):\n"""\n{profile.template}\n"""\n'
        if profile.template
        else ""
    )
    rules = profile.rules or "(no explicit rules provided - use clean, modern, ATS-friendly defaults)"
    global_rules = config.global_rules()
    global_block = (
        f'COMPANY-WIDE RULES (apply to every profile; the developer\'s own rules below take precedence on conflict):\n"""\n{global_rules}\n"""\n\n'
        if global_rules
        else ""
    )
    user = f"""DEVELOPER PROFILE (id: {profile.id}, name: {profile.meta['name']})
\"\"\"
{profile.profile_body}
\"\"\"

{global_block}BUILD RULES (this developer's own resume/cover-letter + tailoring rules):
\"\"\"
{rules}
\"\"\"
{template_block}
TARGET JOB - {jd.get('role') or 'role'} at {jd.get('company') or 'company'}:
\"\"\"
{jd_text}
\"\"\"

Generate the tailored resume and cover letter now."""

    text = llm.complete(config.GENERATE_MODEL, SYSTEM, user)
    return split_docs(text)


def split_docs(text: str) -> dict:
    ri = text.find(RESUME_DELIM)
    ci = text.find(COVER_DELIM)
    if ri == -1 or ci == -1 or ci < ri:
        raise ValueError(
            "Could not parse the generated documents (missing delimiters). Raw output:\n" + text
        )
    resume = text[ri + len(RESUME_DELIM) : ci]
    cover = text[ci + len(COVER_DELIM) :]
    # Strip any stray/repeated delimiter tokens the model may have echoed back.
    for delim in (RESUME_DELIM, COVER_DELIM):
        resume = resume.replace(delim, "")
        cover = cover.replace(delim, "")
    return {"resume_html": resume.strip(), "cover_letter_html": cover.strip()}


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "untitled").lower()).strip("-")[:40]
    return s or "untitled"


def save_docs(docs: dict, profile_id: str, jd: dict, date_iso: str) -> str:
    """Write the two HTML files into a dated, descriptive output folder. Returns the dir."""
    folder = f"{date_iso}_{_slug(jd.get('company', ''))}_{_slug(jd.get('role', ''))}_{_slug(profile_id)}"
    d = config.OUTPUT_DIR / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / "resume.html").write_text(docs["resume_html"], encoding="utf-8")
    (d / "cover-letter.html").write_text(docs["cover_letter_html"], encoding="utf-8")
    return str(d)
