from typing import Dict, List, Any, Optional

from .. import LlmChatRepository

class VisionAgent:
    def __init__(self,
               api_url: str,
               model_name: str,
               system_prompt: str = None,
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
        self.system_prompt = system_prompt
        self.timeout = timeout
        self.options = options or {}

        self.llm_chat_repository: LlmChatRepository|None = None
        if provider == "ollama":
            from ...infrastructure.agents.ollama.factories.ollama_factory import OllamaFactory
            self.ollama_fac = OllamaFactory(api_url=self.api_url,
                                            model_name=self.model_name,
                                            system_prompt=self.system_prompt,
                                            api_token=self.api_token,
                                            tools=None,
                                            timeout=self.timeout,
                                            options=self.options)
            self.llm_chat_repository = self.ollama_fac.create_chat_repository()
        else:
            self.llm_chat_repository = None

    def chat(self,
             image_path: str,
             system_prompt: Optional[str] = None,
             chat_history: List[dict[str, Any]] = None,
             ) -> Optional[list[dict[str, Any]]]:

        chat_system_prompt = system_prompt or self.system_prompt

        return self.llm_chat_repository.chat(
            user_message="",
            system_prompt=chat_system_prompt,
            chat_history=chat_history,
            tools=None,
            image_path=image_path)
