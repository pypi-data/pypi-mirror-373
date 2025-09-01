from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphNodesByPropertyRequestMessage(HaiMessage):
    """Message to get nodes with a specific property value and their relationships"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, property_name: str, property_value: any) -> 'GraphNodesByPropertyRequestMessage':
        """Create a message requesting nodes with a specific property value"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODES_BY_PROPERTY,
            payload={
                "property_name": property_name,
                "property_value": property_value
            },
        )

    @property
    def property_name(self) -> str:
        """Get the property name from the payload"""
        return self.payload.get("property_name")

    @property
    def property_value(self) -> any:
        """Get the property value from the payload"""
        return self.payload.get("property_value")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodesByPropertyRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            property_name=payload.get("property_name", ''),
            property_value=payload.get("property_value")
        )