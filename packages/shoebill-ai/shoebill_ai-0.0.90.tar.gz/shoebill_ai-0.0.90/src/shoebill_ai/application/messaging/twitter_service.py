import logging
import re
from typing import Any, Optional, List

from h_message_bus import NatsPublisherAdapter

from ...domain.messaging.twitter.twitter_follow_user_request_message import TwitterFollowUserRequestMessage
from ...domain.messaging.twitter.twitter_get_tweet_request_message import TwitterGetTweetRequestMessage
from ...domain.messaging.twitter.twitter_get_user_request_message import TwitterGetUserRequestMessage
from ...domain.messaging.twitter.twitter_get_user_response_message import TwitterGetUserResponseMessage
from ...domain.messaging.twitter.twitter_get_users_request_message import TwitterGetUsersRequestMessage
from ...domain.messaging.twitter.twitter_get_users_response_message import TwitterGetUsersResponseMessage
from ...domain.messaging.twitter.twitter_home_timeline_request_message import TwitterHomeTimelineRequestMessage
from ...domain.messaging.twitter.twitter_home_timeline_response_message import TwitterHomeTimelineResponseMessage
from ...domain.messaging.twitter.twitter_post_tweet_request_message import TwitterPostTweetRequestMessage
from ...domain.messaging.twitter.twitter_post_tweet_with_media_request_message import TwitterPostTweetWithMediaRequestMessage
from ...domain.messaging.twitter.twitter_quote_retweet_request_message import TwitterQuoteRetweetRequestMessage
from ...domain.messaging.twitter.twitter_reply_request_message import TwitterReplyRequestMessage
from ...domain.messaging.twitter.twitter_search_request_message import TwitterSearchRequestMessage
from ...domain.messaging.twitter.twitter_search_response_message import TwitterSearchResponseMessage
from ...domain.messaging.twitter.twitter_user_tweets_request_message import TwitterUserTweetsRequestMessage
from ...domain.messaging.twitter.twitter_user_tweets_response_message import TwitterUserTweetsResponseMessage
from ...domain.messaging.twitter.twitter_replies_and_mentions_request_message import TwitterRepliesAndMentionsRequestMessage
from ...domain.messaging.twitter.twitter_replies_and_mentions_response_message import TwitterRepliesAndMentionsResponseMessage


class TwitterService:
    def __init__(self, nats_publisher_adapter: NatsPublisherAdapter):
        self.nats_publisher_adapter = nats_publisher_adapter
        self.logger = logging.getLogger(__name__)

    async def get_home_timeline(self, timeout: float = 30.0) -> list[dict[str,Any]]:
        request = TwitterHomeTimelineRequestMessage.create_message(
            include_retweets=False
            , include_replies=False,
            max_results=100)
        tweets_message = await self.nats_publisher_adapter.request(request, timeout=timeout)

        tweets_response = TwitterHomeTimelineResponseMessage.from_hai_message(tweets_message)
        #print(tweets_response.tweets)
        return tweets_response.tweets

    async def quote_retweet(self, tweet_id: str, text: str, timeout: float = 30.0):
        request = TwitterQuoteRetweetRequestMessage.create_message(tweet_id, text)
        success = await self.nats_publisher_adapter.request(request, timeout=timeout)
        self.logger.info(f"Quote retweet request sent: {success}")

    async def post_tweet(self, text: str, timeout: float = 30.0):
        request = TwitterPostTweetRequestMessage.create_message(text)
        success = await self.nats_publisher_adapter.request(request, timeout=timeout)
        self.logger.info(f"Post tweet request sent: {success}")
        
    async def post_tweet_with_media(self, text: str, media_path: str, timeout: float = 30.0):
        request = TwitterPostTweetWithMediaRequestMessage.create_message(text, media_path)
        success = await self.nats_publisher_adapter.request(request, timeout=timeout)
        self.logger.info(f"Post tweet with media request sent: {success}")

    async def reply_to_tweet(self, tweet_id: str, text: str, timeout: float = 30.0):
        request = TwitterReplyRequestMessage.create_message(tweet_id, text)
        success = await self.nats_publisher_adapter.request(request, timeout=timeout)
        self.logger.info(f"Reply request sent: {success}")

    async def get_tweet_details(self, tweet_id: str, timeout: float = 30.0) -> Optional[dict[str, Any]]:
        request = TwitterGetTweetRequestMessage.create_message(tweet_id)
        try:
            self.logger.debug(f"Tweet request: {request}")
            tweet_message = await self.nats_publisher_adapter.request(request, timeout=timeout)
            self.logger.debug(f"Tweet response: {tweet_message}")
            if tweet_message:
                tweet_dict = tweet_message.payload["tweet"]
                return tweet_dict
            return None
        except Exception as e:
            self.logger.error(f"Error getting tweet details: {str(e)}")
            return None

    async def get_user_tweets(self, user_id: str, max_results: int = 5, timeout: float = 30.0, include_replies = False, include_retweets = False):
        request = TwitterUserTweetsRequestMessage.create_message(user_id, max_results, include_replies, include_retweets)
        response = await self.nats_publisher_adapter.request(request, timeout=timeout)
        tweets_response = TwitterUserTweetsResponseMessage.from_hai_message(response)
        return tweets_response.tweets

    async def get_twitter_users_metadata(self, twitter_screen_names: List[str], timeout: float = 30.0) -> List[dict[str, str]]:
        req_message = TwitterGetUsersRequestMessage.create_message(twitter_screen_names)
        self.logger.debug(f"Twitter users request: {req_message}")

        response = await self.nats_publisher_adapter.request(req_message, timeout=timeout)
        self.logger.debug(f"Twitter users response: {response}")

        twitter_users = TwitterGetUsersResponseMessage.from_hai_message(response)
        result: List[dict[str, str]] = []

        for user in twitter_users.users:
            user_dict = user
            data = {
                "id": user_dict["user_id"],
                "user_name": user_dict["user_name"],
                "screen_name": self.clean_text(user_dict['screen_name']),
                "description": self.clean_text(user_dict['description']),
                "url": user_dict['url'],
                "profile_image_url": user_dict['pfp_url'],
                "followers_count": user_dict['followers_count'],
            }
            result.append(data)

        return result

    async def get_twitter_user_metadata(self, twitter_screen_name: str, timeout: float = 30.0) -> Optional[dict[str, str]]:
        req_message = TwitterGetUserRequestMessage.create_message(twitter_screen_name)
        self.logger.debug(f"Twitter user request: {req_message}")
        response = await self.nats_publisher_adapter.request(req_message, timeout=timeout)
        self.logger.debug(f"Twitter user response: {response}")
        twitter_user = TwitterGetUserResponseMessage.from_hai_message(response)

        data = {
            "id": twitter_user.user_id,
            "user_name": twitter_user.user_name,
            "screen_name": self.clean_text(twitter_user.screen_name),
            "description": self.clean_text(twitter_user.description),
            "url": twitter_user.url,
            "profile_image_url": twitter_user.pfp_url,
            "followers_count": twitter_user.followers_count,
        }
        return data

    async def follow_user(self, user_id: str, timeout: float = 30.0):
        request = TwitterFollowUserRequestMessage.create_message(user_id)
        await self.nats_publisher_adapter.request(request, timeout=timeout)

    async def search_tweets(self, query: str, max_results: int = 10, min_views: int = 0, timeout: float = 30.0):
        request = TwitterSearchRequestMessage.create_message(query, max_results, min_view_count=min_views, sort_order='recency')
        response = await self.nats_publisher_adapter.request(request, timeout=timeout)
        tweets_response = TwitterSearchResponseMessage.from_hai_message(response)
        return tweets_response.results

    async def get_replies_and_mentions(self, max_results: int = 100, hours_ago: int = 24, timeout: float = 30.0) -> dict[str, list[dict[str, Any]]]:
        """
        Fetch replies and mentions from Twitter via the message bus.

        Args:
            max_results: Maximum number of items to return (combined constraint for each list as provided by backend)
            hours_ago: Lookback window in hours
            timeout: Request timeout

        Returns:
            A dict with keys 'replies' and 'mentions', each a list of tweet dicts.
        """
        request = TwitterRepliesAndMentionsRequestMessage.create_message(max_results=max_results, hours_ago=hours_ago)
        self.logger.debug(f"Twitter replies and mentions request: {request}")
        response = await self.nats_publisher_adapter.request(request, timeout=timeout)
        self.logger.debug(f"Twitter replies and mentions response: {response}")
        parsed = TwitterRepliesAndMentionsResponseMessage.from_hai_message(response)
        return {"replies": parsed.replies, "mentions": parsed.mentions}

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Removes emojis and other non-standard characters from text.

        Args:
            text: The text to clean

        Returns:
            Cleaned text containing only standard ASCII characters
        """
        if not text:
            return text

        # This pattern matches emoji and other non-ASCII characters
        pattern = re.compile(r'[^\x00-\x7F]+')
        return pattern.sub('', text).strip()
