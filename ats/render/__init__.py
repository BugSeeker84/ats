"""Deterministic rendering layer: validated JSON content -> HTML -> PDF.

The LLM never emits layout. It returns structured content (see ats.schema);
the modules here turn that content into the final artifacts:

    html.py   JSON content -> HTML (per-profile Jinja template)
    pdf.py    HTML -> PDF (headless Chromium via Playwright)

This keeps styling 100% deterministic and out of the model's hands.
"""
