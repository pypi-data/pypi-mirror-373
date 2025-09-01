from dataclasses import dataclass
from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

@dataclass
class TwitterRepliesAndMentionsRequestMessage(HaiMessage):
    """Message to request replies and mentions from Twitter"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, max_results: int = 100, 
                       hours_ago: int = 24) -> 'TwitterRepliesAndMentionsRequestMessage':
        """Create a message requesting replies and mentions from Twitter"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_REPLIES_AND_MENTIONS,
            payload={
                "max_results": max_results,
                "hours_ago": hours_ago
            },
        )

    @property
    def max_results(self) -> int:
        """Get the maximum number of results from the payload"""
        return self.payload.get("max_results", 100)

    @property
    def hours_ago(self) -> int:
        """Get the number of hours to look back from the payload"""
        return self.payload.get("hours_ago", 24)

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterRepliesAndMentionsRequestMessage':
        """Create a TwitterRepliesAndMentionsRequestMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            max_results=payload.get("max_results", 100),
            hours_ago=payload.get("hours_ago", 24)
        )