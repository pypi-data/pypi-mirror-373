from typing import Type, TypeVar, Dict, Any, List

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class TwitterGetUserResponseMessage(HaiMessage):
    """Response of Twitter user information request"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, user_id: str, user_name: str, screen_name: str, description: str, followers_count: str, like_count: str, is_verified: str, url: str, bio_urls: [str], pfp_url: str = '') -> 'TwitterGetUserResponseMessage':
        """Create a response message from Twitter user information"""
        return cls.create(
            topic=RequestMessageTopic.TWITTER_GET_USER_RESPONSE,
            payload={
                'id': user_id,
                'screen_name': screen_name,
                'user_name': user_name,
                'description': description,
                'followers_count': followers_count,
                'like_count': like_count,
                'is_verified': is_verified,
                'url': url,
                'bio_urls': bio_urls,
                'pfp_url': pfp_url
            })

    @property
    def user_id(self) -> str:
        """Get user ID"""
        return self.payload.get('id', '')

    @property
    def screen_name(self) -> str:
        """Get screen name"""
        return self.payload.get('screen_name', '')

    @property
    def user_name(self) -> str:
        """Get user name"""
        return self.payload.get('user_name', '')

    @property
    def description(self) -> str:
        """Get user description"""
        return self.payload.get('description', '')

    @property
    def followers_count(self) -> str:
        """Get followers count"""
        return self.payload.get('followers_count', '')

    @property
    def like_count(self) -> str:
        """Get like count"""
        return self.payload.get('like_count', '')

    @property
    def is_verified(self) -> str:
        """Get verification status"""
        return self.payload.get('is_verified', '')

    @property
    def url(self) -> str:
        """Get user URL"""
        return self.payload.get('url', '')

    @property
    def bio_urls(self) -> List[str]:
        """Get URLs from user bio"""
        return self.payload.get('bio_urls', [])
        
    @property
    def pfp_url(self) -> str:
        """Get profile picture URL"""
        return self.payload.get('pfp_url', '')

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'TwitterGetUserResponseMessage':
        """
        Convert a HaiMessage to TwitterGetUserResponseMessage

        Args:
            message: The source HaiMessage object

        Returns:
            A new TwitterGetUserResponseMessage with data from the source message
        """
        # Extract necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            user_id=payload.get('id', ''),
            screen_name=payload.get('screen_name', ''),
            user_name=payload.get('user_name', ''),
            description=payload.get('description', ''),
            followers_count=payload.get('followers_count', ''),
            like_count=payload.get('like_count', ''),
            is_verified=payload.get('is_verified', ''),
            url=payload.get('url', ''),
            bio_urls=payload.get('bio_urls', []),
            pfp_url=payload.get('pfp_url', '')
        )

