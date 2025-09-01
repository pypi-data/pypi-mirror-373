from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphEventNodesSinceTimestampRequestMessage(HaiMessage):
    """Message to get event nodes since a specific timestamp"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, timestamp_str: str) -> 'GraphEventNodesSinceTimestampRequestMessage':
        """Create a message requesting to get event nodes since a timestamp"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_EVENT_NODES_SINCE_TIMESTAMP,
            payload={
                "timestamp": timestamp_str
            }
        )

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphEventNodesSinceTimestampRequestMessage':
        """Create a GraphEventNodesSinceTimestampRequestMessage from a HaiMessage"""
        return cls.create_message(
            timestamp_str=message.payload.get("timestamp", "")
        )