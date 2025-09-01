from typing import Dict, Union, Any, List, Optional


class OpenAIChatMessage:
    def __init__(self, role: str, content: Union[str, Dict[str, Any]], images: Optional[List[str]] = None):
        """
        Initialize a new OpenAIChatMessage.

        Args:
            role: The role of the message sender (e.g., "user", "assistant", "system").
            content: The content of the message. Can be a string for text-only messages
                    or a dictionary for structured content.
            images: Optional list of image URLs or base64-encoded images.
        """
        self.role = role
        self.content = content
        self.images = images

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary representation suitable for the OpenAI API.

        Returns:
            Dict[str, Any]: A dictionary with role and content keys.
        """
        # For OpenAI, we need to handle images differently than Ollama
        if self.images and isinstance(self.content, str):
            # For images, we need to create a content list with text and image objects
            content_list = [
                {"type": "text", "text": self.content}
            ]
            
            # Add image objects
            for image_url in self.images:
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
            
            return {
                "role": self.role,
                "content": content_list
            }
        else:
            # Standard text message
            return {
                "role": self.role,
                "content": self.content
            }