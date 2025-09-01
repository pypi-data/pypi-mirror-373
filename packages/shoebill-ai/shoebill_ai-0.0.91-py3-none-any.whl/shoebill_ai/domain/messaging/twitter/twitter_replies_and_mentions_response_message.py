from dataclasses import dataclass
from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

@dataclass
class TwitterRepliesAndMentionsResponseMessage(HaiMessage):
    """Message containing replies and mentions from Twitter"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, success: bool = True, replies: List[Dict[str, Any]] = None, 
                       mentions: List[Dict[str, Any]] = None, 
                       error_message: str = None) -> 'TwitterRepliesAndMentionsResponseMessage':
        """Create a message with replies and mentions from Twitter"""
        if replies is None:
            replies = []
        if mentions is None:
            mentions = []
            
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_REPLIES_AND_MENTIONS_RESPONSE,
            payload={
                "success": success,
                "replies": replies,
                "mentions": mentions,
                "error_message": error_message
            },
        )

    @property
    def success(self) -> bool:
        """Get whether the request was successful"""
        return self.payload.get("success", False)

    @property
    def replies(self) -> List[Dict[str, Any]]:
        """Get the replies from the payload"""
        return self.payload.get("replies", [])

    @property
    def mentions(self) -> List[Dict[str, Any]]:
        """Get the mentions from the payload"""
        return self.payload.get("mentions", [])

    @property
    def error_message(self) -> Optional[str]:
        """Get any error message"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterRepliesAndMentionsResponseMessage':
        """Create a TwitterRepliesAndMentionsResponseMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            success=payload.get("success", False),
            replies=payload.get("replies", []),
            mentions=payload.get("mentions", []),
            error_message=payload.get("error_message")
        )