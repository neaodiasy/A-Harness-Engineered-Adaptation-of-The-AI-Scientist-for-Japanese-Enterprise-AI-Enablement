"""DeepSeek/OpenAI-compatible JSON client for the generated app."""

from __future__ import annotations

import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    import certifi
except Exception:  # pragma: no cover
    certifi = None


def _ssl_context():
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


APP_DIR = Path(__file__).resolve().parents[1]
LOADED_ENV_FILES: list[str] = []


def candidate_env_files() -> list[Path]:
    candidates = [APP_DIR / ".env.local", Path.cwd() / ".env.local"]
    candidates.extend(parent / ".env.local" for parent in APP_DIR.parents[:3])
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)
    return unique


def load_env_file(path: Path | None = None) -> None:
    """Load local runtime settings without requiring shell exports."""
    paths = [path] if path is not None else candidate_env_files()
    for current_path in paths:
        if not current_path.exists():
            continue
        LOADED_ENV_FILES.append(str(current_path.resolve()))
        for raw_line in current_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and not os.environ.get(key):
                os.environ[key] = value


load_env_file()


def parse_jsonish(text: str) -> dict[str, Any]:
    candidates = [text.strip()]
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        candidates.insert(0, fenced.group(1).strip())
    bracket = re.search(r"(\{.*\})", text, flags=re.DOTALL)
    if bracket:
        candidates.append(bracket.group(1).strip())
    for candidate in candidates:
        try:
            value = json.loads(candidate)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            continue
    raise ValueError("DeepSeek did not return a valid JSON object.")


def _endpoint() -> str:
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return base_url + "/chat/completions"


def connection_status() -> dict[str, Any]:
    model = os.environ.get("AGENT_MODEL") or os.environ.get("DEEPSEEK_AGENT_MODEL") or "deepseek-v4-pro"
    thinking_enabled = os.environ.get("DEEPSEEK_THINKING", "1").lower() not in {"0", "false", "disabled", "off", "no"}
    reasoning_effort = os.environ.get("DEEPSEEK_REASONING_EFFORT", "high").strip()
    has_key = bool(os.environ.get("DEEPSEEK_API_KEY"))
    return {
        "has_api_key": has_key,
        "deepseek_api_key_present": has_key,
        "base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "deepseek_base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "endpoint": _endpoint(),
        "model": model,
        "agent_model": model,
        "thinking_enabled": thinking_enabled,
        "thinking": os.environ.get("DEEPSEEK_THINKING", "1"),
        "reasoning_effort": reasoning_effort,
        "env_file_loaded": bool(LOADED_ENV_FILES),
        "env_files_loaded": LOADED_ENV_FILES,
    }


def complete_json(system_prompt: str, user_prompt: str, *, retries: int = 2) -> dict[str, Any]:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is required. This generated product has no mock mode.")
    model = os.environ.get("AGENT_MODEL") or os.environ.get("DEEPSEEK_AGENT_MODEL") or "deepseek-v4-pro"
    thinking_enabled = os.environ.get("DEEPSEEK_THINKING", "1").lower() not in {"0", "false", "disabled", "off", "no"}
    reasoning_effort = os.environ.get("DEEPSEEK_REASONING_EFFORT", "high").strip()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 6000,
        "stream": False,
        "response_format": {"type": "json_object"},
    }
    if thinking_enabled:
        payload["thinking"] = {"type": "enabled"}
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    last_error: Exception | None = None
    ssl_context = _ssl_context()
    for attempt in range(retries + 1):
        request = urllib.request.Request(
            _endpoint(),
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120, context=ssl_context) as response:
                data = json.loads(response.read().decode("utf-8"))
            raw = data["choices"][0]["message"]["content"]
            try:
                return parse_jsonish(raw)
            except ValueError:
                repair_prompt = (
                    "Repair this response into one valid JSON object only. Do not add Markdown.\n\n"
                    + raw
                )
                payload["messages"] = [
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user", "content": repair_prompt},
                ]
        except (ConnectionResetError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            break
    raise RuntimeError(f"DeepSeek request failed after retries: {last_error}") from last_error
