from typing import TypeVar, Dict, Any, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphFindUserEventsAndAnnouncementsRequestMessage(HaiMessage):
    """Message to request finding events and announcements associated with a user"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, user_node_id: str) -> 'GraphFindUserEventsAndAnnouncementsRequestMessage':
        """Create a message requesting to find events and announcements associated with a user"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_FIND_USER_EVENTS_AND_ANNOUNCEMENTS,
            payload={
                "user_node_id": user_node_id
            },
        )

    @property
    def user_node_id(self) -> str:
        """Get the user node ID from the payload"""
        return self.payload.get("user_node_id", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphFindUserEventsAndAnnouncementsRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            user_node_id=payload.get("user_node_id", "")
        )