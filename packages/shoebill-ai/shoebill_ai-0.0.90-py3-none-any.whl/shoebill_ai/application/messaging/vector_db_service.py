import logging
from typing import Optional, List

from h_message_bus import NatsPublisherAdapter

from ...domain.messaging.vector.vector_query_collection_request_message import VectorQueryCollectionRequestMessage
from ...domain.messaging.vector.vector_query_collection_response_message import VectorQueryCollectionResponseMessage
from ...domain.messaging.vector.vector_read_metadata_request_message import VectorReadMetaDataRequestMessage
from ...domain.messaging.vector.vector_read_metadata_response_message import VectorReadMetaDataResponseMessage
from ...domain.messaging.vector.vector_save_request_message import VectorSaveRequestMessage


class VectorDBService:
    def __init__(self, nats_publisher_adapter: NatsPublisherAdapter):
        self.nats_publisher_adapter = nats_publisher_adapter
        self.logger = logging.getLogger(__name__)

    async def get_knowledgebase_metadata(self, timeout: float = 30.0) -> VectorReadMetaDataResponseMessage:
        message = VectorReadMetaDataRequestMessage.create_message()
        response = await self.nats_publisher_adapter.request(message, timeout=timeout)
        metadata_result = VectorReadMetaDataResponseMessage.from_hai_message(response)
        return metadata_result

    async def query_knowledgebase(self, query: List[float], collection_name: str, timeout: float = 30.0) -> Optional[VectorQueryCollectionResponseMessage]:
        try:
            message = VectorQueryCollectionRequestMessage.create_message(query_embedding=query, collection_name=collection_name,
                                                                         top_n="5")
            vector_response = await self.nats_publisher_adapter.request(message, timeout=timeout)
            return VectorQueryCollectionResponseMessage.from_hai_message(vector_response)
        except Exception as e:
            self.logger.error(f"Error querying knowledgebase: {str(e)}")
            return None

    async def save_document(self, collection_name: str, collection_metadata: dict[str, str], document_id: str, content: str, doc_metadata: dict[str,str], embeddings: list[float]):
        try:
            request = VectorSaveRequestMessage.create_message(
                collection_name=collection_name,
                collection_metadata=collection_metadata,
                document_id=document_id,
                content=content,
                metadata=doc_metadata,
            embeddings=embeddings)
            # Await the publish operation
            await self.nats_publisher_adapter.publish(request)
            return None
        except Exception as e:
            self.logger.error(f"Error during save_documentation_pages: {str(e)}")
            return None
