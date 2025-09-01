from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphNodeSubgraphRequestMessage(HaiMessage):
    """Message to request a subgraph centered on a specific node"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str, max_traversal: int = 2) -> 'GraphNodeSubgraphRequestMessage':
        """Create a message requesting a subgraph centered on a specific node"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODE_SUBGRAPH,
            payload={
                "node_id": node_id,
                "max_traversal": max_traversal
            },
        )

    @property
    def node_id(self) -> str:
        """Get the node ID from the payload"""
        return self.payload.get("node_id", "")

    @property
    def max_traversal(self) -> int:
        """Get the maximum traversal depth from the payload"""
        return self.payload.get("max_traversal", 2)

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodeSubgraphRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_id=payload.get("node_id", ""),
            max_traversal=payload.get("max_traversal", 2)
        )