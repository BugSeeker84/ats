"""Command-line interface: import / match / generate / list / profiles."""
import argparse
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .applications import (
    append_application,
    find_prior_applications,
    hash_jd,
    read_applications,
)
from .generate import run_generate, save_docs
from .importer import run_import
from .llm import get_usage
from .match import run_match
from .profiles import get_profile, load_profiles


def _color(code: str):
    def wrap(s: str) -> str:
        return f"\x1b[{code}m{s}\x1b[0m"

    return wrap


DIM = _color("2")
BOLD = _color("1")
GREEN = _color("32")
YELLOW = _color("33")
RED = _color("31")


def _read_clipboard() -> str:
    """Read the system clipboard (X11 xclip/xsel, or Wayland wl-paste)."""
    for cmd in (
        ["xclip", "-selection", "clipboard", "-o"],
        ["xsel", "--clipboard", "--output"],
        ["wl-paste", "--no-newline"],
    ):
        if shutil.which(cmd[0]):
            try:
                return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
            except subprocess.CalledProcessError:
                continue
    raise RuntimeError(
        "No clipboard tool found. Install one (GNOME/X11): sudo apt install xclip"
    )


def _notify(title: str, body: str) -> None:
    """Best-effort desktop notification (no-op if notify-send is missing)."""
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", title, body], check=False)
        except Exception:
            pass


def _open_path(path: str) -> None:
    """Best-effort open in the default app (no-op if xdg-open is missing)."""
    if shutil.which("xdg-open"):
        try:
            subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


def _read_jd(path_or_dash: str | None, text: str | None, clipboard: bool = False) -> str:
    if clipboard:
        jd = _read_clipboard().strip()
        if not jd:
            raise RuntimeError("Clipboard is empty — copy a JD first.")
        return jd
    if text:
        return text
    if not path_or_dash:
        raise RuntimeError('Provide a JD file path (or "-" for stdin), --text "...", or --clipboard.')
    if path_or_dash == "-":
        return sys.stdin.read()
    p = Path(path_or_dash)
    if not p.exists():
        raise RuntimeError(f"JD file not found: {path_or_dash}")
    return p.read_text(encoding="utf-8")


def _print_ranking(result: dict) -> None:
    jd = result["jd"]
    print()
    head = BOLD("JD: ") + f"{jd['role'] or '(role?)'} @ {jd['company'] or '(company?)'}"
    if jd.get("location"):
        head += DIM(f"  · {jd['location']}")
    if jd.get("salary"):
        head += DIM(f"  · {jd['salary']}")
    print(head)
    print()
    print(DIM("  rank  overall  industry  skill  location  profile"))
    for i, s in enumerate(result["ranked"]):
        star = GREEN(" ★") if s["id"] == result["recommended_id"] else "  "
        print(
            f"  {str(i + 1).rjust(2)}{star}  "
            f"{str(s['overall']).rjust(5)}  "
            f"{str(s['industry']).rjust(6)}  "
            f"{str(s['skill']).rjust(5)}  "
            f"{str(s['location']).rjust(6)}  "
            f"{BOLD(s['name'])} {DIM('(' + s['id'] + ')')}"
        )
        print(DIM("        " + s["reasoning"]))
    print()


def _print_usage() -> None:
    u = get_usage()
    if u["calls"] == 0:
        return
    cost = (u["input_tokens"] / 1e6) * config.PRICE_INPUT_PER_M + (
        u["output_tokens"] / 1e6
    ) * config.PRICE_OUTPUT_PER_M
    print(
        DIM(
            f"   Tokens: {u['input_tokens']:,} in / {u['output_tokens']:,} out "
            f"over {u['calls']} call(s) · est. cost ${cost:.4f}"
        )
    )


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _gateway_blocked(result: dict) -> bool:
    """basic_rule.md #4: skip JDs requiring clearance or onsite. Alerts and returns True."""
    g = result.get("gateway") or {}
    if not g.get("blocked"):
        return False
    jd = result["jd"]
    reason = g.get("reason") or "requires clearance or on-site work"
    print(
        RED(BOLD("⛔ JD SKIPPED"))
        + RED(f" — {jd.get('role', '')} @ {jd.get('company', '')}: {reason}")
    )
    print(DIM("   (basic_rule.md: ignore JDs that require a clearance or on-site/hybrid work.)"))
    return True


def cmd_import(args) -> None:
    print(DIM(f"Reading {args.file} and extracting profile…"))
    result = run_import(args.file, profile_id=args.id, force=args.force)
    print(GREEN("✓ Imported profile: ") + BOLD(result["id"]))
    print("   " + result["dir"] + "/profile.md")
    print("   " + result["dir"] + "/rules.md")
    print(
        DIM(
            "   Review both — especially target_industries and the starter rules — "
            "then it is ready to match."
        )
    )
    _print_usage()


def cmd_match(args) -> None:
    profiles = load_profiles()
    if not profiles:
        raise RuntimeError("No profiles found. Add folders under profiles/ (see profiles/_TEMPLATE).")
    jd = _read_jd(args.jd, args.text, args.clipboard)
    print(DIM(f"Matching against {len(profiles)} profile(s)…"))
    result = run_match(profiles, jd)
    if _gateway_blocked(result):
        _print_usage()
        return
    _print_ranking(result)
    rec = result["ranked"][0]["name"] if result["ranked"] else "(none)"
    print(
        GREEN("Recommended: ")
        + BOLD(rec)
        + DIM(f" — run: python -m ats generate <jd> --profile {result['recommended_id']}")
    )
    _print_usage()


def cmd_generate(args) -> None:
    profiles = load_profiles()
    if not profiles:
        raise RuntimeError("No profiles found. Add folders under profiles/ (see profiles/_TEMPLATE).")
    jd_text = _read_jd(args.jd, args.text, args.clipboard)

    print(DIM(f"Matching against {len(profiles)} profile(s)…"))
    result = run_match(profiles, jd_text)
    if _gateway_blocked(result):
        if args.notify:
            jd = result["jd"]
            _notify("ATS — JD skipped", f"{jd.get('role', '')} @ {jd.get('company', '')}")
        _print_usage()
        return
    _print_ranking(result)

    # Duplicate-application alert.
    jd_hash = hash_jd(jd_text)
    prior = find_prior_applications(result["jd"]["company"], result["jd"]["role"], jd_hash)
    if prior:
        print(
            RED(BOLD("⚠  ALREADY APPLIED"))
            + RED(f" — you applied to {result['jd']['role']} @ {result['jd']['company']} before:")
        )
        for p in prior:
            print(
                RED(
                    f"     · {p.get('date')} as {p.get('profile_name')} "
                    f"({p.get('profile_id')}) → {p.get('output_dir')}"
                )
            )
        print()
        # Non-interactive (hotkey) or unconfirmed: do NOT silently make a duplicate.
        if not args.force:
            if args.yes:
                msg = f"Already applied to {result['jd']['role']} @ {result['jd']['company']} — skipped."
                print(YELLOW(msg + " Re-run with --force to generate anyway."))
                if args.notify:
                    _notify("ATS — already applied", msg)
                _print_usage()
                return

    chosen_id = args.profile or result["recommended_id"]
    if not get_profile(chosen_id):
        raise RuntimeError(f"Unknown profile id: {chosen_id}")

    if not args.yes:
        chosen = get_profile(chosen_id)
        prompt = (
            (RED("Duplicate exists. ") if prior else "")
            + f"Generate resume + cover letter for {BOLD(chosen.meta['name'])} ({chosen_id})? "
            + DIM("[Y/n, or type another profile id] ")
        )
        answer = input(prompt).strip()
        low = answer.lower()
        if low in ("n", "no"):
            print(YELLOW("Aborted. Nothing generated."))
            return
        if answer and low not in ("y", "yes"):
            if get_profile(answer):
                chosen_id = answer
            else:
                print(YELLOW(f'Unknown profile id "{answer}" — aborting.'))
                return

    profile = get_profile(chosen_id)
    print(DIM(f'Generating with profile "{chosen_id}"…'))
    docs = run_generate(profile, jd_text, result["jd"])

    date_iso = _today()
    out_dir = save_docs(docs, chosen_id, result["jd"], date_iso)

    append_application(
        {
            "date": date_iso,
            "profile_id": chosen_id,
            "profile_name": profile.meta["name"],
            "company": result["jd"]["company"],
            "role": result["jd"]["role"],
            "salary": result["jd"].get("salary", ""),
            "location": result["jd"].get("location", ""),
            "jd_url": args.jd_url or "",
            "jd_hash": jd_hash,
            "output_dir": out_dir,
        }
    )

    resume_path = out_dir + "/resume.html"
    print()
    print(GREEN("✓ Generated:"))
    print("   " + resume_path)
    print("   " + out_dir + "/cover-letter.html")
    print(DIM("   Logged to data/applications.csv"))
    _print_usage()

    if args.notify:
        jd = result["jd"]
        _notify(
            "ATS — resume ready",
            f"{profile.meta['name']} → {jd.get('role', '')} @ {jd.get('company', '')}",
        )
    if args.open:
        _open_path(resume_path)


def cmd_list(args) -> None:
    apps = read_applications()
    if not apps:
        print(DIM("No applications logged yet."))
        return
    print(BOLD(f"\n{len(apps)} application(s):\n"))
    for a in apps:
        line = (
            f"  {a.get('date')}  {BOLD(a.get('role', ''))} @ {a.get('company', '')}"
            + DIM(f"  · {a.get('profile_name', '')} ({a.get('profile_id', '')})")
        )
        if a.get("salary"):
            line += DIM(f"  · {a.get('salary')}")
        print(line)
    print()


def cmd_profiles(args) -> None:
    profiles = load_profiles()
    if not profiles:
        print(DIM("No profiles found under profiles/."))
        return
    print(BOLD(f"\n{len(profiles)} profile(s):\n"))
    for p in profiles:
        m = p.meta
        line = f"  {BOLD(m['name'])} {DIM('(' + p.id + ')')}"
        if m.get("current_company"):
            line += f"  · {m['current_company']}"
        if m.get("location"):
            line += DIM(f"  · {m['location']}")
        if m.get("target_industries"):
            line += DIM(f"  · {', '.join(m['target_industries'])}")
        print(line)
    print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ats",
        description="Match a JD to the best-fit developer and generate tailored resume/cover-letter HTML.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_import = sub.add_parser("import", help="Convert a resume (pdf/docx/html/txt) into a profile")
    p_import.add_argument("file", help="Path to the resume file")
    p_import.add_argument("--id", help="Force the profile id (folder name)")
    p_import.add_argument("--force", action="store_true", help="Overwrite an existing profile")
    p_import.set_defaults(func=cmd_import)

    p_match = sub.add_parser("match", help="Rank all profiles for a JD (writes nothing)")
    p_match.add_argument("jd", nargs="?", help='JD file path, or "-" for stdin')
    p_match.add_argument("--text", help="Pass the JD inline instead of a file")
    p_match.add_argument("--clipboard", action="store_true", help="Read the JD from the clipboard")
    p_match.set_defaults(func=cmd_match)

    p_gen = sub.add_parser("generate", help="Match, confirm, then write resume + cover letter")
    p_gen.add_argument("jd", nargs="?", help='JD file path, or "-" for stdin')
    p_gen.add_argument("--text", help="Pass the JD inline instead of a file")
    p_gen.add_argument("--clipboard", action="store_true", help="Read the JD from the clipboard")
    p_gen.add_argument("--profile", help="Force a specific profile instead of the recommended one")
    p_gen.add_argument("--jd-url", dest="jd_url", help="Store the JD link in the log")
    p_gen.add_argument("--yes", action="store_true", help="Skip the confirmation prompt")
    p_gen.add_argument("--force", action="store_true", help="Generate even if already applied to this job")
    p_gen.add_argument("--open", action="store_true", help="Open the resume after generating")
    p_gen.add_argument("--notify", action="store_true", help="Send a desktop notification when done")
    p_gen.set_defaults(func=cmd_generate)

    p_list = sub.add_parser("list", help="Show the application log")
    p_list.set_defaults(func=cmd_list)

    p_profiles = sub.add_parser("profiles", help="List loaded developer profiles")
    p_profiles.set_defaults(func=cmd_profiles)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except KeyboardInterrupt:
        print(YELLOW("\nAborted."))
        return 130
    except Exception as err:  # noqa: BLE001 — top-level CLI handler
        status = getattr(err, "status_code", None)
        label = type(err).__name__ + (f" {status}" if status else "")
        print(RED(f"Error ({label}): ") + str(err), file=sys.stderr)
        if status in (429, 500, 502, 503, 504):
            print(DIM("   This looks transient — just run the command again."), file=sys.stderr)
        return 1
    return 0
