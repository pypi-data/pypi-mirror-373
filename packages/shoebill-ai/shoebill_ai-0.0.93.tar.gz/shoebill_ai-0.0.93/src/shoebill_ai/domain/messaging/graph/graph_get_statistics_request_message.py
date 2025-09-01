from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphGetStatisticsRequestMessage(HaiMessage):
    """Message to get statistics from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls) -> 'GraphGetStatisticsRequestMessage':
        """Create a message requesting to get statistics from the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_GET_STATISTICS,
            payload={}
        )

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphGetStatisticsRequestMessage':
        """Create a GraphGetStatisticsRequestMessage from a HaiMessage"""
        return cls.create_message()