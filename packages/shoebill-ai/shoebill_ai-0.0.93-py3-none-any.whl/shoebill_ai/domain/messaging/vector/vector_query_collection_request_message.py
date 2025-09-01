from typing import Type, TypeVar, Dict, Any, List

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class VectorQueryCollectionRequestMessage(HaiMessage):
    """Message to read data from vector store"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, collection_name: str, query_embedding: List[float], top_n: str) -> 'VectorQueryCollectionRequestMessage':
        """Create a message requesting Twitter user data"""
        return cls.create(
            topic=RequestMessageTopic.VECTORS_QUERY,
            payload={
                "collection_name": collection_name,
                "query": query_embedding,
                "top_n": top_n
            },
        )

    @property
    def collection_name(self) -> str:
        """Get the collection name from the message payload"""
        return self.payload.get("collection_name", "")

    @property
    def query(self) -> List[float]:
        """Get the query from the message payload"""
        return self.payload.get("query", [])

    @property
    def top_n(self) -> str:
        """Get the top_n value from the message payload"""
        return self.payload.get("top_n", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'VectorQueryCollectionRequestMessage':
        payload = message.payload

        return cls.create_message(
            collection_name=payload.get("collection_name", ""),
            query_embedding=payload.get("query", []),
            top_n=payload.get("top_n", "")
        )
