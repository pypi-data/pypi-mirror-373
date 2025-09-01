from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphGetStatisticsResponseMessage(HaiMessage):
    """Message containing statistics from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, statistics: Dict[str, int], 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphGetStatisticsResponseMessage':
        """Create a message with statistics from the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_GET_STATISTICS_RESPONSE,
            payload={
                "statistics": statistics,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def statistics(self) -> Dict[str, int]:
        """Get the statistics from the payload"""
        return self.payload.get("statistics", {})

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", True)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphGetStatisticsResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            statistics=payload.get("statistics", {}),
            success=payload.get("success", True),
            error_message=payload.get("error_message")
        )