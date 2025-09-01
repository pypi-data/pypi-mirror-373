from src.shoebill_ai.infrastructure.agents.ollama.repositories.base_ollama_repository import BaseOllamaRepository


def test_base_ollama_repository_initialization(mocker):
    """
    Tests that BaseOllamaRepository correctly initializes its attributes and
    instantiates OllamaHttpClient with the provided arguments.
    """
    # Patch the OllamaHttpClient to intercept its creation
    mock_http_client_class = mocker.patch(
        "src.shoebill_ai.infrastructure.agents.ollama.repositories.base_ollama_repository.OllamaHttpClient"
    )

    # Define arguments for initialization
    api_url = "https://api.test-ollama.com"
    model_name = "test-model"
    api_token = "test-token"
    timeout = 10

    # Create an instance of the repository
    repository = BaseOllamaRepository(
        api_url=api_url,
        model_name=model_name,
        api_token=api_token,
        timeout=timeout
    )

    # Assert that model_name is set correctly
    assert repository.model_name == model_name

    # Assert that OllamaHttpClient was called with the correct arguments
    mock_http_client_class.assert_called_once_with(api_url, api_token, timeout)

    # Assert that the created client instance is assigned to the repository
    assert repository.http_client == mock_http_client_class.return_value



