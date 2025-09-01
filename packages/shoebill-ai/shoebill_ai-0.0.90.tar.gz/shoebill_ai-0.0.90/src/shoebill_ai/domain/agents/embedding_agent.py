from typing import Dict, List, Any

from .. import LlmEmbeddingRepository

class EmbeddingAgent:

    def __init__(self,
                 api_url: str,
                 model_name: str,
                 api_token: str = None,
                 timeout: int = 60,
                 options: Dict[str, Any] = None,
                 provider: str = "ollama"):
        """
        Create a new TextAgent
        """
        self.api_url = api_url
        self.model_name = model_name
        self.api_token = api_token
        self.timeout = timeout
        self.options = options or {}



        self.llm_embedding_repository: LlmEmbeddingRepository | None = None
        if provider == "ollama":
            from ...infrastructure.agents.ollama.factories.ollama_factory import OllamaFactory
            self.ollama_fac = OllamaFactory(api_url=api_url,
                                            model_name=model_name,
                                            system_prompt=None,
                                            api_token=api_token,
                                            tools=None,
                                            timeout=timeout,
                                            options=options)
            self.llm_embedding_repository = self.ollama_fac.create_embedding_repository()
        else:
            self.llm_embedding_repository = None


    def embed(self, text: str) -> List[float]:
        """
        Create an embedding for the given text.

        This method directly calls the EmbeddingService's embed method.

        Args:
            text: The text to create an embedding for

        Returns:
            List[float]: The embedding vector
        """
        return self.llm_embedding_repository.embed(text)