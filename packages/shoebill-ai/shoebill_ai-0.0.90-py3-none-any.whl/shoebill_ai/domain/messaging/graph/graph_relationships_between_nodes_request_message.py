from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphRelationshipsBetweenNodesRequestMessage(HaiMessage):
    """Message to request relationships between two specific nodes in the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, source_node_id: str, target_node_id: str) -> 'GraphRelationshipsBetweenNodesRequestMessage':
        """Create a message requesting relationships between two specific nodes in the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_RELATIONSHIPS_BETWEEN_NODES,
            payload={
                "source_node_id": source_node_id,
                "target_node_id": target_node_id
            },
        )

    @property
    def source_node_id(self) -> str:
        """Get the source node ID from the payload"""
        return self.payload.get("source_node_id", "")

    @property
    def target_node_id(self) -> str:
        """Get the target node ID from the payload"""
        return self.payload.get("target_node_id", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphRelationshipsBetweenNodesRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            source_node_id=payload.get("source_node_id", ""),
            target_node_id=payload.get("target_node_id", "")
        )