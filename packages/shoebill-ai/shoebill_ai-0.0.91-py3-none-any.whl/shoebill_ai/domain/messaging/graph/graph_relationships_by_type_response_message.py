from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphRelationshipsByTypeResponseMessage(HaiMessage):
    """Message containing relationships of a specific type from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, relationship_type: str, relationships: List[Dict], 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphRelationshipsByTypeResponseMessage':
        """Create a message with relationships of a specific type"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_RELATIONSHIPS_BY_TYPE_RESPONSE,
            payload={
                "relationship_type": relationship_type,
                "relationships": relationships,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def relationship_type(self) -> str:
        """Get the relationship type from the payload"""
        return self.payload.get("relationship_type", "")

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
    def from_hai_message(cls, message: HaiMessage) -> 'GraphRelationshipsByTypeResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            relationship_type=payload.get("relationship_type", ""),
            relationships=payload.get("relationships", []),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )