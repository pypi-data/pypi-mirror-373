from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphFindUserEventsAndAnnouncementsResponseMessage(HaiMessage):
    """Message containing events and announcements associated with a user"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, user_node_id: str, announcements: List[Dict], events: List[Dict], 
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphFindUserEventsAndAnnouncementsResponseMessage':
        """Create a message with events and announcements associated with a user"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_FIND_USER_EVENTS_AND_ANNOUNCEMENTS_RESPONSE,
            payload={
                "user_node_id": user_node_id,
                "announcements": announcements,
                "events": events,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def user_node_id(self) -> str:
        """Get the user node ID from the payload"""
        return self.payload.get("user_node_id", "")

    @property
    def announcements(self) -> List[Dict]:
        """Get the list of announcement nodes from the payload"""
        return self.payload.get("announcements", [])

    @property
    def events(self) -> List[Dict]:
        """Get the list of event nodes from the payload"""
        return self.payload.get("events", [])

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphFindUserEventsAndAnnouncementsResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            user_node_id=payload.get("user_node_id", ""),
            announcements=payload.get("announcements", []),
            events=payload.get("events", []),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )