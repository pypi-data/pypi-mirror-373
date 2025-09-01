from typing import Optional, List, Dict, Any

from .....domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from .base_openai_repository import BaseOpenAIRepository
from ..models.openai_chat_message import OpenAIChatMessage
from ..models.openai_chat_session import OpenAIChatSession


class OpenAIChatRepository(BaseOpenAIRepository, LlmChatRepository):
    """
    Repository for chat interactions with OpenAI models.
    """

    def __init__(self, api_key: str, model_name: str, system_prompts: list[str] = None, temperature: float = None, 
                 seed: int = None, organization: str = None, tools: List[Dict[str, Any]] = None, 
                 timeout: int = None, max_tokens: int = None):
        """
        Initialize a new OpenAIChatRepository.

        Args:
            api_key: The API key for authentication.
            model_name: The name of the model to use.
            system_prompts: Optional list of system prompts to use.
            temperature: Optional temperature to use for generation.
            seed: Optional seed for reproducibility.
            organization: Optional organization ID for API requests.
            tools: Optional list of tools to make available to the model.
            timeout: Optional timeout in seconds for API requests.
            max_tokens: The maximum number of tokens to generate.
        """
        super().__init__(api_key, model_name, organization, timeout)
        self.temperature = temperature
        self.seed = seed
        self.system_prompts = system_prompts or []
        self.tools = tools or []
        self.max_tokens = max_tokens

    def chat(self, user_message: str = None, session_id: str = None, chat_history: List[dict] = None, 
             format: Dict[str, Any] = None, system_prompt: str = None, 
             messages: List[Any] = None, tools: List[Dict[str, Any]] = None,
             stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Chat with the model using the OpenAI API.

        This is the main method for chatting with the model. It can handle simple chat scenarios,
        custom messages, and tools.

        Args:
            user_message: The user's message. Can be a string or a dictionary with 'content' and optional 'images'.
                         Not required if messages is provided.
            session_id: The ID of the chat session. Not required if messages is provided.
            chat_history: Optional chat history to include in the conversation.
                         Each message can include 'role', 'content', and optional 'images'.
            format: Optional JSON schema defining the structure of the expected output.
            system_prompt: Optional system prompt to override the default.
            messages: Optional custom list of messages to send to the model. If provided, user_message,
                     session_id, and chat_history are ignored.
            tools: Optional list of tools to make available to the model for this chat session.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the request failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        # If messages is provided, use it directly with the appropriate method
        if messages is not None:
            logger.info(f"OpenAIChatRepository: Using provided messages list with {len(messages)} messages")

            # If tools are provided, use _chat_with_messages_and_tools
            if tools is not None:
                logger.info(f"OpenAIChatRepository: Using provided tools with {len(tools)} tools")
                return self._chat_with_messages_and_tools(messages, tools, format, system_prompt, stream)
            else:
                # Otherwise, use _chat_with_messages
                return self._chat_with_messages(messages, format, system_prompt, stream)

        # If no messages are provided, we need user_message and session_id
        if user_message is None or session_id is None:
            logger.error("OpenAIChatRepository: user_message and session_id are required when messages is not provided")
            return None

        logger.info(f"OpenAIChatRepository: Starting chat with session_id {session_id}")
        # Handle both string and dictionary user messages for logging
        if isinstance(user_message, str):
            logger.debug(f"OpenAIChatRepository: User message: {user_message[:50]}...")
        else:
            logger.debug(f"OpenAIChatRepository: User message: {user_message}")
        logger.debug(f"OpenAIChatRepository: Chat history length: {len(chat_history) if chat_history else 0}")

        # Start with system prompts and user message
        messages = []

        # Use provided system_prompt if available, otherwise use the default system_prompts
        if system_prompt:
            messages.append(OpenAIChatMessage("system", system_prompt))
            logger.debug(f"OpenAIChatRepository: Added provided system prompt: {system_prompt[:50]}...")
        else:
            for prompt in self.system_prompts:
                messages.append(OpenAIChatMessage("system", prompt))
                # Handle both string and dictionary system prompts for logging
                if isinstance(prompt, str):
                    logger.debug(f"OpenAIChatRepository: Added system prompt: {prompt[:50]}...")
                else:
                    logger.debug(f"OpenAIChatRepository: Added system prompt: {prompt}")

        # Add chat history if provided
        if chat_history:
            logger.info(f"OpenAIChatRepository: Adding {len(chat_history)} messages from chat history")
            for message in chat_history:
                role = message.get("role", "user")
                content = message.get("content", "")
                images = message.get("images", None)

                # Create the chat message with images if they exist
                if images:
                    chat_msg = OpenAIChatMessage(role, content, images)
                    logger.debug(f"OpenAIChatRepository: Added {role} message from history with {len(images)} images")
                else:
                    chat_msg = OpenAIChatMessage(role, content)
                    # Handle both string and dictionary content for logging
                    if isinstance(content, str):
                        logger.debug(f"OpenAIChatRepository: Added {role} message from history: {content[:50]}...")
                    else:
                        logger.debug(f"OpenAIChatRepository: Added {role} message from history: {content}")

                messages.append(chat_msg)

        # Add the current user message
        # Check if user_message is a dictionary with content and images
        if isinstance(user_message, dict):
            content = user_message.get("content", "")
            images = user_message.get("images", None)
            if images:
                messages.append(OpenAIChatMessage("user", content, images))
                logger.info(f"OpenAIChatRepository: Added current user message with {len(images)} images")
            else:
                messages.append(OpenAIChatMessage("user", content))
                logger.info(f"OpenAIChatRepository: Added current user message")
        else:
            # User message is a string
            messages.append(OpenAIChatMessage("user", user_message))
            logger.info(f"OpenAIChatRepository: Added current user message")

        # Create a session
        session = OpenAIChatSession(session_id, messages)
        logger.info(f"OpenAIChatRepository: Created chat session with {len(session.messages)} messages")

        # If tools are provided, use _chat_with_messages_and_tools
        if tools is not None:
            logger.info(f"OpenAIChatRepository: Using provided tools with {len(tools)} tools")
            result = self._chat_with_messages_and_tools(session.messages, tools, format, system_prompt, stream)
        else:
            # Otherwise, use _chat_with_messages
            logger.info(f"OpenAIChatRepository: Calling _chat_with_messages")
            result = self._chat_with_messages(session.messages, format, system_prompt, stream)

        if result:
            logger.info(f"OpenAIChatRepository: Received response")
            logger.debug(f"OpenAIChatRepository: Response: {str(result)[:100]}...")
        else:
            logger.error(f"OpenAIChatRepository: Failed to get response")

        return result

    def _chat_with_messages(self, messages: List[Any], format: Dict[str, Any] = None, system_prompt: str = None, stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Private method to chat with the model using a custom list of messages.

        This method allows for more flexibility in message formatting, such as including
        document messages or other special message types.

        Args:
            messages: The list of messages to send to the model. Each message should have
                     'role' and 'content' attributes or keys.
            format: Optional JSON schema defining the structure of the expected output.
            system_prompt: Optional system prompt to override the default.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the request failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"OpenAIChatRepository: Starting chat_with_messages with {len(messages)} messages")

        # If system_prompt is provided, check if we need to add it or replace an existing system message
        if system_prompt:
            logger.debug(f"OpenAIChatRepository: Using provided system prompt: {system_prompt[:50]}...")

            # Create a new messages list with the system prompt at the beginning
            new_messages = []
            system_message_added = False

            # Check if there's already a system message
            for msg in messages:
                role = getattr(msg, "role", "unknown") if hasattr(msg, "role") else msg.get("role", "unknown")

                # If this is the first system message, replace it with our new system prompt
                if role == "system" and not system_message_added:
                    if hasattr(msg, "role"):
                        # It's an object with attributes
                        msg.content = system_prompt
                    else:
                        # It's a dictionary
                        msg["content"] = system_prompt
                    system_message_added = True

                new_messages.append(msg)

            # If no system message was found, add one at the beginning
            if not system_message_added:
                new_messages.insert(0, OpenAIChatMessage("system", system_prompt))

            messages = new_messages

        # Log the first few messages to help with debugging
        for i, msg in enumerate(messages[:3]):  # Log only first 3 messages to avoid excessive logging
            role = getattr(msg, "role", "unknown") if hasattr(msg, "role") else msg.get("role", "unknown")
            content = getattr(msg, "content", "") if hasattr(msg, "content") else msg.get("content", "")
            # Handle both string and dictionary content for logging
            if isinstance(content, str):
                logger.debug(f"OpenAIChatRepository: Message {i+1} - Role: {role}, Content: {content[:50]}...")
            else:
                logger.debug(f"OpenAIChatRepository: Message {i+1} - Role: {role}, Content: {content}")

        if len(messages) > 3:
            logger.debug(f"OpenAIChatRepository: ... and {len(messages) - 3} more messages")

        # Call the OpenAI API
        return self._call_openai_api(messages, format, stream)

    def _chat_with_messages_and_tools(self, messages: List[Any], tools: List[Dict[str, Any]] = None, format: Dict[str, Any] = None, system_prompt: str = None, stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Private method to chat with the model using a custom list of messages and specific tools.

        This method allows for more flexibility in message formatting and tool usage,
        without modifying the repository's default tools.

        Args:
            messages: The list of messages to send to the model. Each message should have
                     'role' and 'content' attributes or keys.
            tools: Optional list of tools to make available to the model for this chat session.
                  If None, uses the repository's default tools.
            format: Optional JSON schema defining the structure of the expected output.
            system_prompt: Optional system prompt to override the default.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the request failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"OpenAIChatRepository: Starting chat_with_messages_and_tools with {len(messages)} messages")

        # Use the provided tools or the repository's default tools
        tools_to_use = tools if tools is not None else self.tools
        logger.info(f"OpenAIChatRepository: Using {len(tools_to_use)} tools")

        # Format messages and call the API with tools
        formatted_messages = self._format_messages(messages)
        logger.debug(f"OpenAIChatRepository: Formatted {len(formatted_messages)} messages")

        # Create the payload for the API call
        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "tools": tools_to_use,
            "stream": stream
        }

        # Add temperature if provided
        if self.temperature is not None:
            payload["temperature"] = self.temperature
            logger.debug(f"OpenAIChatRepository: Using temperature {self.temperature}")

        # Add max_tokens if provided
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
            logger.debug(f"OpenAIChatRepository: Using max_tokens {self.max_tokens}")

        # Call the API
        logger.info(f"OpenAIChatRepository: Calling OpenAI API with tools")
        return self.http_client.post("chat", payload)

    def _format_messages(self, messages: List[Any]) -> List[Dict[str, Any]]:
        """
        Format messages for the OpenAI API.

        Args:
            messages: The list of messages to format. Each message should have
                     'role' and 'content' attributes or keys.

        Returns:
            List[Dict[str, Any]]: The formatted messages.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"OpenAIChatRepository: Formatting {len(messages)} messages")
        result = []

        for msg in messages:
            # Extract role and content from the message
            if hasattr(msg, "role") and hasattr(msg, "content"):
                # It's an object with attributes (like OpenAIChatMessage)
                role = msg.role
                content = msg.content
                # Check if it has images
                images = getattr(msg, "images", None) if hasattr(msg, "images") else None
                
                # Use the to_dict method if available
                if hasattr(msg, "to_dict") and callable(getattr(msg, "to_dict")):
                    formatted_msg = msg.to_dict()
                    result.append(formatted_msg)
                    logger.debug(f"OpenAIChatRepository: Added message with role '{role}' using to_dict()")
                    continue
            else:
                # It's a dictionary or something else
                role = msg.get("role", "user") if hasattr(msg, "get") else "user"
                content = msg.get("content", "") if hasattr(msg, "get") else str(msg)
                # Check if it has images
                images = msg.get("images", None) if hasattr(msg, "get") else None

            # Create the formatted message
            if images:
                # For OpenAI, we need to create a content list with text and image objects
                if isinstance(content, str):
                    content_list = [
                        {"type": "text", "text": content}
                    ]
                    
                    # Add image objects
                    for image_url in images:
                        if image_url.startswith("http"):
                            # URL image
                            content_list.append({
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            })
                        else:
                            # Base64 image
                            content_list.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_url}"}
                            })
                    
                    formatted_msg = {
                        "role": role,
                        "content": content_list
                    }
                else:
                    # If content is not a string, just use it as is
                    formatted_msg = {
                        "role": role,
                        "content": content
                    }
            else:
                # Standard text message
                formatted_msg = {
                    "role": role,
                    "content": content
                }

            result.append(formatted_msg)
            logger.debug(f"OpenAIChatRepository: Added message with role '{role}' and content: {str(content)[:50]}...")

        logger.info(f"OpenAIChatRepository: Formatted {len(result)} messages in standard format")
        return result

    def _call_openai_api(self, messages: List[Any], format: Dict[str, Any] = None, stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Call the OpenAI API with the given messages.

        Args:
            messages: The messages to send to the API. Each message should have 'role' and 'content' attributes.
                     May also include 'images' for multimodal models.
            format: Optional JSON schema defining the structure of the expected output.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the request failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"OpenAIChatRepository: Preparing chat request for model {self.model_name}")

        # Format messages for the OpenAI API
        formatted_messages = self._format_messages(messages)

        # Create the payload for the API call
        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": stream
        }

        # Add temperature if provided
        if self.temperature is not None:
            payload["temperature"] = self.temperature
            logger.debug(f"OpenAIChatRepository: Using temperature {self.temperature}")

        # Add max_tokens if provided
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
            logger.debug(f"OpenAIChatRepository: Using max_tokens {self.max_tokens}")

        # Add response format if provided
        if format:
            # OpenAI expects a specific format for structured output
            payload["response_format"] = {"type": "json_object"}
            logger.debug(f"OpenAIChatRepository: Using JSON response format for structured output")

        # Call the API
        logger.info(f"OpenAIChatRepository: Calling OpenAI API")
        return self.http_client.post("chat", payload)