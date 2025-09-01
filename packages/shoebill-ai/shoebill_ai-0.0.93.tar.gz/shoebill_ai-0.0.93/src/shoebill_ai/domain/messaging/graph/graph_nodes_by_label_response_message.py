from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphNodesByLabelResponseMessage(HaiMessage):
    """Message containing nodes with a specific label from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, label: str, nodes: List[Dict], 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphNodesByLabelResponseMessage':
        """Create a message with nodes of a specific label"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODES_BY_LABEL_RESPONSE,
            payload={
                "label": label,
                "nodes": nodes,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def label(self) -> str:
        """Get the label from the payload"""
        return self.payload.get("label", "")

    @property
    def nodes(self) -> List[Dict]:
        """Get the list of nodes from the payload"""
        return self.payload.get("nodes", [])

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodesByLabelResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            label=payload.get("label", ""),
            nodes=payload.get("nodes", []),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )