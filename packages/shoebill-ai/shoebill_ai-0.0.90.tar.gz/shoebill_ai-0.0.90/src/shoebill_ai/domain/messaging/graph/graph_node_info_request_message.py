from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphNodeInfoRequestMessage(HaiMessage):
    """Message to request information about a specific node from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_name: str) -> 'GraphNodeInfoRequestMessage':
        """Create a message requesting information about a specific node from the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODE_INFO,
            payload={
                "node_name": node_name
            },
        )

    @property
    def node_name(self) -> str:
        """Get the node name from the payload"""
        return self.payload.get("node_name", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodeInfoRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_name=payload.get("node_name", "")
        )