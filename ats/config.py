"""Configuration: paths, models, weights, pricing, and credentials (from .env)."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
# Load .env from the project root explicitly, so the tool works from any working
# directory (e.g. when launched by a global hotkey with no cwd).
load_dotenv(ROOT / ".env")
PROFILES_DIR = ROOT / "profiles"
OUTPUT_DIR = ROOT / "output"
# Integrated results log lives inside the output folder (one row per generated application).
APPLICATIONS_CSV = OUTPUT_DIR / "applications.csv"
# Shared base templates (per-profile templates at profiles/<id>/template.html override these).
TEMPLATES_DIR = ROOT / "templates"
# Company-wide tailoring policy applied to every profile (layered under each dev's own rules.md).
BASIC_RULES_FILE = ROOT / "shared" / "basic_rule.md"


def global_rules() -> str:
    return (
        BASIC_RULES_FILE.read_text(encoding="utf-8").strip()
        if BASIC_RULES_FILE.exists()
        else ""
    )

# OpenAI-compatible endpoint. Defaults to Fireworks.
DEFAULT_BASE_URL = "https://api.fireworks.ai/inference/v1"
DEFAULT_MODEL = "accounts/fireworks/models/gpt-oss-120b"

MATCH_MODEL = os.getenv("MATCH_MODEL", DEFAULT_MODEL)
GENERATE_MODEL = os.getenv("GENERATE_MODEL", DEFAULT_MODEL)
IMPORT_MODEL = os.getenv("IMPORT_MODEL", MATCH_MODEL)


def _num(name: str, fallback: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return fallback
    try:
        value = float(raw)
    except ValueError:
        return fallback
    return value if value >= 0 else fallback


MAX_TOKENS = int(_num("MAX_TOKENS", 8000))

# Resilience against transient API errors (timeouts, 429/5xx). The SDK retries with backoff.
MAX_RETRIES = int(_num("MAX_RETRIES", 5))
REQUEST_TIMEOUT = _num("REQUEST_TIMEOUT", 180.0)

# USD per 1M tokens, for the cost estimate printed after each run. Defaults = gpt-oss-120b.
PRICE_INPUT_PER_M = _num("PRICE_INPUT_PER_M", 0.15)
PRICE_OUTPUT_PER_M = _num("PRICE_OUTPUT_PER_M", 0.60)


def weights() -> dict[str, float]:
    """Scoring weights, normalized to sum to 1. Industry is the rule-of-thumb default."""
    industry = _num("WEIGHT_INDUSTRY", 0.5)
    skill = _num("WEIGHT_SKILL", 0.3)
    location = _num("WEIGHT_LOCATION", 0.2)
    total = industry + skill + location or 1.0
    return {
        "industry": industry / total,
        "skill": skill / total,
        "location": location / total,
    }


def get_api_key() -> str:
    key = os.getenv("LLM_API_KEY") or os.getenv("FIREWORKS_API_KEY")
    if not key:
        raise RuntimeError(
            "LLM_API_KEY is not set. Copy .env.example to .env and add your Fireworks key."
        )
    return key


def get_base_url() -> str:
    return os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL)
