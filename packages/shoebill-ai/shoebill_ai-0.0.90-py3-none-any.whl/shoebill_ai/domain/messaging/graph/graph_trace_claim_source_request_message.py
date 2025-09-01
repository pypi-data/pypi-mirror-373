from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphTraceClaimSourceRequestMessage(HaiMessage):
    """Message to request tracing the source of a claim node"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, claim_node_id: str) -> 'GraphTraceClaimSourceRequestMessage':
        """Create a message requesting to trace the source of a claim node"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_TRACE_CLAIM_SOURCE,
            payload={
                "claim_node_id": claim_node_id
            },
        )

    @property
    def claim_node_id(self) -> str:
        """Get the claim node ID from the payload"""
        return self.payload.get("claim_node_id", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphTraceClaimSourceRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            claim_node_id=payload.get("claim_node_id", "")
        )