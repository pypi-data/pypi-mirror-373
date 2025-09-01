from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphFindOpinionsOnNodeRequestMessage(HaiMessage):
    """Message to request finding opinions on a specific node"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str, since_timestamp: str = None) -> 'GraphFindOpinionsOnNodeRequestMessage':
        """Create a message requesting to find opinions on a specific node"""
        payload = {
            "node_id": node_id
        }
        if since_timestamp:
            payload["since_timestamp"] = since_timestamp

        return cls.create(
            topic=RequestMessageTopic.GRAPH_FIND_OPINIONS_ON_NODE,
            payload=payload
        )

    @property
    def node_id(self) -> str:
        """Get the node ID from the payload"""
        return self.payload.get("node_id", "")

    @property
    def since_timestamp(self) -> str:
        """Get the since timestamp from the payload"""
        return self.payload.get("since_timestamp")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphFindOpinionsOnNodeRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_id=payload.get("node_id", ""),
            since_timestamp=payload.get("since_timestamp", None)
        )
