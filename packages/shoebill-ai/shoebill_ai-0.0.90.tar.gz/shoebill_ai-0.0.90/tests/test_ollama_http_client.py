import pytest
from src.shoebill_ai.infrastructure.agents.ollama.ollama_http_client import OllamaHttpClient


@pytest.fixture
def mock_client(mocker):
    mock_ollama_client = mocker.patch("src.shoebill_ai.infrastructure.agents.ollama.ollama_http_client.ollama.Client")
    return mock_ollama_client


@pytest.fixture
def ollama_http_client(mock_client):
    api_url = "https://api.test-ollama.com"
    api_token = "test-token"
    timeout = 10
    return OllamaHttpClient(api_url=api_url, api_token=api_token, timeout=timeout)


def test_initialization(ollama_http_client, mock_client):
    assert ollama_http_client.api_url == "https://api.test-ollama.com"
    assert ollama_http_client.api_token == "test-token"
    assert ollama_http_client.timeout == 10
    assert ollama_http_client.headers["Authorization"] == "Bearer test-token"

    # Verify the ollama.Client initialization with correct arguments
    mock_client.assert_called_once_with(
        host="https://api.test-ollama.com",
        headers={"Authorization": "Bearer test-token"},
        timeout=10
    )


def test_get_headers(ollama_http_client):
    headers = ollama_http_client._get_headers()
    assert headers == {"Authorization": "Bearer test-token"}


def test_post_chat_with_default_options(ollama_http_client, mock_client):
    mock_client.return_value.chat.return_value = [
        {"message": {"content": "Hello, "}},
        {"message": {"content": "world!"}, "done": True}
    ]
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Say hi"}],
        "stream": True
    }
    response = ollama_http_client.post(endpoint="chat", payload=payload)

    # Verify correct response
    assert response == {
        "message": {
            "role": "assistant",
            "content": "Hello, world!"
        }
    }

    # Verify options use default values
    mock_client.return_value.chat.assert_called_once_with(
        model="test-model",
        messages=[{"role": "user", "content": "Say hi"}],
        options={
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 20,
            "min_p": 0.0,
            "num_predict": 32768,
            "seed": 20240628,
            "num_ctx": 120000
        },
        stream=True,
        tools=None
    )


def test_post_chat_with_custom_options(ollama_http_client, mock_client):
    mock_client.return_value.chat.return_value = {"message": {"content": "Custom options response"}}
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Custom options test"}],
        "stream": False,
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 50,
        "min_p": 0.2,
        "num_predict": 5000,
        "seed": 123456,
        "num_ctx": 64000
    }
    response = ollama_http_client.post(endpoint="chat", payload=payload)

    # Verify correct response
    assert response == {
        "message": {
            "role": "assistant",
            "content": "Custom options response",
            "tool_calls": []
        }
    }

    # Verify custom options override defaults
    mock_client.return_value.chat.assert_called_once_with(
        model="test-model",
        messages=[{"role": "user", "content": "Custom options test"}],
        options={
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 50,
            "min_p": 0.2,
            "num_predict": 5000,
            "seed": 123456,
            "num_ctx": 64000
        },
        stream=False,
        tools=None
    )
