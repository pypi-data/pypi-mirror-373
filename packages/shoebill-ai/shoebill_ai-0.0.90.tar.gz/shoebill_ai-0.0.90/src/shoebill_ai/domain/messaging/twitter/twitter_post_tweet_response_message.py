from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterPostTweetResponseMessage')


@dataclass
class TwitterPostTweetResponseMessage(HaiMessage):
    """Message to respond to a request to post a new tweet"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls,
                       success: bool,
                       tweet: Optional[Dict[str, Any]] = None,
                       error_message: str = "") -> 'TwitterPostTweetResponseMessage':
        """Create a response message for a request to post a new tweet"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_POST_TWEET_RESPONSE,  # You'll need to add this to ResponseMessageTopic
            payload={
                "success": success,
                "tweet": tweet,
                "error_message": error_message
            },
        )

    @property
    def success(self) -> bool:
        """Get whether the post tweet operation was successful"""
        return self.payload.get("success", False)

    @property
    def tweet(self) -> Optional[Dict[str, Any]]:
        """Get the posted tweet data if the operation was successful"""
        return self.payload.get("tweet", None)

    @property
    def error_message(self) -> str:
        """Get the error message if the post tweet operation failed"""
        return self.payload.get("error_message", "")