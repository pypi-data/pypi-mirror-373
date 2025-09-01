from .....domain.agents.interfaces.base_repository import BaseRepository
from ..ollama_http_client import OllamaHttpClient


class BaseOllamaRepository(BaseRepository):
    """
    Base class for all Ollama repositories.
    Provides common functionality for interacting with the Ollama API.
    """

    def __init__(self, api_url: str, model_name: str, api_token: str = None, timeout: int = None):
        """
        Initialize a new BaseOllamaRepository.

        Args:
            api_url: The base URL of the Ollama API.
            model_name: The name of the model to use.
            api_token: Optional API token for authentication.
            timeout: Optional timeout in seconds for API requests.
        """
        self.model_name = model_name
        self.http_client = OllamaHttpClient(api_url, api_token, timeout)
