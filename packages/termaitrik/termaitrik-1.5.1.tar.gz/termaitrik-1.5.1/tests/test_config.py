import os
from pathlib import Path
import yaml
import pytest
from termai.config import load_config, DEFAULT_CONFIG_PATH

def test_load_config_default(monkeypatch, tmp_path: Path):
    # Test with no config file present
    monkeypatch.setenv("TERMAI_PROVIDER", "")
    monkeypatch.setattr(Path, 'home', lambda: tmp_path)
    cfg = load_config()
    assert cfg["default_provider"] == "ollama"

def test_load_config_env_override(monkeypatch, tmp_path: Path):
    # Test environment variable override
    custom_config_path = tmp_path / "config.yaml"
    custom_config_path.write_text(
        yaml.dump({"default_provider": "openai", "model": "gpt-4"})
    )
    monkeypatch.setenv("TERMAI_PROVIDER", "ollama")
    monkeypatch.setenv("TERMAI_MODEL", "llama2")
    cfg = load_config(custom_config_path)
    assert cfg["default_provider"] == "ollama"
    assert cfg["model"] == "llama2"

def test_load_config_env_expansion(tmp_path: Path):
    # Test environment variable expansion
    custom_config_path = tmp_path / "config.yaml"
    os.environ["MY_API_KEY"] = "12345"
    custom_config_path.write_text(
        yaml.dump({"openai": {"api_key": "${MY_API_KEY}"}})
    )
    cfg = load_config(custom_config_path)
    assert cfg["openai"]["api_key"] == "12345"

def test_load_config_custom_path(tmp_path: Path):
    # Test with a custom config file
    custom_config_path = tmp_path / "config.yaml"
    custom_config_path.write_text(
        yaml.dump({"default_provider": "openai", "model": "gpt-4"})
    )
    cfg = load_config(custom_config_path)
    assert cfg["default_provider"] == "openai"
    assert cfg["model"] == "gpt-4"

def test_load_config_malformed_yaml(tmp_path: Path):
    # Test with a malformed YAML file
    malformed_config_path = tmp_path / "malformed.yaml"
    malformed_config_path.write_text("default_provider: [openai")
    cfg = load_config(malformed_config_path)
    # Should return default config
    assert cfg["default_provider"] == "ollama"

def test_load_config_merge(tmp_path: Path):
    # Test merging of default and custom configs
    custom_config_path = tmp_path / "config.yaml"
    custom_config_path.write_text(
        yaml.dump({"openai": {"api_key": "custom_key"}})
    )
    cfg = load_config(custom_config_path)
    assert cfg["openai"]["api_key"] == "custom_key"
    assert cfg["ollama"]["host"] is not None
