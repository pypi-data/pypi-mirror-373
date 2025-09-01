from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphCountRelationshipsRequestMessage(HaiMessage):
    """Message to request counting relationships in the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, anchor_node: str, relationship_type: str = None, 
                      relationship_direction: str = None) -> 'GraphCountRelationshipsRequestMessage':
        """Create a message requesting to count relationships in the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_COUNT_RELATIONSHIPS,
            payload={
                "anchor_node": anchor_node,
                "relationship_type": relationship_type,
                "relationship_direction": relationship_direction
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

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphCountRelationshipsRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            anchor_node=payload.get("anchor_node", ""),
            relationship_type=payload.get("relationship_type"),
            relationship_direction=payload.get("relationship_direction")
        )