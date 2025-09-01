from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphCypherQueryRequestMessage(HaiMessage):
    """Message to perform a Cypher query on the graph database"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, query: str, parameters: dict | None = None) -> 'GraphCypherQueryRequestMessage':
        """Create a message requesting to perform a Cypher query on the graph"""
        if parameters is None:
            parameters = {}

        return cls.create(
            topic=RequestMessageTopic.GRAPH_CYPHER_QUERY,
            payload={
                "query": query,
                "parameters": parameters
            },
        )

    @property
    def query(self) -> str:
        """Get the query from the payload"""
        return self.payload.get("query", "")

    @property
    def parameters(self) -> dict:
        """Get the query parameters from the payload"""
        return self.payload.get("parameters", {})

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphCypherQueryRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            query=payload.get("query", ''),
            parameters=payload.get("parameters", {})
        )
