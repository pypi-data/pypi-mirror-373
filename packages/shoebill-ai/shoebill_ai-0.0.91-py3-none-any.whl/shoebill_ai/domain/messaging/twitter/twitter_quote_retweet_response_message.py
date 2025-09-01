from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterQuoteRetweetResponseMessage')


@dataclass
class TwitterQuoteRetweetResponseMessage(HaiMessage):
    """Message to respond to a request to quote retweet a tweet"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls,
                       original_tweet_id: str,
                       success: bool,
                       quote_tweet: Optional[Dict[str, Any]] = None,
                       error_message: str = "") -> 'TwitterQuoteRetweetResponseMessage':
        """Create a response message for a request to quote retweet a tweet"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_QUOTE_RETWEET_RESPONSE,
            # You'll need to add this to ResponseMessageTopic
            payload={
                "original_tweet_id": original_tweet_id,
                "success": success,
                "quote_tweet": quote_tweet,
                "error_message": error_message
            },
        )

    @property
    def original_tweet_id(self) -> str:
        """Get the original tweet ID that was quote retweeted"""
        return self.payload.get("original_tweet_id", "")

    @property
    def success(self) -> bool:
        """Get whether the quote retweet operation was successful"""
        return self.payload.get("success", False)

    @property
    def quote_tweet(self) -> Optional[Dict[str, Any]]:
        """Get the quote tweet data if the operation was successful"""
        return self.payload.get("quote_tweet", None)

    @property
    def error_message(self) -> str:
        """Get the error message if the quote retweet operation failed"""
        return self.payload.get("error_message", "")