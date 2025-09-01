from typing import Dict, Any, Type, TypeVar, Optional, Literal, cast

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class TwitterSearchRequestMessage(HaiMessage):
    """Message to request Twitter search"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(
            cls,
            query: str,
            max_results: int = 10,
            min_view_count: int = 50,
            sort_order: Literal["relevancy", "recency"] = "relevancy"
    ) -> 'TwitterSearchRequestMessage':
        """Create a message requesting Twitter search"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_SEARCH,
            payload={
                "query": query,
                "max_results": max_results,
                "min_view_count": min_view_count,
                "sort_order": sort_order
            },
        )

    @property
    def query(self) -> str:
        """Get the search query from the payload"""
        return self.payload.get("query", "")

    @property
    def max_results(self) -> int:
        """Get the maximum number of results from the payload"""
        return self.payload.get("max_results", 10)

    @property
    def min_view_count(self) -> int:
        """Get the minimum view count from the payload"""
        return self.payload.get("min_view_count", 50)

    @property
    def sort_order(self) -> Literal["relevancy", "recency"]:
        """Get the sort order from the payload"""
        sort_order_str = self.payload.get("sort_order", "relevancy")
        if sort_order_str not in ("relevancy", "recency"):
            sort_order_str = "relevancy"
        return cast(Literal["relevancy", "recency"], sort_order_str)

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterSearchRequestMessage':
        """Create a TwitterSearchRequestMessage from a HaiMessage"""
        payload = message.payload
        query = payload.get("query", "")
        max_results = payload.get("max_results", 10)
        min_view_count = payload.get("min_view_count", 50)
        sort_order = payload.get("sort_order", "relevancy")

        return cls.create_message(
            query=query,
            max_results=max_results,
            min_view_count=min_view_count,
            sort_order=sort_order
        )