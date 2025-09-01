from typing import Dict, Any, Type, TypeVar, List, Optional
import json

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class TwitterSearchResponseMessage(HaiMessage):
    """Message containing Twitter search results"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(
            cls,
            query: str,
            results: List[Dict[str, Any]],
            result_count: int,
            request_id: str
    ) -> 'TwitterSearchResponseMessage':
        """Create a message containing Twitter search results"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_SEARCH_RESPONSE,
            payload={
                "query": query,
                "results": json.dumps(results),
                "result_count": result_count,
                "request_id": request_id
            },
        )

    @property
    def query(self) -> str:
        """Get the search query from the payload"""
        return self.payload.get("query", "")

    @property
    def result_count(self) -> int:
        """Get the number of results from the payload"""
        return self.payload.get("result_count", 0)

    @property
    def request_id(self) -> str:
        """Get the original request ID from the payload"""
        return self.payload.get("request_id", "")

    @property
    def results(self) -> List[Dict[str, Any]]:
        """Get the search results from the payload"""
        results_json = self.payload.get("results", "[]")
        return json.loads(results_json)

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterSearchResponseMessage':
        """Create a TwitterSearchResponseMessage from a HaiMessage"""
        payload = message.payload
        query = payload.get("query", "")
        results_json = payload.get("results", "[]")
        results = json.loads(results_json)
        result_count = payload.get("result_count", 0)
        request_id = payload.get("request_id", "")

        return cls.create_message(
            query=query,
            results=results,
            result_count=result_count,
            request_id=request_id
        )