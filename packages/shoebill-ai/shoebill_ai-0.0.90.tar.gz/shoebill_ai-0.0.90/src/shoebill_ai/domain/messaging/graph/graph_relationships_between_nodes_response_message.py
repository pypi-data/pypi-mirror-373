from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphRelationshipsBetweenNodesResponseMessage(HaiMessage):
    """Message containing relationships between two specific nodes in the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, source_node_id: str, target_node_id: str, relationships: List[Dict], 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphRelationshipsBetweenNodesResponseMessage':
        """Create a message with relationships between two specific nodes"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_RELATIONSHIPS_BETWEEN_NODES_RESPONSE,
            payload={
                "source_node_id": source_node_id,
                "target_node_id": target_node_id,
                "relationships": relationships,
                "success": success,
                "error_message": error_message
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

    @property
    def relationships(self) -> List[Dict]:
        """Get the list of relationships from the payload"""
        return self.payload.get("relationships", [])

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphRelationshipsBetweenNodesResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            source_node_id=payload.get("source_node_id", ""),
            target_node_id=payload.get("target_node_id", ""),
            relationships=payload.get("relationships", []),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )