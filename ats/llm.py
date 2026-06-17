"""OpenAI-compatible chat client (Fireworks by default) + helpers."""
import json
import re

from openai import OpenAI

from . import config

_client: OpenAI | None = None

# Cumulative token usage since process start.
_usage = {"input_tokens": 0, "output_tokens": 0, "calls": 0}


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=config.get_api_key(),
            base_url=config.get_base_url(),
            max_retries=config.MAX_RETRIES,
            timeout=config.REQUEST_TIMEOUT,
        )
    return _client


def get_usage() -> dict:
    return dict(_usage)


def complete(
    model: str,
    system: str,
    user: str,
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> str:
    """Single-turn chat completion. Returns the response text and records token usage."""
    kwargs = {
        "model": model,
        "max_tokens": max_tokens or config.MAX_TOKENS,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if temperature is not None:
        kwargs["temperature"] = temperature
    res = _get_client().chat.completions.create(**kwargs)
    usage = getattr(res, "usage", None)
    if usage is not None:
        _usage["input_tokens"] += getattr(usage, "prompt_tokens", 0) or 0
        _usage["output_tokens"] += getattr(usage, "completion_tokens", 0) or 0
    _usage["calls"] += 1

    content = res.choices[0].message.content
    if not content:
        raise RuntimeError("Model returned an empty response.")
    return content.strip()


def extract_json(text: str):
    """Extract the first balanced JSON object/array, tolerating fences/prose/reasoning."""
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    candidate = fenced.group(1) if fenced else text

    start = next((i for i, ch in enumerate(candidate) if ch in "{["), -1)
    if start == -1:
        raise ValueError(f"No JSON found in model response:\n{text}")

    open_ch = candidate[start]
    close_ch = "}" if open_ch == "{" else "]"
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(candidate)):
        ch = candidate[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return json.loads(candidate[start : i + 1])
    raise ValueError(f"Could not parse balanced JSON from model response:\n{text}")
