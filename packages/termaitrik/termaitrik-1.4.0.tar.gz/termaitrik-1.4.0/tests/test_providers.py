import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from termai.providers import (
    OllamaProvider,
    OpenAIProvider,
    ProviderError,
    ChatMessage,
    make_provider,
)


@patch("requests.post")
def test_ollama_provider_chat_non_stream(mock_post):
    # Mock the response from the Ollama API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "model": "llama3",
        "created_at": "2023-08-04T19:22:45.499127Z",
        "message": {"role": "assistant", "content": "Hello, world!"},
        "done": True,
    }
    mock_post.return_value = mock_response

    provider = OllamaProvider(host="http://localhost:11434")
    messages = [ChatMessage(role="user", content="Hi")]
    response = provider.chat(
        messages=messages,
        model="llama3",
        stream=False,
    )
    result = "".join(response)
    assert result == "Hello, world!"


@patch("requests.post")
def test_ollama_provider_chat_stream(mock_post):
    # Mock the streaming response from the Ollama API
    mock_response = MagicMock()
    mock_response.status_code = 200
    stream_chunks = [
        {"message": {"content": "Hello,"}},
        {"message": {"content": " world!"}},
    ]
    mock_response.iter_lines.return_value = [
        json.dumps(chunk).encode("utf-8") for chunk in stream_chunks
    ]
    mock_post.return_value.__enter__.return_value = mock_response

    provider = OllamaProvider(host="http://localhost:11434")
    messages = [ChatMessage(role="user", content="Hi")]
    response = provider.chat(
        messages=messages,
        model="llama3",
        stream=True,
    )
    result = "".join(response)
    assert result == "Hello, world!"


@patch("requests.post")
def test_ollama_provider_http_error(mock_post):
    # Mock an HTTP error from the Ollama API
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_post.return_value = mock_response

    provider = OllamaProvider(host="http://localhost:11434")
    messages = [ChatMessage(role="user", content="Hi")]
    with pytest.raises(ProviderError):
        list(provider.chat(messages=messages, model="llama3"))


@patch("requests.post")
def test_openai_provider_chat_non_stream(mock_post):
    # Mock the response from the OpenAI API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello from OpenAI!"}}]
    }
    mock_post.return_value = mock_response

    provider = OpenAIProvider(api_key="fake_key")
    messages = [ChatMessage(role="user", content="Hi")]
    response = provider.chat(
        messages=messages,
        model="gpt-4",
        stream=False,
    )
    result = "".join(response)
    assert result == "Hello from OpenAI!"


@patch("requests.post")
def test_openai_provider_chat_stream(mock_post):
    # Mock the streaming response from the OpenAI API
    mock_response = MagicMock()
    mock_response.status_code = 200
    stream_chunks = [
        b'data: {"choices": [{"delta": {"content": "Hello,"}}]}',
        b'data: {"choices": [{"delta": {"content": " world!"}}]}',
        b"data: [DONE]",
    ]
    mock_response.iter_lines.return_value = stream_chunks
    mock_post.return_value.__enter__.return_value = mock_response

    provider = OpenAIProvider(api_key="fake_key")
    messages = [ChatMessage(role="user", content="Hi")]
    response = provider.chat(
        messages=messages,
        model="gpt-4",
        stream=True,
    )
    result = "".join(response)
    assert result == "Hello, world!"


@patch("requests.post")
def test_openai_provider_http_error(mock_post):
    # Mock an HTTP error from the OpenAI API
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_post.return_value = mock_response

    provider = OpenAIProvider(api_key="fake_key")
    messages = [ChatMessage(role="user", content="Hi")]
    with pytest.raises(ProviderError):
        list(provider.chat(messages=messages, model="gpt-4"))


def test_make_provider_ollama():
    cfg = {"default_provider": "ollama", "ollama": {"host": "http://test.host"}}
    provider = make_provider(cfg)
    assert isinstance(provider, OllamaProvider)
    assert provider.base == "http://test.host"


def test_make_provider_openai():
    cfg = {
        "default_provider": "openai",
        "openai": {"api_key": "test_key", "base_url": "http://test.url"},
    }
    provider = make_provider(cfg)
    assert isinstance(provider, OpenAIProvider)
    assert provider.api_key == "test_key"
    assert provider.base_url == "http://test.url"


def test_make_provider_missing_key():
    with pytest.raises(ProviderError):
        make_provider({"default_provider": "openai", "openai": {"api_key": ""}})


def test_make_provider_env_vars(monkeypatch):
    monkeypatch.setenv("TERMAI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "env_key")
    provider = make_provider({})
    assert isinstance(provider, OpenAIProvider)
    assert provider.api_key == "env_key"
