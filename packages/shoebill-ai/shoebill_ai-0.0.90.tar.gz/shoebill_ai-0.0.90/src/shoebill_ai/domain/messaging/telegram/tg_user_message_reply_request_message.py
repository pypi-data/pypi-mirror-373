from typing import Type, TypeVar, Dict, Any

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class TelegramUserMessageReplyRequestMessage(HaiMessage):
    """Message containing user message data"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, message: str, chat_id: int,
                       message_id: int) -> 'TelegramUserMessageReplyRequestMessage':

        payload = {
            "message": message,
            "chat_id": chat_id,
            "message_id": message_id,
        }

        return cls.create(
            topic=RequestMessageTopic.TG_CHAT_REPLY,
            payload=payload
        )

    @property
    def message(self) -> str:
        """Get the message content from the payload"""
        return self.payload.get("message", "")

    @property
    def chat_id(self) -> int:
        """Get the Telegram chat ID from the payload"""
        return self.payload.get("chat_id", 0)

    @property
    def message_id(self) -> int:
        """Get the Telegram message ID from the payload"""
        return self.payload.get("message_id", 0)

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TelegramUserMessageReplyRequestMessage':
        payload = message.payload

        return cls.create_message(
            message=payload.get("message", ""),
            chat_id=payload.get("chat_id"),
            message_id=payload.get("message_id")
        )

