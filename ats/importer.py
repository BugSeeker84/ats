"""Convert an existing resume file into a profiles/<id>/ seed (profile.md + rules.md).

The default model is text-only, so PDF/DOCX text is extracted locally before sending.
"""
import re
from pathlib import Path

from . import config, llm

PROFILE_DELIM = "===PROFILE_MD==="
RULES_DELIM = "===RULES_MD==="

SYSTEM = f"""You convert a developer's existing resume (provided as text) into seed files for an internal resume-build tool.

You output TWO documents.

(1) profile.md - must begin with a YAML frontmatter block of EXACTLY these keys, then the full resume content as Markdown below it:
---
name: <full name>
current_company: <current or most recent employer>
location: <city, region - include "(Remote)" if stated>
years_experience: <integer, inferred from earliest role to present>
target_industries: [<the real domains this person has shipped in, e.g. Retail, Fintech, Cloud>]
primary_skills: [<the headline skills/stack>]
summary: <one sentence>
contact:
  email: <or omit if unknown>
  phone: <or omit>
  linkedin: <or omit>
  github: <or omit>
---
## Summary
...full experience, skills, education, certifications as Markdown...

(2) rules.md - a sensible STARTER set of resume/cover-letter build rules for this person
(length, section order, tone, ATS-friendliness, styling). Add a top line noting it is a
starter the user should review and edit.

Hard rules:
- Use ONLY facts present in the resume text. Never invent employers, dates, titles, metrics, or skills.
- Infer target_industries from the companies/domains actually in the resume.
- Keep frontmatter valid YAML; use [a, b] inline lists; quote phone numbers.

Output EXACTLY this, nothing before/between/after:
{PROFILE_DELIM}
<profile.md content>
{RULES_DELIM}
<rules.md content>"""

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
_TEXT_EXTS = {".html", ".htm", ".txt", ".md"}


def _extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
        if not text:
            raise RuntimeError(
                "No text found in PDF (it may be a scanned image). "
                "Export a text-based PDF, or paste the resume as .txt."
            )
        return text
    if ext == ".docx":
        import docx

        doc = docx.Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    if ext in _TEXT_EXTS:
        return path.read_text(encoding="utf-8")
    if ext in _IMAGE_EXTS:
        raise RuntimeError(
            f"Image resumes ({ext}) need a vision model. "
            "Convert to a text-based PDF/DOCX, or paste as .txt."
        )
    raise RuntimeError(f'Unsupported resume type "{ext}". Use pdf, docx, html, txt, or md.')


def split_seed(text: str) -> tuple[str, str]:
    pi = text.find(PROFILE_DELIM)
    ri = text.find(RULES_DELIM)
    if pi == -1 or ri == -1 or ri < pi:
        raise ValueError("Could not parse import output (missing delimiters). Raw:\n" + text)
    profile_md = text[pi + len(PROFILE_DELIM) : ri].strip() + "\n"
    rules_md = text[ri + len(RULES_DELIM) :].strip() + "\n"
    return profile_md, rules_md


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "developer").lower()).strip("-")[:40]
    return s or "developer"


def run_import(file: str, profile_id: str | None = None, force: bool = False) -> dict:
    path = Path(file)
    if not path.exists():
        raise RuntimeError(f"Resume file not found: {file}")
    resume_text = _extract_text(path)
    user = (
        "Convert this resume into profile.md and rules.md as specified.\n\n"
        f'RESUME:\n"""\n{resume_text}\n"""'
    )
    out = llm.complete(config.IMPORT_MODEL, SYSTEM, user)
    profile_md, rules_md = split_seed(out)

    pid = profile_id
    if not pid:
        m = re.search(r"^\s*name:\s*(.+)$", profile_md, re.MULTILINE)
        pid = _slug(m.group(1) if m else path.stem)

    d = config.PROFILES_DIR / pid
    profile_path = d / "profile.md"
    if profile_path.exists() and not force:
        raise RuntimeError(
            f'Profile "{pid}" already exists. Use --id <other> or --force to overwrite.'
        )
    d.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(profile_md, encoding="utf-8")
    (d / "rules.md").write_text(rules_md, encoding="utf-8")
    return {"id": pid, "dir": str(d)}
