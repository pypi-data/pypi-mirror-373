from typing import Optional, List, Dict, Any

from ...utils.image_utils import encode_image
from .....domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from .base_ollama_repository import BaseOllamaRepository

import logging

class OllamaChatRepository(BaseOllamaRepository, LlmChatRepository):
    """
    Repository for chat interactions using the Ollama API.
    """

    def __init__(self,
                 api_url: str,
                 model_name: str,
                 system_prompt: str = None,
                 api_token: str = None,
                 tools: List[Dict[str, Any]] = None,
                 timeout: int = 60,
                 options: Dict[str, Any] = None):
        """
        Initialize a new OllamaChatRepository.

        Args:
            api_url: The base URL of the Ollama API.
            model_name: The name of the model to use.
            system_prompt: Optional system prompt to use for the chat.
            api_token: Optional API token for authentication.
            tools: Optional list of tools to make available to the model.
            timeout: Optional timeout in seconds for API requests.
        """
        super().__init__(api_url, model_name, api_token, timeout)

        self.options = options or {}
        self.system_prompt = system_prompt
        self.tools = tools or []

        self.logger = logging.getLogger(__name__)

    def chat(self,
             user_message: str,
             system_prompt: Optional[str] = None,
             chat_history: List[dict[str, Any]] = None,
             tools: List[Dict[str, Any]] = None,
             image_path: Optional[str] = None) -> Optional[list[dict[str, Any]]]:
        """
        Chat with the model using the Ollama API.

        This is the main method for chatting with the model. It can handle simple chat scenarios,
        custom messages, and tools.
        Returns:
            Optional[list[dict[str, Any]]]: The model's response, or None if the request failed.
        """
        messages: List[dict[str, Any]] = []
        if chat_history:
            messages = chat_history.copy()
        if system_prompt:
            #self.logger.debug(f"OllamaChatRepository: Using custom system prompt: {system_prompt}")
            messages.append({"role": "system", "content": system_prompt})
        else:
            #self.logger.debug(f"OllamaChatRepository: Using default system prompt: {self.system_prompt}")
            messages.append({"role": "system", "content": self.system_prompt})

        if image_path:
            image_base64 = encode_image(image_path)
            messages.append({"role": "user", "content": user_message, "images": [image_base64]})
        else:
            messages.append({"role": "user", "content": user_message})

        result = self._call_ollama_api(messages, tools)

        if result:
            messages.append({"role": "assistant", "content": result})
        else:
            messages.append({"role": "assistant", "content": "Failed to get response"})

        return messages

    def _call_ollama_api(self, messages: List[dict[str, Any]], tools: List[Dict[str, Any]]) -> Optional[str]:
        """
        Call the Ollama API with the given messages using the ollama-python library.

        Args:
            messages: The messages to send to the API. Each message should have 'role' and 'content' attributes.
                     May also include 'images' for multimodal models.

        Returns:
            Optional[str]: The model's response, or None if the request failed.
        """

        self.logger.info(f"OllamaChatRepository: Preparing chat request for model {self.model_name}")

        # Create the payload for the ollama-python library
        payload = self.options.copy()
        payload["model"] = self.model_name
        payload["messages"] = messages

        # Always use the chat endpoint
        endpoint = "chat"
        self.logger.info(f"OllamaChatRepository: Sending request to {endpoint} endpoint")

        # Call the API endpoint using the ollama-python library
        available_tools = self.tools
        if tools is not None:
            available_tools = tools

        response_data = self.http_client.post(endpoint, payload, tools=available_tools)
        if response_data:
            self.logger.info("OllamaChatRepository: Received response from API")
            content = response_data.get("message", {}).get("content", "")
            return content

        self.logger.error("OllamaChatRepository: Failed to get response from API")
        return None