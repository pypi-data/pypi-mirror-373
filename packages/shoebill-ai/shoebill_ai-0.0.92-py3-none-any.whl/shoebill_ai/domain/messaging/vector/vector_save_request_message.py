from typing import Type, TypeVar, Dict, Any, List

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class VectorSaveRequestMessage(HaiMessage):
    """Message to data in vector store"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, collection_name: str, collection_metadata: dict[str,str], document_id: str, content: str, embeddings: List[float], metadata: dict[str,str]) -> 'VectorSaveRequestMessage':
        """Create a message requesting Twitter user data"""
        return cls.create(
            topic=RequestMessageTopic.VECTORS_SAVE,
            payload={
                "collection_name": collection_name,
                "collection_metadata": collection_metadata,
                "document_id": document_id,
                "content": content,
                "embeddings": embeddings,
                "metadata": metadata
            },
        )

    @property
    def collection_name(self) -> str:
        """Get the collection name from the payload"""
        return self.payload.get("collection_name")

    @property
    def collection_metadata(self) -> dict[str, str]:
        """Get the collection name from the payload"""
        return self.payload.get("collection_metadata")

    @property
    def document_id(self) -> str:
        """Get the document ID from the payload"""
        return self.payload.get("document_id")

    @property
    def content(self) -> str:
        """Get the content from the payload"""
        return self.payload.get("content")

    @property
    def embeddings(self) -> List[float]:
        """Get the embeddings from the payload"""
        return self.payload.get("embeddings")

    @property
    def metadata(self) -> dict[str, str]:
        """Get the metadata from the payload"""
        return self.payload.get("metadata")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'VectorSaveRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            collection_name=payload.get("collection_name", ''),
            collection_metadata=payload.get("collection_metadata", {}),
            document_id=payload.get("document_id", ''),
            content=payload.get("content", ''),
            metadata=payload.get("metadata", {}),
            embeddings=payload.get("embeddings", [])
        )
