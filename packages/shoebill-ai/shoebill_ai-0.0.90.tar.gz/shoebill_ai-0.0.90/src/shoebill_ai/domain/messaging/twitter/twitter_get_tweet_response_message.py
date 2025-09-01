from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterGetTweetResponseMessage')


@dataclass
class TwitterGetTweetResponseMessage(HaiMessage):
    """Message to respond to a request to get a tweet by its ID"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls,
                       tweet_id: str,
                       success: bool,
                       tweet: Optional[Dict[str, Any]] = None,
                       error_message: str = "") -> 'TwitterGetTweetResponseMessage':
        """Create a response message for a request to get a tweet"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_TWEET_RESPONSE,  # You'll need to add this to ResponseMessageTopic
            payload={
                "tweet_id": tweet_id,
                "success": success,
                "tweet": tweet,
                "error_message": error_message
            },
        )

    @property
    def tweet_id(self) -> str:
        """Get the tweet ID that was requested"""
        return self.payload.get("tweet_id", "")

    @property
    def success(self) -> bool:
        """Get whether the get tweet operation was successful"""
        return self.payload.get("success", False)

    @property
    def tweet(self) -> Optional[Dict[str, Any]]:
        """Get the tweet data if the operation was successful"""
        return self.payload.get("tweet", None)

    @property
    def error_message(self) -> str:
        """Get the error message if the get tweet operation failed"""
        return self.payload.get("error_message", "")