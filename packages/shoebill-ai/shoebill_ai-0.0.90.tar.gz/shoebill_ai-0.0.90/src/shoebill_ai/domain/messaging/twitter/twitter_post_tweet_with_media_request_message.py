from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterPostTweetWithMediaRequestMessage')

@dataclass
class TwitterPostTweetWithMediaRequestMessage(HaiMessage):
    """Message to request posting a new tweet with media"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, text: str, media_path: str) -> 'TwitterPostTweetWithMediaRequestMessage':
        """Create a message requesting to post a new tweet with media"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_POST_TWEET_WITH_MEDIA,  # You'll need to add this to RequestMessageTopic
            payload={
                "text": text,
                "media_path": media_path
            },
        )

    @property
    def text(self) -> str:
        """Get the text content of the tweet from the payload"""
        return self.payload.get("text", "")
    
    @property
    def media_path(self) -> str:
        """Get the media path from the payload"""
        return self.payload.get("media_path", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterPostTweetWithMediaRequestMessage':
        """Create a TwitterPostTweetWithMediaRequestMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            text=payload.get("text", ""),
            media_path=payload.get("media_path", "")
        )