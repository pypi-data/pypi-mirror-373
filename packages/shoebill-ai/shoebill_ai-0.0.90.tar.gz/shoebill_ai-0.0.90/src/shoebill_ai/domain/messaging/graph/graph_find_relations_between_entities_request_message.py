from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphFindRelationsBetweenEntitiesRequestMessage(HaiMessage):
    """Message to request finding relations between two entities"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, entity1_id: str, entity2_id: str) -> 'GraphFindRelationsBetweenEntitiesRequestMessage':
        """Create a message requesting to find relations between two entities"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_FIND_RELATIONS_BETWEEN_ENTITIES,
            payload={
                "entity1_id": entity1_id,
                "entity2_id": entity2_id
            },
        )

    @property
    def entity1_id(self) -> str:
        """Get the first entity ID from the payload"""
        return self.payload.get("entity1_id", "")

    @property
    def entity2_id(self) -> str:
        """Get the second entity ID from the payload"""
        return self.payload.get("entity2_id", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphFindRelationsBetweenEntitiesRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            entity1_id=payload.get("entity1_id", ""),
            entity2_id=payload.get("entity2_id", "")
        )