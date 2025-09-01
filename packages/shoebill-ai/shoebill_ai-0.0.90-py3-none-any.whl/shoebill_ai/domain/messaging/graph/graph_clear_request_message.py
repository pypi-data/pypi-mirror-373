from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphClearRequestMessage(HaiMessage):
    """Message to clear all nodes and relationships from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls) -> 'GraphClearRequestMessage':
        """Create a message requesting to clear the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_CLEAR,
            payload={}
        )

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphClearRequestMessage':
        return cls.create_message()
