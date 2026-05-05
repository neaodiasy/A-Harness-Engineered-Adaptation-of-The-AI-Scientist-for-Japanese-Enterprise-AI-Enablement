"""JSON validation and small repair helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path, fallback: Any | None = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        if fallback is not None:
            return fallback
        raise


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require_keys(item: dict[str, Any], keys: list[str]) -> bool:
    return all(key in item and item[key] not in (None, "") for key in keys)


def parse_jsonish(text: str, fallback: Any | None = None) -> Any:
    """Parse raw JSON or a fenced JSON block; return fallback if parsing fails."""
    candidates = [text.strip()]
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        candidates.insert(0, fenced.group(1).strip())
    bracket = re.search(r"(\[.*\]|\{.*\})", text, flags=re.DOTALL)
    if bracket:
        candidates.append(bracket.group(1).strip())
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return fallback
