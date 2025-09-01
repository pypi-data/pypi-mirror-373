import logging
from typing import Dict, Any, Optional, List

import ollama


class OllamaHttpClient:
    """
    Base HTTP client for the Ollama API using the ollama-python library.
    Handles authentication and common request functionality.
    """

    def __init__(self, api_url: str, api_token: str = None, timeout: Optional[int] = None):
        """
        Initialize a new OllamaHttpClient.

        Args:
            api_url: The base URL of the Ollama API.
            api_token: Optional API token for authentication.
            timeout: Optional timeout in seconds for API requests.
        """
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token
        self.timeout = timeout

        self.logger = logging.getLogger(__name__)

        self.headers = {}
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"

        # Configure the ollama client with the API URL and timeout
        self.client = ollama.Client(host=self.api_url, headers=self.headers, timeout=self.timeout)

    def _get_headers(self) -> Dict[str, str]:
        """
        Get the headers for the request, including authentication if available.

        Returns:
            Dict[str, str]: The headers for the request.
        """
        return self.headers

    def post(self, endpoint: str, payload: Dict[str, Any], tools: List[dict] = None) -> Optional[Dict[str, Any]]:
        """
        Send a POST request to the Ollama API using the ollama-python library.

        Args:
            endpoint: The endpoint to send the request to (without the base URL).
            payload: The payload to send with the request.
            tools: The tools to use for the request.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if the request failed.
        """
        self.logger.info(f"OllamaHttpClient: Sending request to {endpoint} endpoint")
        self.logger.debug(f"OllamaHttpClient: Headers: {self.headers}")

        try:

            model = payload.get("model")
            messages = payload.get("messages", [])
            temperature = payload.get("temperature", 0.7)
            seed = payload.get("seed", 20240628)
            top_p = payload.get("top_p", 0.8)
            top_k = payload.get("top_k", 20)
            min_p = payload.get("min_p", 0.0)
            num_predict = payload.get("num_predict", 32768)
            num_ctx = payload.get("num_ctx", 120000)
            stream = payload.get("stream", True)
            prompt = payload.get("prompt", "")

            options: dict[str, Any] = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "min_p": min_p,
                "num_predict": num_predict,
                "seed": seed,
                "num_ctx": num_ctx,
            }

            options = {k: v for k, v in options.items() if v is not None}

            self.logger.debug(f"OllamaHttpClient: Options: {options}")

            # Route to the appropriate ollama-python method based on the endpoint
            if endpoint == "chat":
                response_json: dict[str, Any] = {
                    "message": {
                        "role": "assistant",
                        "content": ""
                    }
                }

                if stream:
                    try:
                        response = self.client.chat(
                            model=model,
                            messages=messages,
                            options=options,
                            stream=True,
                            tools=tools
                        )
                        try:
                            for chunk in response:
                                if "message" in chunk and "content" in chunk["message"]:
                                    response_json["message"]["content"] += chunk["message"]["content"]
                                if "message" in chunk and "tool_calls" in chunk["message"]:
                                    response_json["message"]["tool_calls"] += chunk["message"]["tool_calls"]

                                if chunk.get("done", False):
                                    break
                        except Exception as e:
                            self.logger.error(f"OllamaHttpClient: Error during streaming chunk response: {e}")
                    except Exception as e:
                        self.logger.error(f"OllamaHttpClient: Error during streaming chat response: {e}")

                else:
                    response = self.client.chat(
                        model=model,
                        messages=messages,
                        options=options,
                        stream=False,
                        tools=tools
                    )
                    # Format response to match the expected structure
                    response_json["message"]["content"] = response.get("message", {}).get("content", "")
                    response_json["message"]["tool_calls"] = response.get("message", {}).get("tool_calls", [])

            elif endpoint == "generate":
                self.logger.warning("OllamaHttpClient: generate endpoint not yet implemented")
                return None

            elif endpoint == "embeddings":

                response = self.client.embeddings(
                    model=model,
                    prompt=prompt,
                )

                # Format response to match the expected structure
                response_json = {
                    "embedding": response.get("embedding", [])
                }

            else:
                self.logger.error(f"OllamaHttpClient: Unsupported endpoint: {endpoint}")
                return None

            self.logger.info(f"OllamaHttpClient: Received successful response from {endpoint} endpoint")
            self.logger.debug(f"OllamaHttpClient: Response body: {response_json}")

            return response_json

        except Exception as e:
            self.logger.error(f"OllamaHttpClient: Error during API call to {endpoint}: {e}")
            return None
