import json
from typing import Type, TypeVar, Dict, Any, List

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class TwitterGetUsersResponseMessage(HaiMessage):

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, users: List[dict[str, str]]) -> 'TwitterGetUsersResponseMessage':
        user_result = json.dumps(users)
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_USERS_RESPONSE,
            payload={
                "users": user_result,
            },
        )

    @property
    def users(self) -> List[dict[str, str]]:
        """Get the collection name from the message payload"""
        users = self.payload.get("users", "")
        users_dict = json.loads(users)
        response_list = []
        for user in users_dict:
            response_list.append(user)
        return response_list

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterGetUsersResponseMessage':
        payload = message.payload
        metadata = payload.get("users", "")
        meta_list = json.loads(metadata)
        return cls.create_message(
            users=meta_list
        )