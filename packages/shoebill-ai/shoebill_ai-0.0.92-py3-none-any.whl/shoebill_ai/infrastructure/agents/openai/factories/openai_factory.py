from typing import Optional, List, Dict, Any

from ....factories.llm_repo_factory import LlmRepoFactory
from .....domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from .....domain.agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository
from ..repositories.openai_chat_repository import OpenAIChatRepository
from ..repositories.openai_embedding_repository import OpenAIEmbeddingRepository


class OpenAIFactory(LlmRepoFactory):
    """
    Factory for creating repositories for OpenAI models.
    This factory can create repositories for any OpenAI model based on its capabilities.
    """

    def __init__(self, api_key: str, temperature: float = 0.7, max_tokens: int = 2000,
                 organization: str = None, system_prompt: str = None,
                 model_name: str = None, tools: List[Dict[str, Any]] = None,
                 timeout: Optional[int] = None):
        """
        Initialize a new OpenAIFactory.

        Args:
            api_key: The API key for authentication.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            organization: Optional organization ID for API requests.
            system_prompt: Optional system prompt to use for generation and chat.
            model_name: The name of the model to use.
            tools: Optional list of tools to make available to the model.
            timeout: Optional timeout in seconds for API requests.
        """
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.organization = organization
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.tools = tools or []
        self.timeout = timeout

        if not model_name:
            raise ValueError("Model name cannot be empty or None")

    def create_chat_repository(self) -> LlmChatRepository:
        """
        Creates a chat repository for the model.

        Returns:
            LlmChatRepository: A repository for chat interactions with the model.
        """
        kwargs = {
            "api_key": self.api_key,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "organization": self.organization
        }

        # Add system prompts if provided
        if self.system_prompt:
            kwargs["system_prompts"] = [self.system_prompt]

        # Add tools if provided
        if self.tools:
            kwargs["tools"] = self.tools

        # Add timeout if provided
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout

        return OpenAIChatRepository(**kwargs)

    def create_embedding_repository(self) -> Optional[LlmEmbeddingRepository]:
        """
        Creates an embedding repository for the model if it supports embeddings.

        Returns:
            Optional[LlmEmbeddingRepository]: A repository for creating embeddings with the model,
                                             or None if the model doesn't support embeddings.
        """
        # Check if the model supports embeddings
        if any(self.model_name.startswith(prefix) for prefix in self.EMBEDDING_MODEL_PREFIXES):
            kwargs = {
                "api_key": self.api_key,
                "model_name": self.model_name,
                "organization": self.organization
            }

            # Add timeout if provided
            if self.timeout is not None:
                kwargs["timeout"] = self.timeout

            return OpenAIEmbeddingRepository(**kwargs)
        return None
