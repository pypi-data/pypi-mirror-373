from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphNodesByLabelRequestMessage(HaiMessage):
    """Message to request nodes with a specific label from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, label: str) -> 'GraphNodesByLabelRequestMessage':
        """Create a message requesting nodes with a specific label from the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODES_BY_LABEL,
            payload={
                "label": label
            },
        )

    @property
    def label(self) -> str:
        """Get the label from the payload"""
        return self.payload.get("label", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodesByLabelRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            label=payload.get("label", "")
        )