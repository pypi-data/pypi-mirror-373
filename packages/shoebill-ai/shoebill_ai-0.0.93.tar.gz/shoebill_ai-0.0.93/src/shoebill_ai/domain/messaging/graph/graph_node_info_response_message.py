from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphNodeInfoResponseMessage(HaiMessage):
    """Message containing information about a specific node from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_name: str, node_info: Dict, 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphNodeInfoResponseMessage':
        """Create a message with information about a specific node"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODE_INFO_RESPONSE,
            payload={
                "node_name": node_name,
                "node_info": node_info,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def node_name(self) -> str:
        """Get the node name from the payload"""
        return self.payload.get("node_name", "")

    @property
    def node_info(self) -> Dict:
        """Get the node info from the payload"""
        return self.payload.get("node_info", {})

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodeInfoResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_name=payload.get("node_name", ""),
            node_info=payload.get("node_info", {}),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )