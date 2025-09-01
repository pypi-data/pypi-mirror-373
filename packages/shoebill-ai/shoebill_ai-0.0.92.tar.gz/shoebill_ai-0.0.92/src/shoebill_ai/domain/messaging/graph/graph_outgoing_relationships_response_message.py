from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphOutgoingRelationshipsResponseMessage(HaiMessage):
    """Message containing outgoing relationships for a specific node from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str, relationships: List[Dict], 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphOutgoingRelationshipsResponseMessage':
        """Create a message with outgoing relationships for a specific node"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_OUTGOING_RELATIONSHIPS_RESPONSE,
            payload={
                "node_id": node_id,
                "relationships": relationships,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def node_id(self) -> str:
        """Get the node ID from the payload"""
        return self.payload.get("node_id", "")

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
    def from_hai_message(cls, message: HaiMessage) -> 'GraphOutgoingRelationshipsResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_id=payload.get("node_id", ""),
            relationships=payload.get("relationships", []),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )