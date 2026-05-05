"""Strict DeepSeek/OpenAI-compatible LLM gateway."""

from __future__ import annotations

import json
import os
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMClient:
    """Minimal model gateway."""

    model_name: str
    provider: str = "deepseek"
    base_url: str = "https://api.deepseek.com"
    api_key_env: str = "DEEPSEEK_API_KEY"
    temperature: float = 0.1
    max_tokens: int = 4096
    timeout_seconds: int = 120
    retries: int = 2
    thinking_enabled: bool = False
    reasoning_effort: str = ""

    def complete(
        self,
        prompt: str,
        system: str = "",
        json_mode: bool = False,
    ) -> str:
        if self.provider not in {"deepseek", "openai_compatible", "openai-compatible"}:
            raise RuntimeError(f"Unsupported LLM provider: {self.provider}")
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing {self.api_key_env}. Set it before running the pipeline.")
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system or "You are a careful applied research engineering assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        if self.thinking_enabled:
            payload["thinking"] = {"type": "enabled"}
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        request = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        last_error = ""
        for attempt in range(max(1, self.retries + 1)):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    data = json.loads(response.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                if json_mode:
                    try:
                        json.loads(content)
                    except json.JSONDecodeError:
                        # Some OpenAI-compatible endpoints still return JSON
                        # wrapped in prose; let downstream jsonish repair try,
                        # but mark truly empty responses as failed.
                        if not content.strip():
                            raise
                return content
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                last_error = f"HTTP {exc.code}: {body[:800]}"
                if 400 <= exc.code < 500 and exc.code not in {408, 409, 429}:
                    break
            except (
                ConnectionResetError,
                TimeoutError,
                socket.timeout,
                urllib.error.URLError,
                json.JSONDecodeError,
                KeyError,
                OSError,
            ) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
            if attempt < self.retries:
                time.sleep(min(2.0 * (attempt + 1), 6.0))
        raise RuntimeError(f"LLM API call failed after retries: {last_error or 'remote API failure'}")


@dataclass
class ModelRouter:
    """Map pipeline stages to cheap or strong model clients."""

    cheap: LLMClient
    strong: LLMClient
    stage_models: dict[str, str]

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "ModelRouter":
        model_config = config.get("model", {})
        thinking_config = model_config.get("thinking", {})
        if not isinstance(thinking_config, dict):
            thinking_config = {}
        common = {
            "provider": model_config.get("provider", "deepseek"),
            "base_url": model_config.get("base_url", "https://api.deepseek.com"),
            "api_key_env": model_config.get("api_key_env", "DEEPSEEK_API_KEY"),
            "temperature": float(model_config.get("temperature", 0.1)),
            "max_tokens": int(model_config.get("max_tokens", 4096)),
            "timeout_seconds": int(model_config.get("timeout_seconds", 120)),
            "retries": int(model_config.get("retries", 2)),
            "thinking_enabled": bool(thinking_config.get("enabled", model_config.get("thinking_enabled", False))),
            "reasoning_effort": str(thinking_config.get("reasoning_effort", model_config.get("reasoning_effort", ""))).strip(),
        }
        return cls(
            cheap=LLMClient(model_config.get("cheap_model", "deepseek-v4-pro"), **common),
            strong=LLMClient(model_config.get("strong_model", "deepseek-v4-pro"), **common),
            stage_models=model_config.get("stage_models", {}),
        )

    def for_stage(self, stage: str) -> LLMClient:
        tier = self.stage_models.get(stage, "cheap")
        return self.strong if tier == "strong" else self.cheap

    def describe(self) -> dict[str, str]:
        return {
            stage: self.for_stage(stage).model_name
            for stage in sorted(self.stage_models)
        }
