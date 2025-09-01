from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphOpinionNodesSinceTimestampRequestMessage(HaiMessage):
    """Message to get opinion nodes since a specific timestamp"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, timestamp_str: str) -> 'GraphOpinionNodesSinceTimestampRequestMessage':
        """Create a message requesting to get opinion nodes since a timestamp"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_OPINION_NODES_SINCE_TIMESTAMP,
            payload={
                "timestamp": timestamp_str
            }
        )

    # @property
    # def timestamp(self) -> str:
    #     """Get the timestamp from the payload"""
    #     return self.payload.get("timestamp", "")
    #
    # @timestamp.setter
    # def timestamp(self, value: str) -> None:
    #     """Set the timestamp in the payload"""
    #     if hasattr(self, 'payload'):
    #         self.payload["timestamp"] = value
    #     else:
    #         self.payload = {"timestamp": value}

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphOpinionNodesSinceTimestampRequestMessage':
        """Create a GraphOpinionNodesSinceTimestampRequestMessage from a HaiMessage"""
        return cls.create_message(
            timestamp_str=message.payload.get("timestamp", "")
        )