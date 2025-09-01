from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterRetweetRequestMessage')

@dataclass
class TwitterRetweetRequestMessage(HaiMessage):
    """Message to request retweeting a tweet"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, tweet_id: str) -> 'TwitterRetweetRequestMessage':
        """Create a message requesting to retweet a tweet"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_RETWEET,  # You'll need to add this to RequestMessageTopic
            payload={
                "tweet_id": tweet_id
            },
        )

    @property
    def tweet_id(self) -> str:
        """Get the tweet ID from the payload"""
        return self.payload.get("tweet_id", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterRetweetRequestMessage':
        """Create a TwitterRetweetRequestMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            tweet_id=payload.get("tweet_id", "")
        )