from typing import Type, TypeVar, Dict, Any

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class VectorReadMetaDataRequestMessage(HaiMessage):

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls) -> 'VectorReadMetaDataRequestMessage':
        """Create a message requesting Twitter user data"""
        return cls.create(
            topic=RequestMessageTopic.VECTORS_METADATA_READ,
            payload={},
        )

    @classmethod
    def from_hai_message(cls) -> 'VectorReadMetaDataRequestMessage':
        return cls.create_message()