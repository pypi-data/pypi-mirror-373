from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphRelationshipAddRequestMessage(HaiMessage):
    """Message to add a relationship between nodes in the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, source_node_id: str, target_node_id: str,
                       relationship_type: str, properties: dict = None) -> 'GraphRelationshipAddRequestMessage':
        """Create a message requesting to add a relationship to the graph"""
        if properties is None:
            properties = {}

        return cls.create(
            topic=RequestMessageTopic.GRAPH_RELATIONSHIP_ADD,
            payload={
                "source_node_id": source_node_id,
                "target_node_id": target_node_id,
                "relationship_type": relationship_type,
                "properties": properties
            },
        )

    @property
    def source_node_id(self) -> str:
        """Get the source node ID from the payload"""
        return self.payload.get("source_node_id")

    @property
    def target_node_id(self) -> str:
        """Get the target node ID from the payload"""
        return self.payload.get("target_node_id")

    @property
    def relationship_type(self) -> str:
        """Get the relationship type from the payload"""
        return self.payload.get("relationship_type")

    @property
    def properties(self) -> dict:
        """Get the properties from the payload"""
        return self.payload.get("properties", {})

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphRelationshipAddRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            source_node_id=payload.get("source_node_id", ''),
            target_node_id=payload.get("target_node_id", ''),
            relationship_type=payload.get("relationship_type", ''),
            properties=payload.get("properties", {})
        )
