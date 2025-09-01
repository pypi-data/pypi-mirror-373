from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterPostTweetRequestMessage')

@dataclass
class TwitterPostTweetRequestMessage(HaiMessage):
    """Message to request posting a new tweet"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, text: str) -> 'TwitterPostTweetRequestMessage':
        """Create a message requesting to post a new tweet"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_POST_TWEET,  # You'll need to add this to RequestMessageTopic
            payload={
                "text": text
            },
        )

    @property
    def text(self) -> str:
        """Get the text content of the tweet from the payload"""
        return self.payload.get("text", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterPostTweetRequestMessage':
        """Create a TwitterPostTweetRequestMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            text=payload.get("text", "")
        )