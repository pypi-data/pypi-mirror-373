from abc import abstractmethod
from typing import Optional, List, Dict, Any

from .base_repository import BaseRepository

class LlmChatRepository(BaseRepository):
    """
    Repository interface for chat interactions with an LLM.
    Implementations in the infrastructure layer should provide concrete behavior.
    """

    @abstractmethod
    def chat(self,
             user_message: str,
             system_prompt: Optional[str] = None,
             chat_history: List[dict[str, Any]] = None,
             tools: List[Dict[str, Any]] = None,
             image_path: Optional[str] = None) -> Optional[list[dict[str, Any]]]:
        """
        Chat with the LLM.

        This is the main method for chatting with the model. It can handle simple chat scenarios,
        custom messages, and tools.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the request failed.
                The dictionary includes:
                - 'message': The model's response message
                - 'tool_calls': Any tool calls made by the model (if tools were used)
                - 'eval_metrics': Any evaluation metrics
                - Other model-specific fields
        """
        ...
