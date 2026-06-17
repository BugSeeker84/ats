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

## Profiles (the seed data)

Each developer is a folder under `profiles/<id>/`:

```
profiles/
  aws-senior/
    profile.md      # frontmatter (matcher fields) + full real experience (generator source)
    rules.md        # this dev's resume/cover-letter + tailoring rules
    template.html   # OPTIONAL: an HTML skeleton/style to match
```

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
output/<date>_<company>_<role>_<profile>/resume.html
output/<date>_<company>_<role>_<profile>/cover-letter.html
```

and appends a row to `data/applications.csv`. Each run also prints token usage and an
estimated cost.

## One-key flow (copy JD → hotkey → done)

Read the JD straight from the clipboard, auto-pick the best candidate, generate, open the
resume, and post a desktop notification:

```bash
ats generate --clipboard --yes --open --notify
```

A ready-made launcher is installed at `~/.local/bin/ats-clip` that runs exactly this.

**Requirements (one-time):**

```bash
sudo apt install xclip      # clipboard reader (GNOME/X11); use wl-clipboard on Wayland
```

**Bind it to Ctrl+1 (GNOME):** Settings → Keyboard → View and Customize Shortcuts →
Custom Shortcuts → **+**, then:
- Name: `ATS Resume`
- Command: `/home/phoenix/.local/bin/ats-clip`
- Shortcut: `Ctrl+1`

Now: copy a job description anywhere, press **Ctrl+1**, and the tailored resume opens with
a notification. (Selection sends each candidate's full profile but never their build rules;
generation then applies the rules to the winner.)

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
