import pytest
import requests
from termai.providers import OllamaProvider, ProviderError, ChatMessage

# Check if Ollama is running
try:
    requests.get("http://127.0.0.1:11434")
    ollama_running = True
except requests.exceptions.ConnectionError:
    ollama_running = False

def is_model_available(model_name):
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        return any(model["name"] == model_name for model in models)
    except (requests.exceptions.RequestException, KeyError):
        return False

@pytest.mark.skipif(not ollama_running or not is_model_available("phi3"), reason="Ollama is not running or phi3 model not available")
def test_ollama_integration():
    provider = OllamaProvider(host="http://127.0.0.1:11434")
    messages = [ChatMessage(role="user", content="What is 2 + 2?")]
    response = provider.chat(messages=messages, model="phi3")
    result = "".join(response)
    assert "4" in result
