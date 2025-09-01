from typing import Optional, List, Dict, Any

from ....factories.llm_repo_factory import LlmRepoFactory
from .....domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from .....domain.agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository
from ..repositories.ollama_chat_repository import OllamaChatRepository
from ..repositories.ollama_embed_repository import OllamaEmbeddingRepository


class OllamaFactory(LlmRepoFactory):
    """
    Factory for creating repositories for Ollama models.
    This factory can create repositories for any Ollama model based on its capabilities.
    """

    def __init__(self,
                 api_url: str,
                 model_name: str,
                 api_token: str = None,
                 system_prompt: str = None,
                 tools: List[Dict[str, Any]] = None,
                 timeout: int = 60,
                 options: Dict[str, Any] = None):
        """
        Initialize a new OllamaFactory.

        Args:
            api_url: The base URL of the Ollama API.
            api_token: Optional API token for authentication.
            system_prompt: Optional system prompt to use for generation and chat.
            model_name: The name of the model to use.
            tools: Optional list of tools to make available to the model.
            timeout: Optional timeout in seconds for API requests.
        """
        self.api_url = api_url
        self.options = options or {}
        self.api_token = api_token
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.tools = tools or []
        self.timeout = timeout

    def create_chat_repository(self) -> LlmChatRepository:
        """
        Creates a chat repository for the model.

        Returns:
            LlmChatRepository: A repository for chat interactions with the model.
        """
        kwargs: dict[str, Any] = {
            "api_url": self.api_url,
            "model_name": self.model_name,
            "api_token": self.api_token,
            "options": self.options
        }

        # Add system prompts if provided
        if self.system_prompt:
            kwargs["system_prompt"] = self.system_prompt

        # Add tools if provided
        if self.tools:
            kwargs["tools"] = self.tools

        # Add timeout if provided
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout

        return OllamaChatRepository(**kwargs)


    def create_embedding_repository(self) -> Optional[LlmEmbeddingRepository]:
        """
        Creates an embedding repository for the model if it supports embeddings.

        Returns:
            Optional[LlmEmbeddingRepository]: A repository for creating embeddings with the model,
                                             or None if the model doesn't support embeddings.
        """
        kwargs: dict[str, Any] = {
            "api_url": self.api_url,
            "model_name": self.model_name,
            "api_token": self.api_token
        }

        # Add timeout if provided
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout

        return OllamaEmbeddingRepository(**kwargs)