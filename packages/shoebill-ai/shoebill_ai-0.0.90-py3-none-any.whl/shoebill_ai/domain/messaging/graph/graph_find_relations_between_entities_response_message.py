from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphFindRelationsBetweenEntitiesResponseMessage(HaiMessage):
    """Message containing relations found between two entities"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, entity1_id: str, entity2_id: str, paths: List[Dict], 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphFindRelationsBetweenEntitiesResponseMessage':
        """Create a message with relations found between two entities"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_FIND_RELATIONS_BETWEEN_ENTITIES_RESPONSE,
            payload={
                "entity1_id": entity1_id,
                "entity2_id": entity2_id,
                "paths": paths,
                "success": success,
                "error_message": error_message
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

    @property
    def paths(self) -> List[Dict]:
        """Get the list of paths from the payload"""
        return self.payload.get("paths", [])

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphFindRelationsBetweenEntitiesResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            entity1_id=payload.get("entity1_id", ""),
            entity2_id=payload.get("entity2_id", ""),
            paths=payload.get("paths", []),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )