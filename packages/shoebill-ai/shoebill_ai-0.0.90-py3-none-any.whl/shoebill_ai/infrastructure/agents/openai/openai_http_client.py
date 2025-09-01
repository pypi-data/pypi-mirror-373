import logging
from typing import Dict, Any, Optional, List

import openai
from openai import OpenAI


class OpenAIHttpClient:
    """
    Base HTTP client for the OpenAI API using the openai library.
    Handles authentication and common request functionality.
    """

    def __init__(self, api_url: str, api_key: str, organization: str = None, timeout: Optional[int] = None):
        """
        Initialize a new OpenAIHttpClient.

        Args:
            api_key: The API key for authentication.
            organization: Optional organization ID for API requests.
            timeout: Optional timeout in seconds for API requests.
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.organization = organization
        self.timeout = timeout or 60  # Default timeout of 60 seconds

        self.logger = logging.getLogger(__name__)

        # Initialize the OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            organization=self.organization,
            timeout=self.timeout,
            base_url=self.api_url
        )

    def post(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a request to the OpenAI API using the openai library.

        Args:
            endpoint: The endpoint to send the request to (e.g., "chat", "embeddings").
            payload: The payload to send with the request.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if the request failed.
        """
        self.logger.info(f"OpenAIHttpClient: Sending request to {endpoint} endpoint")
        self.logger.debug(f"OpenAIHttpClient: Payload: {payload}")

        try:

            model = payload.get("model")
            messages = payload.get("messages", [])
            temperature = payload.get("temperature", 0.7)

            num_predict = payload.get("num_predict", 32768)
            num_ctx = payload.get("num_ctx", 120000)
            stream = payload.get("stream", True)



            # Route to the appropriate OpenAI method based on the endpoint
            if endpoint == "chat":
                # Extract required parameters for chat

                
                # Initialize response_json
                response_json: dict[str, Any] = {
                    "message": {
                        "role": "assistant",
                        "content": ""
                    }
                }

                # Call the chat completions method
                if stream:
                    try:
                        response = self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=num_ctx,
                            stream=True
                        )
                        # Accumulate chunks
                        try:
                            for chunk in response:
                                if chunk.choices and chunk.choices[0].delta.content:
                                    response_json["message"]["content"] += chunk.choices[0].delta.content
                        except Exception as e:
                            self.logger.error(f"OpenAIHttpClient: Error during streaming chunk response: {e}")
                    except Exception as e:
                        self.logger.error(f"OpenAIHttpClient: Error during streaming chat response: {e}")
                else:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=num_ctx,
                        stream=False
                    )
                    # Format response to match the expected structure
                    if response.choices and response.choices[0].message:
                        response_json["message"]["role"] = response.choices[0].message.role
                        response_json["message"]["content"] = response.choices[0].message.content or ""
                        
                        # Add tool calls if present
                        if response.choices[0].message.tool_calls:
                            response_json["tool_calls"] = [
                                {
                                    "id": tool_call.id,
                                    "type": tool_call.type,
                                    "function": {
                                        "name": tool_call.function.name,
                                        "arguments": tool_call.function.arguments
                                    }
                                }
                                for tool_call in response.choices[0].message.tool_calls
                            ]

            elif endpoint == "embeddings":
                # Extract required parameters for embeddings
                model = payload.get("model")
                input_text = payload.get("input")
                
                # Call the embeddings method
                response = self.client.embeddings.create(
                    model=model,
                    input=input_text
                )
                
                # Format response to match the expected structure
                response_json = {
                    "embedding": response.data[0].embedding if response.data else []
                }
                
            else:
                self.logger.error(f"OpenAIHttpClient: Unsupported endpoint: {endpoint}")
                return None
                
            self.logger.info(f"OpenAIHttpClient: Received successful response from {endpoint} endpoint")
            return response_json
            
        except Exception as e:
            self.logger.error(f"OpenAIHttpClient: Error during API call to {endpoint}: {e}")
            return None