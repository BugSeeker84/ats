"""Render HTML to PDF with headless Chromium (Playwright).

High-fidelity, deterministic, and self-contained on Windows. Page margins are controlled
here (the templates zero out body padding under @media print).
"""
from pathlib import Path

_MARGIN = {"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"}


class PdfUnavailable(RuntimeError):
    """Raised when the Chromium browser isn't installed for Playwright."""


def html_to_pdfs(jobs: list[tuple[str, Path]]) -> None:
    """Render each (html, out_path) to a Letter-size PDF, reusing one browser.

    Raises PdfUnavailable with an actionable hint if Chromium isn't installed.
    """
    if not jobs:
        return
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as err:  # pragma: no cover
        raise PdfUnavailable(
            "Playwright is not installed. Run: pip install -e . "
            "&& python -m playwright install chromium"
        ) from err

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                for html, out_path in jobs:
                    page = browser.new_page()
                    page.emulate_media(media="print")
                    page.set_content(html, wait_until="load")
                    page.pdf(
                        path=str(out_path),
                        format="Letter",
                        print_background=True,
                        margin=_MARGIN,
                    )
                    page.close()
            finally:
                browser.close()
    except PlaywrightError as err:
        msg = str(err)
        if "Executable doesn't exist" in msg or "playwright install" in msg:
            raise PdfUnavailable(
                "Chromium isn't installed for Playwright. Run: "
                "python -m playwright install chromium"
            ) from err
        raise