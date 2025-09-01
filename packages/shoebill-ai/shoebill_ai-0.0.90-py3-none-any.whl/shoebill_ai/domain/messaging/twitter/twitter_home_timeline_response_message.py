from dataclasses import dataclass
from typing import Type, Dict, Any, TypeVar, List

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='TwitterHomeTimelineResponseMessage')

@dataclass
class TwitterHomeTimelineResponseMessage(HaiMessage):
    """Message containing the home timeline for the authenticated Twitter user"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, tweets: List[Dict[str, Any]]) -> 'TwitterHomeTimelineResponseMessage':
        """Create a response message with the user's home timeline tweets"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_HOME_TIMELINE_RESPONSE,
            payload={
                "tweets": tweets
            },
        )

    @property
    def tweets(self) -> List[Dict[str, Any]]:
        """Get the tweets from the payload"""
        return self.payload.get("tweets", [])

    @classmethod
    def from_twitter_messages(cls,
                              twitter_messages: List[dict[str, Any]]) -> 'TwitterHomeTimelineResponseMessage':
        """Create a TwitterHomeTimelineResponseMessage from a list"""
        tweet_list = []

        for message in twitter_messages:
            tweet_data = {
                "tweet_id": message["tweet_id"],
                "message": message["message"],
                "created_at": message["created_at"],
                "view_count": message["view_count"],
                "retweet_count": message["retweet_count"],
                "reply_count": message["reply_count"],
                "user": message["user"]
            }
            tweet_list.append(tweet_data)

        return cls.create_message(tweets=tweet_list)

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterHomeTimelineResponseMessage':
        """Create a TwitterHomeTimelineResponseMessage from a HaiMessage"""
        payload = message.payload

        return cls.create_message(
            tweets=payload.get("tweets", [])
        )
