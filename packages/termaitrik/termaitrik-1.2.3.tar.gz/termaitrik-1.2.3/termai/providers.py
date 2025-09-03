from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Iterator
import os

import requests


@dataclass
class ChatMessage:
    role: str
    content: str


class ProviderError(RuntimeError):
    pass


class BaseProvider:
    name: str

    def chat(self, messages: List[ChatMessage], model: str, temperature: float = 0.2, stream: bool = False) -> Iterator[str]:
        raise NotImplementedError


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, host: str = "http://127.0.0.1:11434"):
        # Normalize host so callers may pass:
        #  - http://host:port
        #  - http://host:port/v1
        #  - http://host:port/api
        # We want self.base to be the authority + optional port, without trailing
        # path segments, so we consistently append /api/chat below.
        base = host.rstrip("/")
        if base.endswith("/v1"):
            base = base[: -len("/v1")]
        if base.endswith("/api"):
            base = base[: -len("/api")]
        self.base = base.rstrip("/")

    def chat(self, messages: List[ChatMessage], model: str, temperature: float = 0.2, stream: bool = False) -> Iterator[str]:
        url = f"{self.base}/api/chat"
        payload = {
            "model": model,
            "messages": [m.__dict__ for m in messages],
            "options": {"temperature": temperature},
            "stream": stream,
        }
        if not stream:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code != 200:
                raise ProviderError(f"Ollama error {resp.status_code}: {resp.text}")
            data = resp.json()
            yield data.get("message", {}).get("content", "")
        else:
            # For streaming requests, do not pass 0 as timeout (urllib3 rejects <= 0).
            # None means no timeout (block until response/stream closes).
            with requests.post(url, json=payload, stream=True, timeout=None) as r:
                if r.status_code != 200:
                    raise ProviderError(f"Ollama error {r.status_code}: {r.text}")
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        part = json.loads(line.decode("utf-8"))
                        delta = part.get("message", {}).get("content", "")
                        if delta:
                            yield delta
                    except Exception:
                        continue


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def chat(self, messages: List[ChatMessage], model: str, temperature: float = 0.2, stream: bool = False) -> Iterator[str]:
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is missing")
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": [m.__dict__ for m in messages],
            "temperature": temperature,
            "stream": stream,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if not stream:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code != 200:
                raise ProviderError(f"OpenAI error {resp.status_code}: {resp.text}")
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                return
            yield choices[0].get("message", {}).get("content", "")
        else:
            # For streaming requests, do not pass 0 as timeout (urllib3 rejects <= 0).
            # None means no timeout (block until response/stream closes).
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=None) as r:
                if r.status_code != 200:
                    raise ProviderError(f"OpenAI error {r.status_code}: {r.text}")
                for line in r.iter_lines():
                    if not line:
                        continue
                    if line.startswith(b"data: "):
                        line = line[6:]
                    if line.strip() == b"[DONE]":
                        break
                    try:
                        part = json.loads(line.decode("utf-8"))
                        delta = part.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            yield delta
                    except Exception:
                        continue


VALID_PROVIDERS = {"ollama", "openai"}


def make_provider(cfg: Dict) -> BaseProvider:
    """
    Resolves which provider to use.

    Priority:
      1. TERMAI_PROVIDER environment variable
      2. cfg['default_provider']
      3. fallback -> 'ollama'
    """
    env_provider = os.getenv("TERMAI_PROVIDER")
    provider = (env_provider or cfg.get("default_provider") or "ollama").lower()

    if provider not in VALID_PROVIDERS:
        raise ProviderError(f"Unsupported provider: {provider}")

    if provider == "ollama":
        return OllamaProvider(host=cfg.get("ollama", {}).get("host", "http://127.0.0.1:11434"))

    # openai
    ocfg = cfg.get("openai", {}) or {}
    api_key = ocfg.get("api_key") or os.getenv("OPENAI_API_KEY") or ""
    base_url = ocfg.get("base_url", "https://api.openai.com/v1")
    if not api_key:
        # fail early for clarity
        raise ProviderError("OpenAI provider selected but API key is missing (config.openai.api_key or OPENAI_API_KEY).")
    return OpenAIProvider(api_key=api_key, base_url=base_url)
