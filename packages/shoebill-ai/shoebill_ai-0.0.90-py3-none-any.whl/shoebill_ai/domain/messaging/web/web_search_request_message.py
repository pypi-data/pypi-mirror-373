from typing import Type, TypeVar, Dict, Any

from h_message_bus import HaiMessage

from ..request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class WebSearchRequestMessage(HaiMessage):

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, query: str) -> 'WebSearchRequestMessage':
        return cls.create(
            topic=RequestMessageTopic.WEB_SEARCH,
            payload={"query": query},
        )

    @property
    def query(self) -> str:
        return self.payload.get("query", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'WebSearchRequestMessage':
        payload = message.payload

        return cls.create_message(
        query=payload.get("query", "")
        )