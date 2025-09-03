from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


DEFAULT_CONFIG_PATH = Path.home() / ".termai" / "config.yaml"


def _expand_env_vars(d: Any) -> Any:
    if isinstance(d, dict):
        return {k: _expand_env_vars(v) for k, v in d.items()}
    if isinstance(d, list):
        return [_expand_env_vars(x) for x in d]
    if isinstance(d, str):
        return os.path.expandvars(d)
    return d


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Loads the configuration from a YAML file, with environment variable overrides.
    """
    if path is None:
        local = Path.cwd() / "config.yaml"
        path = local if local.exists() else DEFAULT_CONFIG_PATH

    cfg: Dict[str, Any] = {
        "default_provider": "ollama",
        "model": "llama3.1",
        "ollama": {
            "host": "http://127.0.0.1:11434/v1",
        },
        "openai": {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
        },
    }

    if path.exists():
        try:
            raw = path.read_text()
            data = yaml.safe_load(raw) or {}
            expanded = _expand_env_vars(data)
            if isinstance(expanded, dict):
                for key, value in expanded.items():
                    if key in cfg and isinstance(cfg[key], dict) and isinstance(value, dict):
                        cfg[key].update(value)
                    else:
                        cfg[key] = value
            else:
                logger.warning(
                    "Config file %s did not contain a mapping at top-level, ignoring.", path
                )
        except yaml.YAMLError as e:
            logger.error("Failed to parse YAML config %s: %s", path, e)
        except Exception as e:
            logger.exception("Unexpected error loading config %s: %s", path, e)

    # Environment variables override config file values
    # Only apply non-empty environment variables so empty exports don't blank defaults
    def _maybe(var: str, current: str) -> str:
        val = os.environ.get(var, None)
        return val if val not in (None, "") else current

    cfg["default_provider"] = _maybe("TERMAI_PROVIDER", cfg["default_provider"])
    cfg["model"] = _maybe("TERMAI_MODEL", cfg["model"])
    cfg["ollama"]["host"] = _maybe("OLLAMA_HOST", cfg["ollama"]["host"])
    cfg["openai"]["api_key"] = _maybe("OPENAI_API_KEY", cfg["openai"]["api_key"])
    cfg["openai"]["base_url"] = _maybe("OPENAI_BASE_URL", cfg["openai"]["base_url"])

    return cfg
