import json
from typing import Type, TypeVar, Dict, Any, List

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class TwitterGetUsersRequestMessage(HaiMessage):
    """Message to request Twitter user information"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, usernames: List[str]) -> 'TwitterGetUsersRequestMessage':
        """Create a message requesting Twitter user data"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_USERS,
            payload={"usernames": json.dumps(usernames)},
        )

    @property
    def usernames(self) -> List[str]:
        """Get the username from the payload"""
        usernames_payload = self.payload.get("usernames", "")
        usernames = json.loads(usernames_payload)
        response_list = []
        for username in usernames:
            response_list.append(username)
        return response_list

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterGetUsersRequestMessage':
        payload = message.payload
        usernames = payload.get("usernames", "")
        usernames_list = json.loads(usernames)
        return cls.create_message(
        usernames=usernames_list
        )