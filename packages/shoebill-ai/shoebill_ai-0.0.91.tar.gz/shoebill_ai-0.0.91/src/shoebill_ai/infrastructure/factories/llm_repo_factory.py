from abc import ABC, abstractmethod
from typing import Optional

from ...domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from ...domain.agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository


class LlmRepoFactory(ABC):
    """
    Abstract factory for creating model-specific repositories.
    This factory is responsible for creating the appropriate repositories for a given model.
    """

    @abstractmethod
    def create_chat_repository(self) -> LlmChatRepository:
        """
        Creates a chat repository for the model.

        Returns:
            LlmChatRepository: A repository for chat interactions with the model.
        """
        pass

    @abstractmethod
    def create_embedding_repository(self) -> Optional[LlmEmbeddingRepository]:
        """
        Creates an embedding repository for the model.

        Returns:
            Optional[LlmEmbeddingRepository]: A repository for creating embeddings with the model,
                                             or None if the model doesn't support embeddings.
        """
        pass
