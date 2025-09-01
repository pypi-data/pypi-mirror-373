from typing import Type, TypeVar, Dict, Any

from h_message_bus import HaiMessage

from ..request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class WebGetTwitterProfilesFromUrlRequestMessage(HaiMessage):

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, url: str) -> 'WebGetTwitterProfilesFromUrlRequestMessage':
        return cls.create(
            topic=RequestMessageTopic.WEB_GET_TWITTER_PROFILES,
            payload={
                "url": url
            },
        )

    @property
    def url(self) -> str:
        return self.payload.get("url", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'WebGetTwitterProfilesFromUrlRequestMessage':
        payload = message.payload

        return cls.create_message(
            url=payload.get("url", ""),
        )
