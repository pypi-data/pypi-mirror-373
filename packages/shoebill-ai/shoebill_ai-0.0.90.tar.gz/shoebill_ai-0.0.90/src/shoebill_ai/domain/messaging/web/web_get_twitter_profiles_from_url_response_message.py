from typing import List, Dict, Type, Any, TypeVar

from h_message_bus import HaiMessage

from ..request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class WebGetTwitterProfilesFromUrlResponseMessage(HaiMessage):

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, profile_names: List[str]) -> 'WebGetTwitterProfilesFromUrlResponseMessage':
        return cls.create(
            topic=RequestMessageTopic.WEB_GET_TWITTER_PROFILES_RESPONSE,
            payload={
                "profile_names": profile_names
            },
        )

    @property
    def profile_names(self) -> List[str]:
        return self.payload.get("profile_names", [])

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'WebGetTwitterProfilesFromUrlResponseMessage':
        payload = message.payload

        return cls.create_message(
            profile_names=payload.get("profile_names", []),
        )
