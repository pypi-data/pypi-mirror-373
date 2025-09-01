from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterHomeTimelineRequestMessage')

@dataclass
class TwitterHomeTimelineRequestMessage(HaiMessage):
    """Message to request the home timeline for the authenticated Twitter user"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, max_results: int = 100,
                      include_replies: bool = True,
                      include_retweets: bool = True) -> 'TwitterHomeTimelineRequestMessage':
        """Create a message requesting the Twitter home timeline"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_HOME_TIMELINE,  # You'll need to add this to RequestMessageTopic
            payload={
                "max_results": max_results,
                "include_replies": include_replies,
                "include_retweets": include_retweets
            },
        )

    @property
    def max_results(self) -> int:
        """Get the maximum number of results from the payload"""
        return self.payload.get("max_results", 100)

    @property
    def include_replies(self) -> bool:
        """Get whether to include replies from the payload"""
        return self.payload.get("include_replies", True)

    @property
    def include_retweets(self) -> bool:
        """Get whether to include retweets from the payload"""
        return self.payload.get("include_retweets", True)

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterHomeTimelineRequestMessage':
        """Create a TwitterHomeTimelineRequestMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            max_results=payload.get("max_results", 100),
            include_replies=payload.get("include_replies", True),
            include_retweets=payload.get("include_retweets", True)
        )