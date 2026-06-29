# ATS Resume Build

Internal AI tool (Python): paste a job description, find the best-fit developer from your
roster (industry match first, then skills, then location), and generate a tailored
**resume + cover letter as raw HTML** — following each developer's own build rules.
Every generation is logged to a CSV, and you get an alert if you already applied to the
same company + role.

Runs on any **OpenAI-compatible** endpoint; defaults to **Fireworks** (`gpt-oss-120b`).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env      # then paste your Fireworks key (LLM_API_KEY) into .env
```

Python 3.10+ required. After `pip install -e .` you can use either `ats <command>` or
`python -m ats <command>`.

## Project layout

```
ats/                  # Python package (the CLI + pipeline)
  render/             # JSON content -> HTML -> PDF (deterministic, no LLM)
profiles/<id>/        # one self-contained folder per developer (see below)
shared/basic_rule.md  # company-wide tailoring rules, layered under each dev's rules.md
templates/            # shared base resume/cover-letter templates
sample-jds/           # example job descriptions for testing
data/applications.csv # the application log
output/               # generated resumes + cover letters
```

## Profiles (the seed data)

Each developer is a self-contained folder under `profiles/<id>/`:

```
profiles/
  aws-senior/
    profile.md      # frontmatter (matcher fields) + full real experience (generator source)
    rules.md        # this dev's resume/cover-letter + tailoring rules
    template.html   # OPTIONAL: per-profile HTML/Jinja layout (overrides templates/)
    sources/        # OPTIONAL: original resume + hand-written prompt this profile came from
```

A folder is only loaded as a profile once it has a `profile.md`; folders with just
`sources/` are raw material waiting to be turned into a profile (via `ats import`).

The fastest way to create a profile is to **import an existing resume** — the tool reads
the file and drafts `profile.md` + a starter `rules.md` for you:

```bash
ats import resumes/jane-walmart.pdf            # pdf, docx, html, txt, md
ats import resumes/jane.docx --id walmart-jane # force the profile id
```

Text is extracted locally (PDF via `pypdf`, DOCX via `python-docx`) before being sent to
the model, so it works with text-only models like `gpt-oss-120b`. Scanned/image-only PDFs
and image files need a vision model — export a text-based PDF or paste as `.txt`. It uses
only what's in the resume (it won't invent experience), infers `target_industries` from
the real companies, and writes a starter `rules.md` you should review. Or copy
`profiles/_TEMPLATE/` and fill it in by hand. The `example-aws-senior` profile is
placeholder data — delete it once your real profiles are in.

## Commands

```bash
ats import   resume.pdf            # turn an existing resume into a profile
ats profiles                       # list loaded developers
ats match    jd.txt                # rank all profiles for a JD (writes nothing)
ats generate jd.txt                # match -> confirm -> write resume + cover letter, log it
ats generate jd.txt --profile aws-senior --jd-url https://...
ats list                           # show the application log
cat jd.txt | ats generate -        # JD from stdin
```

`generate` flow: it matches, shows the ranking + recommendation, **alerts if you've
already applied to that company + role**, asks you to confirm (or type a different profile
id), then writes:

```
output/<Company> - <Full Name>/<CompactName>_Resume.html   (+ .pdf)
output/<Company> - <Full Name>/<CompactName>_CoverLetter.html  (+ .pdf)
output/<Company> - <Full Name>/JD.txt
```

and appends a row to `output/applications.csv` (number, date, profile, company, job title,
salary). Each run also prints token usage and an estimated cost.

Per JD that's **two model calls**: one to score/select the candidate and extract the JD
fields, and one to generate the resume + cover letter as validated JSON (rendered to
HTML/PDF by code). Rule checks (bullet counts, ≥20-word bullets, bold keywords) run locally
and only warn; add `--fix` to auto-correct with extra calls.

## One-key flow (copy JD → hotkey → PDF opens)

Read the JD straight from the clipboard, auto-pick the best candidate, generate, open the
PDF, and post a desktop notification:

```
ats generate --clipboard --yes --open --notify
```

**Windows** — a ready-made launcher is at `scripts\ats-clip.cmd`. Bind it to a global
hotkey (creates a Start-Menu shortcut Windows registers):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup-hotkey.ps1                 # Ctrl+Alt+1
powershell -ExecutionPolicy Bypass -File scripts\setup-hotkey.ps1 -HotKey "CTRL+ALT+J"
```

Now copy a job description anywhere, press the hotkey, and the tailored PDF opens with a
notification. (Clipboard, open, and notify all work natively on Windows — no extra tools.)

**Linux/macOS** — `scripts/setup-hotkey.sh` binds a GNOME shortcut to a launcher; clipboard
needs `xclip` (X11) or `wl-clipboard` (Wayland), or `pbpaste` on macOS.

(Selection sends each candidate's profile but never their resume prompt; generation then
applies the prompt to the winner.)

## Configuration (`.env`)

| Variable           | Default                                   | Purpose                                  |
|--------------------|-------------------------------------------|------------------------------------------|
| `LLM_API_KEY`      | —                                         | Required (Fireworks key, `fw_...`).      |
| `LLM_BASE_URL`     | `https://api.fireworks.ai/inference/v1`   | OpenAI-compatible endpoint.              |
| `MATCH_MODEL`      | `accounts/fireworks/models/gpt-oss-120b`  | Model for ranking.                       |
| `GENERATE_MODEL`   | `accounts/fireworks/models/gpt-oss-120b`  | Model for document generation.           |
| `IMPORT_MODEL`     | `accounts/fireworks/models/gpt-oss-120b`  | Model for resume import.                 |
| `MAX_TOKENS`       | `8000`                                    | Max output tokens per call.              |
| `PRICE_INPUT_PER_M`| `0.15`                                    | $/1M input tokens (for the cost line).   |
| `PRICE_OUTPUT_PER_M`| `0.60`                                   | $/1M output tokens (for the cost line).  |
| `WEIGHT_INDUSTRY`  | `0.5`                                     | Industry weight (the rule of thumb).     |
| `WEIGHT_SKILL`     | `0.3`                                     | Skill weight.                            |
| `WEIGHT_LOCATION`  | `0.2`                                     | Location weight.                         |

Weights are normalized automatically; the overall score is computed locally from the
model's sub-scores so your weighting always wins.
