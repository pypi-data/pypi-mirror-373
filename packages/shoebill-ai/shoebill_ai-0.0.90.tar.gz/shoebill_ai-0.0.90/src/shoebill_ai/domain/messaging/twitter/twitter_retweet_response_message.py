from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterRetweetResponseMessage')

@dataclass
class TwitterRetweetResponseMessage(HaiMessage):
    """Message to respond to a request to retweet a tweet"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, tweet_id: str, success: bool, error_message: str = "") -> 'TwitterRetweetResponseMessage':
        """Create a response message for a request to retweet a tweet"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_RETWEET_RESPONSE,  # You'll need to add this to ResponseMessageTopic
            payload={
                "tweet_id": tweet_id,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def tweet_id(self) -> str:
        """Get the tweet ID from the payload"""
        return self.payload.get("tweet_id", "")

    @property
    def success(self) -> bool:
        """Get whether the retweet operation was successful"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> str:
        """Get the error message if the retweet operation failed"""
        return self.payload.get("error_message", "")