from typing import Optional, List
import logging

from .....domain.agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository
from .base_openai_repository import BaseOpenAIRepository

logger = logging.getLogger(__name__)


class OpenAIEmbeddingRepository(BaseOpenAIRepository, LlmEmbeddingRepository):
    """
    Repository for creating embeddings using the OpenAI API.
    """

    def __init__(self, api_key: str, model_name: str, organization: str = None, timeout: int = None):
        """
        Initialize a new OpenAIEmbeddingRepository.

        Args:
            api_key: The API key for authentication.
            model_name: The name of the model to use.
            organization: Optional organization ID for API requests.
            timeout: Optional timeout in seconds for API requests.
        """
        super().__init__(api_key, model_name, organization, timeout)

    def embed(self, text: str) -> Optional[List[float]]:
        """
        Create an embedding for the given text using the OpenAI API.

        Args:
            text: The text to create an embedding for.

        Returns:
            Optional[List[float]]: The embedding vector, or None if the request failed.
        """
        payload = {
            "model": self.model_name,
            "input": text
        }

        logger.info(f"Creating embedding with model {self.model_name}")
        logger.debug(f"Text for embedding: {text[:50]}...")

        # Call the embeddings endpoint using the OpenAI client
        response_data = self.http_client.post("embeddings", payload)
        if response_data:
            embedding = response_data.get("embedding")
            if embedding:
                logger.info("Embedding created successfully")
                logger.debug(f"Embedding vector length: {len(embedding)}")
                return embedding
            else:
                logger.error("Embedding response did not contain embedding data")
        else:
            logger.error("Failed to get response from embeddings API")

        return None