from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphNodeUpdateRequestMessage(HaiMessage):
    """Message to update an existing node in the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str, properties: dict = None,
                       description: str = None) -> 'GraphNodeUpdateRequestMessage':
        """Create a message requesting to update a node in the graph"""
        if properties is None:
            properties = {}

        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODE_UPDATE,
            payload={
                "node_id": node_id,
                "properties": properties,
                "description": description
            },
        )

    @property
    def node_id(self) -> str:
        """Get the node ID from the payload"""
        return self.payload.get("node_id")

    @property
    def properties(self) -> dict:
        """Get the properties from the payload"""
        return self.payload.get("properties", {})

    @property
    def description(self) -> Optional[str]:
        """Get the description from the payload"""
        return self.payload.get("description")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodeUpdateRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_id=payload.get("node_id", ''),
            properties=payload.get("properties", {}),
            description=payload.get("description")
        )
