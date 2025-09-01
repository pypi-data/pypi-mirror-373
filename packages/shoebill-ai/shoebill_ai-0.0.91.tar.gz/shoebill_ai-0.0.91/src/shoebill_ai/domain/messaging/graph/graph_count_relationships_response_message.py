from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphCountRelationshipsResponseMessage(HaiMessage):
    """Message containing the count of relationships in the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, anchor_node: str, relationship_type: Optional[str], 
                       relationship_direction: Optional[str], count: int, 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphCountRelationshipsResponseMessage':
        """Create a message with the count of relationships"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_COUNT_RELATIONSHIPS_RESPONSE,
            payload={
                "anchor_node": anchor_node,
                "relationship_type": relationship_type,
                "relationship_direction": relationship_direction,
                "count": count,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def anchor_node(self) -> str:
        """Get the anchor node from the payload"""
        return self.payload.get("anchor_node", "")

    @property
    def relationship_type(self) -> Optional[str]:
        """Get the relationship type from the payload"""
        return self.payload.get("relationship_type")

    @property
    def relationship_direction(self) -> Optional[str]:
        """Get the relationship direction from the payload"""
        return self.payload.get("relationship_direction")

    @property
    def count(self) -> int:
        """Get the count from the payload"""
        return self.payload.get("count", 0)

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphCountRelationshipsResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            anchor_node=payload.get("anchor_node", ""),
            relationship_type=payload.get("relationship_type"),
            relationship_direction=payload.get("relationship_direction"),
            count=payload.get("count", 0),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )