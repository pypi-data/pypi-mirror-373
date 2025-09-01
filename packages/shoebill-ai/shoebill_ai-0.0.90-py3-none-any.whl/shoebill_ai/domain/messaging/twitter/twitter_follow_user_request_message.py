from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterFollowUserRequestMessage')

@dataclass
class TwitterFollowUserRequestMessage(HaiMessage):
    """Message to request following a Twitter user"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, user_id: str) -> 'TwitterFollowUserRequestMessage':
        """Create a message requesting to follow a Twitter user"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_FOLLOW_USER,  # You'll need to add this to RequestMessageTopic
            payload={
                "user_id": user_id
            },
        )

    @property
    def user_id(self) -> str:
        """Get the user ID from the payload"""
        return self.payload.get("user_id", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterFollowUserRequestMessage':
        """Create a TwitterFollowUserRequestMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            user_id=payload.get("user_id", "")
        )