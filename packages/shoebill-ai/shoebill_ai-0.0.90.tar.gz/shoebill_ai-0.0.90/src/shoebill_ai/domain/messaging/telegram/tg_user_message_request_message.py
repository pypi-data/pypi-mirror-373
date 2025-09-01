from typing import Type, TypeVar, Dict, Any, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class TelegramUserMessageRequestMessage(HaiMessage):
    """Message containing user message data"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, message: str, user_id: str, username: str,
                       chat_id: str,
                       message_id: str,
                       replied_to_text: Optional[str] = None) -> 'TelegramUserMessageRequestMessage':
        """Create a message with user message data

        Args:
            message: The cleaned message content
            user_id: The ID of the user
            username: The username of the user
            replied_to_text: The text being replied to, if any
            chat_id: The Telegram chat ID
            message_id: The Telegram message ID

        Returns:
            A new TelegramUserMessageRequestMessage instance
        """
        payload = {
            "message": message,
            "user_id": user_id,
            "username": username,
            "chat_id" : chat_id,
            "message_id" : message_id
        }

        if replied_to_text:
            payload["replied_to_text"] = replied_to_text

        return cls.create(
            topic=RequestMessageTopic.TG_USER_CHAT_SEND,
            payload=payload
        )

    @property
    def message(self) -> str:
        """Get the message content from the payload"""
        return self.payload.get("message", "")

    @property
    def user_id(self) -> str:
        """Get the user ID from the payload"""
        return self.payload.get("user_id", "")

    @property
    def username(self) -> str:
        """Get the username from the payload"""
        return self.payload.get("username", "")

    @property
    def replied_to_text(self) -> str:
        """Get the replied to text from the payload"""
        return self.payload.get("replied_to_text", "")

    @property
    def chat_id(self) -> int:
        """Get the Telegram chat ID from the payload"""
        return self.payload.get("chat_id", 0)

    @property
    def message_id(self) -> int:
        """Get the Telegram message ID from the payload"""
        return self.payload.get("message_id", 0)

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TelegramUserMessageRequestMessage':
        payload = message.payload

        return cls.create_message(
            message=payload.get("message", ""),
            user_id=payload.get("user_id", ""),
            username=payload.get("username", ""),
            replied_to_text=payload.get("replied_to_text", ""),
            chat_id=payload.get("chat_id"),
            message_id=payload.get("message_id")
        )

