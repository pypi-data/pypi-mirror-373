from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphRelationshipsByTypeRequestMessage(HaiMessage):
    """Message to request relationships of a specific type from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, relationship_type: str) -> 'GraphRelationshipsByTypeRequestMessage':
        """Create a message requesting relationships of a specific type from the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_RELATIONSHIPS_BY_TYPE,
            payload={
                "relationship_type": relationship_type
            },
        )

    @property
    def relationship_type(self) -> str:
        """Get the relationship type from the payload"""
        return self.payload.get("relationship_type", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphRelationshipsByTypeRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            relationship_type=payload.get("relationship_type", "")
        )