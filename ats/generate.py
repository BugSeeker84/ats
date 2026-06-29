"""Generate a tailored resume + cover letter for a chosen profile.

The model returns ONLY validated JSON content (ats.schema.GeneratedContent); we render
that into HTML with the profile's Jinja template. The model never emits layout, so the
styling is deterministic and cannot drift between runs.
"""
import re

from . import config, llm
from .profiles import Profile
from .render.html import render_cover_letter, render_resume
from .rules import check_resume
from .schema import GeneratedContent

# Default re-prompt rounds to fix rule violations. 0 = one LLM call per resume (cheapest);
# rule checks still run and are reported as warnings. Raise via `ats generate --fix`.
DEFAULT_FIX_ATTEMPTS = 0

SYSTEM = """You are an expert resume and cover-letter writer for senior software engineers.
You return STRUCTURED JSON only — never HTML, never any prose outside the JSON.

Return EXACTLY one JSON object of this shape (no comments, no trailing commas):
{
  "resume": {
    "title": "JD-aligned positioning title, e.g. 'Senior Backend Engineer'",
    "summary": "2-3 sentence professional summary; lead with a noun phrase, no first-person 'I'",
    "skills": [ { "category": "Languages", "items": ["..."] } ],
    "experience": [
      { "title": "<copied verbatim from the profile>",
        "company": "<copied verbatim from the profile>",
        "dates": "<copied verbatim from the profile>",
        "bullets": ["achievement-first bullet", "..."] }
    ],
    "education": [ { "degree": "...", "school": "...", "dates": "..." } ],
    "certifications": [ { "name": "...", "issuer": "...", "year": "..." } ]
  },
  "cover_letter": { "paragraphs": ["body paragraph 1", "body paragraph 2", "body paragraph 3"] }
}

Hard rules:
- Use ONLY the developer's real companies, titles, and dates from the PROFILE — copy them
  verbatim into experience[].title/company/dates, most recent first. Never invent or alter
  employers, titles, or dates.
- Tailor by WRITING the bullets, summary, and skills toward the JD. Do not fabricate degrees.
- Follow the developer's RESUME PROMPT and the COMPANY-WIDE RULES for tone and emphasis.
- In bullets and cover-letter paragraphs, wrap key technologies in **double asterisks** for
  bold (e.g. **Kubernetes**). Use no other markup — no HTML.
- cover_letter.paragraphs are BODY paragraphs only — do NOT include a salutation
  ("Dear ...") or a sign-off ("Sincerely", your name). The template adds those.
- Return valid JSON only.

Bullet requirements (MANDATORY — get these right the first time, there is no second pass):
- Bullets per company BY RECENCY: 1st/most-recent company 6-7 bullets, 2nd 5-6, 3rd 4-5,
  and EVERY remaining company exactly 4. Count them before you answer.
- EVERY experience bullet must be at least 20 words.
- EVERY experience bullet must bold at least one key technology with **double asterisks**.
(Unless the developer's RESUME PROMPT specifies different counts — then follow the prompt.)"""


def run_generate(profile: Profile, jd_text: str, jd: dict, fix_attempts: int = DEFAULT_FIX_ATTEMPTS) -> dict:
    prompt = profile.prompt or "(no explicit prompt provided - use clean, ATS-friendly defaults)"
    global_rules = config.global_rules()
    global_block = (
        f'COMPANY-WIDE RULES (apply to every profile; the developer\'s own prompt takes precedence on conflict):\n"""\n{global_rules}\n"""\n\n'
        if global_rules
        else ""
    )
    user = f"""DEVELOPER PROFILE (id: {profile.id}, name: {profile.meta['name']})
\"\"\"
{profile.profile_body}
\"\"\"

{global_block}RESUME PROMPT (this developer's own resume/cover-letter + tailoring instructions):
\"\"\"
{prompt}
\"\"\"

TARGET JOB - {jd.get('role') or 'role'} at {jd.get('company') or 'company'}:
\"\"\"
{jd_text}
\"\"\"

Return the resume + cover letter as the specified JSON now."""

    content, issues = _generate_validated(user, fix_attempts)

    contact = _contact(profile)
    name = profile.meta["name"]
    title = content.resume.title or profile.meta.get("summary") or name
    return {
        "resume_html": render_resume(profile.template, name, contact, content.resume),
        "cover_letter_html": render_cover_letter(name, title, contact, jd, content.cover_letter),
        "content": content,
        "issues": issues,
    }


def _generate_validated(user: str, fix_attempts: int) -> tuple[GeneratedContent, list[str]]:
    """Generate once, then optionally re-prompt up to `fix_attempts` times to fix
    deterministic rule violations. With fix_attempts=0 it's a single call and any
    violations are returned as warnings (no extra calls).

    Returns the content plus any rule issues that still remained.
    """
    content = llm.complete_structured(config.GENERATE_MODEL, SYSTEM, user, GeneratedContent)
    issues = check_resume(content.resume)
    for _ in range(fix_attempts):
        if not issues:
            return content, []
        fix_user = (
            user
            + "\n\nYour previous JSON broke these REQUIRED rules:\n"
            + "\n".join("- " + i for i in issues)
            + "\n\nReturn the FULL corrected JSON, fixing every issue above. "
            "Keep all companies, titles, and dates identical."
        )
        content = llm.complete_structured(
            config.GENERATE_MODEL, SYSTEM, fix_user, GeneratedContent
        )
        issues = check_resume(content.resume)
    return content, issues


def _contact(profile: Profile) -> dict:
    """Contact block for the templates — fixed profile data, never LLM-generated."""
    contact = dict(profile.meta.get("contact") or {})
    contact.setdefault("location", profile.meta.get("location") or "")
    return contact


def _fs_safe(s: str) -> str:
    """A readable, filesystem-safe folder name (keeps spaces, strips illegal chars)."""
    s = re.sub(r'[\\/:*?"<>|]+', " ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s or "untitled"


def _compact(s: str) -> str:
    """Compact name for filenames: 'Gavin Li' -> 'GavinLi'."""
    return "".join(re.findall(r"[A-Za-z0-9]+", s or "")) or "Resume"


def _unique_dir(path):
    """Return path, or path (2), path (3)… if it already exists."""
    if not path.exists():
        return path
    i = 2
    while (cand := path.with_name(f"{path.name} ({i})")).exists():
        i += 1
    return cand


def save_docs(docs: dict, profile, jd: dict, jd_text: str, pdf: bool = True) -> dict:
    """Write resume + cover letter (HTML + PDF) and the JD into `output/<Company> - <Name>/`.

    Returns a dict of string paths: dir, resume_html, cover_html, resume_pdf, cover_pdf,
    jd. The *_pdf values are None if PDF rendering is skipped or unavailable.
    """
    company = _fs_safe(jd.get("company") or "Company")
    name = profile.meta.get("name") or profile.id
    folder = _unique_dir(config.OUTPUT_DIR / _fs_safe(f"{company} - {name}"))
    folder.mkdir(parents=True, exist_ok=True)

    stem = _compact(name)
    resume_html = folder / f"{stem}_Resume.html"
    cover_html = folder / f"{stem}_CoverLetter.html"
    resume_html.write_text(docs["resume_html"], encoding="utf-8")
    cover_html.write_text(docs["cover_letter_html"], encoding="utf-8")
    jd_path = folder / "JD.txt"
    jd_path.write_text(jd_text or "", encoding="utf-8")

    out = {
        "dir": str(folder),
        "resume_html": str(resume_html),
        "cover_html": str(cover_html),
        "jd": str(jd_path),
        "resume_pdf": None,
        "cover_pdf": None,
    }

    if pdf:
        from .render.pdf import PdfUnavailable, html_to_pdfs

        resume_pdf = folder / f"{stem}_Resume.pdf"
        cover_pdf = folder / f"{stem}_CoverLetter.pdf"
        try:
            html_to_pdfs(
                [
                    (docs["resume_html"], resume_pdf),
                    (docs["cover_letter_html"], cover_pdf),
                ]
            )
            out["resume_pdf"] = str(resume_pdf)
            out["cover_pdf"] = str(cover_pdf)
        except PdfUnavailable as err:
            out["pdf_error"] = str(err)

    return out
