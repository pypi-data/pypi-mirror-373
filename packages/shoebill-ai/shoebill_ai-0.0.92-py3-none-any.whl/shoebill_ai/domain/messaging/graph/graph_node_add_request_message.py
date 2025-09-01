from typing import TypeVar, Dict, Any, Type, Optional, List

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphNodeAddRequestMessage(HaiMessage):
    """Message to add a node to the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str, labels: List[str], properties: dict = None,
                       description: str = None) -> 'GraphNodeAddRequestMessage':
        """Create a message requesting to add a node to the graph"""
        if properties is None:
            properties = {}

        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODE_ADD,
            payload={
                "node_id": node_id,
                "labels": labels,
                "properties": properties,
                "description": description
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

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodeAddRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_id=payload.get("node_id", ''),
            labels=payload.get("labels", []),
            properties=payload.get("properties", {}),
            description=payload.get("description")
        )
