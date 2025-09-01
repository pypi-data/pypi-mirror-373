from typing import TypeVar, Dict, Any, Type, Optional, List

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphCypherQueryResponseMessage(HaiMessage):
    """Response message containing results of a Cypher query"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(
        cls,
        query: str,
        results: List[Dict[str, Any]],
        success: bool,
        error_message: Optional[str] = None
    ) -> 'GraphCypherQueryResponseMessage':
        """Create a response message with cypher query results"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_CYPHER_QUERY_RESPONSE,
            payload={
                "query": query,
                "results": results,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def query(self) -> str:
        return self.payload.get("query", "")

    @property
    def results(self) -> List[Dict[str, Any]]:
        return self.payload.get("results", [])

    @property
    def success(self) -> bool:
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphCypherQueryResponseMessage':
        payload = message.payload
        return cls.create_message(
            query=payload.get("query", ""),
            results=payload.get("results", []),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )
