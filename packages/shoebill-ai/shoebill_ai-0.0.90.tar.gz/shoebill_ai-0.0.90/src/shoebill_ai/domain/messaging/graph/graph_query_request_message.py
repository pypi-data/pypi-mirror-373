from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphQueryRequestMessage(HaiMessage):
    """Message to perform a custom query on the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, query: str, parameters: dict = None) -> 'GraphQueryRequestMessage':
        """Create a message requesting to perform a custom query on the graph"""
        if parameters is None:
            parameters = {}

        return cls.create(
            topic=RequestMessageTopic.GRAPH_QUERY,
            payload={
                "query": query,
                "parameters": parameters
            },
        )

    @property
    def query(self) -> str:
        """Get the query from the payload"""
        return self.payload.get("query")

    @property
    def parameters(self) -> dict:
        """Get the query parameters from the payload"""
        return self.payload.get("parameters", {})

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphQueryRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            query=payload.get("query", ''),
            parameters=payload.get("parameters", {})
        )
