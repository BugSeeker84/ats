"""Deterministic checks on generated resume content, with messages for re-prompting.

These enforce the parts of shared/basic_rule.md that can be verified in code, so they're
guaranteed rather than merely requested of the model:
  #6  each experience bullet has >= 20 words
  #7  each bullet bolds at least one keyword (**...**)
  #8  bullets per company by recency (current 6-7, 2nd 5-6, 3rd 4-5, rest 4)
"""
import re

_BOLD = re.compile(r"\*\*(.+?)\*\*")

MIN_WORDS = 20

# basic_rule.md #8 — (min, max) bullets per company by recency. Index 0 = most recent.
DEFAULT_BULLET_RANGES: list[tuple[int, int]] = [(6, 7), (5, 6), (4, 5)]
DEFAULT_TRAILING: tuple[int, int] = (4, 4)  # all remaining companies


def _range_for(index: int, ranges, trailing) -> tuple[int, int]:
    return ranges[index] if index < len(ranges) else trailing


def _word_count(text: str) -> int:
    """Words in a bullet, ignoring the ** bold markers."""
    return len(_BOLD.sub(r"\1", text or "").split())


def check_resume(resume, bullet_ranges=None, trailing=None) -> list[str]:
    """Return a list of human-readable rule violations (empty == all good)."""
    ranges = bullet_ranges or DEFAULT_BULLET_RANGES
    trail = trailing or DEFAULT_TRAILING
    issues: list[str] = []

    for i, job in enumerate(resume.experience):
        label = job.company or f"company #{i + 1}"
        lo, hi = _range_for(i, ranges, trail)
        n = len(job.bullets)
        if not (lo <= n <= hi):
            want = str(lo) if lo == hi else f"{lo}-{hi}"
            issues.append(f"{label}: has {n} bullets but needs {want}.")

        for j, bullet in enumerate(job.bullets):
            wc = _word_count(bullet)
            if wc < MIN_WORDS:
                issues.append(
                    f'{label} bullet {j + 1}: {wc} words, needs >= {MIN_WORDS} '
                    f'("{bullet[:50]}...").'
                )
            if not _BOLD.search(bullet):
                issues.append(
                    f"{label} bullet {j + 1}: no **bold** keyword — bold the key tech."
                )

    return issues