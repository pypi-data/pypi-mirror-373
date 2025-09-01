from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterFollowUserResponseMessage')

@dataclass
class TwitterFollowUserResponseMessage(HaiMessage):
    """Message to respond to a request to follow a Twitter user"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, user_id: str, success: bool, error_message: str = "") -> 'TwitterFollowUserResponseMessage':
        """Create a response message for a request to follow a Twitter user"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_FOLLOW_USER_RESPONSE,  # You'll need to add this to ResponseMessageTopic
            payload={
                "user_id": user_id,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def user_id(self) -> str:
        """Get the user ID from the payload"""
        return self.payload.get("user_id", "")

    @property
    def success(self) -> bool:
        """Get whether the follow operation was successful"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> str:
        """Get the error message if the follow operation failed"""
        return self.payload.get("error_message", "")