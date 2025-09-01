from typing import Type, TypeVar, Dict, Any, List

from h_message_bus import HaiMessage

from ..request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='WebGetDocsResponseMessage')

class WebGetDocsResponseMessage(HaiMessage):

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, pages: List[Dict[str, Any]]) -> 'WebGetDocsResponseMessage':
        return cls.create(
            topic=RequestMessageTopic.WEB_GET_DOCS_RESPONSE,
            payload={
                "pages": pages
            },
        )

    @property
    def docs(self) -> List[Dict[str, Any]]:
        return self.payload.get("pages", [])

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'WebGetDocsResponseMessage':
        payload = message.payload

        return cls.create_message(
            pages=payload.get("pages", []),
        )