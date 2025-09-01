from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphTraceNodeSourceResponseMessage(HaiMessage):
    """Message containing the source of a node"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str, source_node: Optional[Dict] = None, 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphTraceNodeSourceResponseMessage':
        """Create a message with the source of a node"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_TRACE_NODE_SOURCE_RESPONSE,
            payload={
                "node_id": node_id,
                "source_node": source_node,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def node_id(self) -> str:
        """Get the node ID from the payload"""
        return self.payload.get("node_id", "")

    @property
    def source_node(self) -> Optional[Dict]:
        """Get the source node from the payload"""
        return self.payload.get("source_node")

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphTraceNodeSourceResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_id=payload.get("node_id", ""),
            source_node=payload.get("source_node"),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )