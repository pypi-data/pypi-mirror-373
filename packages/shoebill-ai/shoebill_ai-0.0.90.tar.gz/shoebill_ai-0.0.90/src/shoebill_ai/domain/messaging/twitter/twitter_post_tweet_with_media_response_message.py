from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterPostTweetWithMediaResponseMessage')


@dataclass
class TwitterPostTweetWithMediaResponseMessage(HaiMessage):
    """Message to respond to a request to post a new tweet with media"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls,
                       success: bool,
                       tweet: Optional[Dict[str, Any]] = None,
                       error_message: str = "") -> 'TwitterPostTweetWithMediaResponseMessage':
        """Create a response message for a request to post a new tweet with media"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_POST_TWEET_WITH_MEDIA_RESPONSE,
            payload={
                "success": success,
                "tweet": tweet,
                "error_message": error_message
            },
        )

    @property
    def success(self) -> bool:
        """Get whether the post tweet with media operation was successful"""
        return self.payload.get("success", False)

    @property
    def tweet(self) -> Optional[Dict[str, Any]]:
        """Get the posted tweet data if the operation was successful"""
        return self.payload.get("tweet", None)

    @property
    def error_message(self) -> str:
        """Get the error message if the post tweet with media operation failed"""
        return self.payload.get("error_message", "")