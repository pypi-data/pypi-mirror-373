from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphIncomingRelationshipsRequestMessage(HaiMessage):
    """Message to request incoming relationships for a specific node from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str) -> 'GraphIncomingRelationshipsRequestMessage':
        """Create a message requesting incoming relationships for a specific node from the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_INCOMING_RELATIONSHIPS,
            payload={
                "node_id": node_id
            },
        )

    @property
    def node_id(self) -> str:
        """Get the node ID from the payload"""
        return self.payload.get("node_id", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphIncomingRelationshipsRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_id=payload.get("node_id", "")
        )