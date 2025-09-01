from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphGetAllResultResponseMessage(HaiMessage):
    """Message containing all nodes and relationships from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, nodes: List[Dict], relationships: List[Dict], 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphGetAllResultResponseMessage':
        """Create a message with all nodes and relationships"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_GET_ALL_RESPONSE,
            payload={
                "nodes": nodes,
                "relationships": relationships,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def nodes(self) -> List[Dict]:
        """Get the list of nodes from the payload"""
        return self.payload.get("nodes", [])

    @property
    def relationships(self) -> List[Dict]:
        """Get the list of relationships from the payload"""
        return self.payload.get("relationships", [])

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", True)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphGetAllResultResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            nodes=payload.get("nodes", []),
            relationships=payload.get("relationships", []),
            success=payload.get("success", True),
            error_message=payload.get("error_message")
        )
