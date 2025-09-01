from .....domain.agents.interfaces.base_repository import BaseRepository
from ..openai_http_client import OpenAIHttpClient


class BaseOpenAIRepository(BaseRepository):
    """
    Base class for all OpenAI repositories.
    Provides common functionality for interacting with the OpenAI API.
    """

    def __init__(self, api_key: str, model_name: str, organization: str = None, timeout: int = None):
        """
        Initialize a new BaseOpenAIRepository.

        Args:
            api_key: The API key for authentication.
            model_name: The name of the model to use.
            organization: Optional organization ID for API requests.
            timeout: Optional timeout in seconds for API requests.
        """
        self.model_name = model_name
        self.http_client = OpenAIHttpClient(api_key, organization, timeout)