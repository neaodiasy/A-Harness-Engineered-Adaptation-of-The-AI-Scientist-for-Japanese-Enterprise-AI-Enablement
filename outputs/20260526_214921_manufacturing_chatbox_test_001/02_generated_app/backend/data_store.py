"""Data loading helpers for the generated product."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"


def load_json_file(relative_path: str) -> Any:
    return json.loads((APP_DIR / relative_path).read_text(encoding="utf-8"))


def load_product_spec() -> dict[str, Any]:
    return load_json_file("product_spec.json")


def load_domain_data() -> dict[str, Any]:
    return load_json_file("domain_data.json")


def load_llm_app_design() -> dict[str, Any]:
    return load_json_file("llm_app_design.json")


def load_interaction_config() -> dict[str, Any]:
    return load_json_file("frontend/generated_interaction_config.json")


def load_agent_spec() -> dict[str, Any]:
    return load_json_file("agent_spec.json")


def load_areas() -> list[dict[str, Any]]:
    return load_json_file("data/areas.json")


def load_properties() -> list[dict[str, Any]]:
    return load_json_file("data/properties.json")


def load_sample_cases() -> list[dict[str, Any]]:
    return load_json_file("data/sample_customers.json")


def load_knowledge_base() -> str:
    return (APP_DIR / "knowledge_base.md").read_text(encoding="utf-8")
