from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterReplyRequestMessage')


@dataclass
class TwitterReplyRequestMessage(HaiMessage):
    """Message to request replying to a tweet"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, tweet_id: str, text: str) -> 'TwitterReplyRequestMessage':
        """Create a message requesting to reply to a tweet"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_REPLY,  # You'll need to add this to RequestMessageTopic
            payload={
                "tweet_id": tweet_id,
                "text": text
            },
        )

    @property
    def tweet_id(self) -> str:
        """Get the tweet ID to reply to from the payload"""
        return self.payload.get("tweet_id", "")

    @property
    def text(self) -> str:
        """Get the text content of the reply from the payload"""
        return self.payload.get("text", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterReplyRequestMessage':
        """Create a TwitterReplyRequestMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            tweet_id=payload.get("tweet_id", ""),
            text=payload.get("text", "")
        )