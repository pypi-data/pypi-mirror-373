from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphAnnouncementNodesSinceTimestampResponseMessage(HaiMessage):
    """Message containing announcement nodes since a specific timestamp"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, announcement_nodes: List[Dict], 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphAnnouncementNodesSinceTimestampResponseMessage':
        """Create a message with announcement nodes since timestamp"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_ANNOUNCEMENT_NODES_SINCE_TIMESTAMP_RESPONSE,
            payload={
                "announcement_nodes": announcement_nodes,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def announcement_nodes(self) -> List[Dict]:
        """Get the list of announcement nodes from the payload"""
        return self.payload.get("announcement_nodes", [])

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", True)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphAnnouncementNodesSinceTimestampResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            announcement_nodes=payload.get("announcement_nodes", []),
            success=payload.get("success", True),
            error_message=payload.get("error_message")
        )