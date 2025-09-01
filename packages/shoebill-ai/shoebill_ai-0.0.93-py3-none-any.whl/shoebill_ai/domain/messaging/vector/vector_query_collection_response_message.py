import json
from typing import Type, TypeVar, Dict, Any

from h_message_bus import HaiMessage

from .vector_query_answer import VectorQueryAnswer
from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class VectorQueryCollectionResponseMessage(HaiMessage):
    """Response Message from reading vector data"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, result: dict[int, dict[str, str]]) -> 'VectorQueryCollectionResponseMessage':
        """Create a message requesting Twitter user data"""
        result_list = json.dumps(result)
        return cls.create(
            topic=RequestMessageTopic.VECTORS_QUERY_RESPONSE,
            payload={
                "result": result_list,
            },
        )

    @property
    def results(self) -> list[VectorQueryAnswer]:
        """Returns the results from the message payload"""
        results = self.payload.get("result", "")
        meta_dict = json.loads(results)
        response_list = []
        for meta in meta_dict:
            response_list.append(VectorQueryAnswer.from_dict(meta))
        return response_list

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'VectorQueryCollectionResponseMessage':
        # Extract necessary fields from the message payload
        payload = message.payload
        result = payload.get("result", "")
        result_list = json.loads(result)
        return cls.create_message(
           result=result_list
        )
