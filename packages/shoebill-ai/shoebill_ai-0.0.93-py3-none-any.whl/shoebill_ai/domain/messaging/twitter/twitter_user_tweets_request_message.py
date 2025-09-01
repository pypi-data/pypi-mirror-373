from dataclasses import dataclass
from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

@dataclass
class TwitterUserTweetsRequestMessage(HaiMessage):
    """Message to request tweets from a Twitter user"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, user_id: str, max_results: int = 100,
                       include_replies: bool = False,
                       include_retweets: bool = False) -> 'TwitterUserTweetsRequestMessage':
        """Create a message requesting tweets from a Twitter user"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_USER_TWEETS,
            payload={
                "user_id": user_id,
                "max_results": max_results,
                "include_replies": include_replies,
                "include_retweets": include_retweets
            },
        )

    @property
    def user_id(self) -> str:
        """Get the user ID from the payload"""
        return self.payload.get("user_id")

    @property
    def max_results(self) -> int:
        """Get the maximum number of results from the payload"""
        return self.payload.get("max_results", 100)

    @property
    def include_replies(self) -> bool:
        """Get whether to include replies from the payload"""
        return self.payload.get("include_replies", False)

    @property
    def include_retweets(self) -> bool:
        """Get whether to include retweets from the payload"""
        return self.payload.get("include_retweets", False)

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterUserTweetsRequestMessage':
        """Create a TwitterUserTweetsRequestMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            user_id=payload.get("user_id", ""),
            max_results=payload.get("max_results", 100),
            include_replies=payload.get("include_replies", False),
            include_retweets=payload.get("include_retweets", False)
        )
