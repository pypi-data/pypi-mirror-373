from typing import TypeVar, Dict, Any, Type, Optional, List

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphNodeAddedResponseMessage(HaiMessage):
    """Message indicating a node was successfully added to the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str, labels: List[str], properties: dict = None,
                       description: str = None, success: bool = True,
                       error_message: Optional[str] = None) -> 'GraphNodeAddedResponseMessage':
        """Create a message confirming a node was added"""
        if properties is None:
            properties = {}

        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODE_ADD_RESPONSE,
            payload={
                "node_id": node_id,
                "labels": labels,
                "properties": properties,
                "description": description,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def node_id(self) -> str:
        """Get the node ID from the payload"""
        return self.payload.get("node_id")

    @property
    def labels(self) -> List[str]:
        """Get the labels from the payload"""
        return self.payload.get("labels", [])

    @property
    def properties(self) -> dict:
        """Get the properties from the payload"""
        return self.payload.get("properties", {})

    @property
    def description(self) -> Optional[str]:
        """Get the description from the payload"""
        return self.payload.get("description")

    @property
    def success(self) -> bool:
        """Check if the operation was successful"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodeAddedResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_id=payload.get("node_id", ''),
            labels=payload.get("labels", []),
            properties=payload.get("properties", {}),
            description=payload.get("description"),
            success=payload.get("success", True),
            error_message=payload.get("error_message")
        )
