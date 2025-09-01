from typing import Type, TypeVar, Dict, Any

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class TwitterGetUserRequestMessage(HaiMessage):
    """Message to request Twitter user information"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, username: str) -> 'TwitterGetUserRequestMessage':
        """Create a message requesting Twitter user data"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_USER,
            payload={"username": username},
        )

    @property
    def username(self) -> str:
        """Get the username from the payload"""
        return self.payload.get("username", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterGetUserRequestMessage':
        payload = message.payload

        return cls.create_message(
        username=payload.get("username", "")
        )
