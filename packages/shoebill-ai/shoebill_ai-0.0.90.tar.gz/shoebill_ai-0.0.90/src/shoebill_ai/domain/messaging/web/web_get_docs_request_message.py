from typing import Type, TypeVar, Dict, Any, Optional

from h_message_bus import HaiMessage

from ..request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class WebGetDocsRequestMessage(HaiMessage):

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, root_url: Optional[str]) -> 'WebGetDocsRequestMessage':
        return cls.create(
            topic=RequestMessageTopic.WEB_GET_DOCS,
            payload={
                "root_url": root_url
            },
        )

    @property
    def root_url(self) -> str:
        return self.payload.get("root_url", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'WebGetDocsRequestMessage':
        payload = message.payload

        return cls.create_message(
            root_url=payload.get("root_url", ""),
        )