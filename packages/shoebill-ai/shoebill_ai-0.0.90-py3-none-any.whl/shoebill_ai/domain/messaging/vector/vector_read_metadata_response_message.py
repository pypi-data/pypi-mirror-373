import json
from typing import Type, TypeVar, Dict, Any, List

from h_message_bus import HaiMessage

from .vector_collection_metadata import VectorCollectionMetadata
from ....domain.messaging.request_message_topic import RequestMessageTopic


T = TypeVar('T', bound='HaiMessage')

class VectorReadMetaDataResponseMessage(HaiMessage):

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, metadata: List[dict[str, str]]) -> 'VectorReadMetaDataResponseMessage':
        metadata_result = json.dumps(metadata)
        return cls.create(
            topic=RequestMessageTopic.VECTORS_METADATA_READ_RESPONSE,
            payload={
                "metadata": metadata_result,
            },
        )

    @property
    def metadata(self) -> List[VectorCollectionMetadata]:
        """Get the collection name from the message payload"""
        metadata = self.payload.get("metadata", "")
        meta_dict = json.loads(metadata)
        response_list = []
        for meta in meta_dict:
            response_list.append(VectorCollectionMetadata.from_dict(meta))
        return response_list

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'VectorReadMetaDataResponseMessage':
        payload = message.payload
        metadata = payload.get("metadata", "")
        meta_list = json.loads(metadata)
        return cls.create_message(
            metadata=meta_list
        )