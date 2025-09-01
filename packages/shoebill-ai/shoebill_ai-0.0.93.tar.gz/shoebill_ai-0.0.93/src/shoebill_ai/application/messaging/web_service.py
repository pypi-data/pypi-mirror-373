import logging
from typing import Dict, Any

from h_message_bus import NatsPublisherAdapter

from ...domain.messaging.web.web_get_docs_request_message import WebGetDocsRequestMessage
from ...domain.messaging.web.web_get_docs_response_message import WebGetDocsResponseMessage
from ...domain.messaging.web.web_get_twitter_profiles_from_url_request_message import \
    WebGetTwitterProfilesFromUrlRequestMessage
from ...domain.messaging.web.web_get_twitter_profiles_from_url_response_message import \
    WebGetTwitterProfilesFromUrlResponseMessage


class WebService:
    def __init__(self, nats_publisher_adapter: NatsPublisherAdapter):
        self.nats_publisher_adapter = nats_publisher_adapter
        self.logger = logging.getLogger(__name__)


    async def get_docs_from_web(self, url: str, timeout: float = 30.0)-> list[Dict[str, Any]] :
        request = WebGetDocsRequestMessage.create_message(
            root_url=url)
        self.logger.debug("Requested get docs for url")
        response = await self.nats_publisher_adapter.request(request, timeout=timeout)
        response_message = WebGetDocsResponseMessage.from_hai_message(response)

        return response_message.docs

    async def get_twitter_profiles_from_community_web(self, url: str, timeout: float = 30.0)-> list[str] :
        request = WebGetTwitterProfilesFromUrlRequestMessage.create_message(
            url=url)
        self.logger.debug("Requested get twitter profiles from url")

        response = await self.nats_publisher_adapter.request(request, timeout=timeout)
        response_message = WebGetTwitterProfilesFromUrlResponseMessage.from_hai_message(response)

        return response_message.profile_names
