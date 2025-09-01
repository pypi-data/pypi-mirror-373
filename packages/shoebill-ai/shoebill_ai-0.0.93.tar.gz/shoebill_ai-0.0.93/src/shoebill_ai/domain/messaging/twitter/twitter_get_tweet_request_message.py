from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterGetTweetRequestMessage')

@dataclass
class TwitterGetTweetRequestMessage(HaiMessage):
    """Message to request getting a tweet by its ID"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, tweet_id: str) -> 'TwitterGetTweetRequestMessage':
        """Create a message requesting to get a tweet by its ID"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_TWEET,  # You'll need to add this to RequestMessageTopic
            payload={
                "tweet_id": tweet_id
            },
        )

    @property
    def tweet_id(self) -> str:
        """Get the tweet ID from the payload"""
        return self.payload.get("tweet_id", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterGetTweetRequestMessage':
        """Create a TwitterGetTweetRequestMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            tweet_id=payload.get("tweet_id", "")
        )