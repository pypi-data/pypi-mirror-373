from h_message_bus import NatsPublisherAdapter

from ...domain.messaging.telegram.tg_message_request_message import TelegramMessageRequestMessage
from ...domain.messaging.telegram.tg_user_message_reply_request_message import TelegramUserMessageReplyRequestMessage


class TelegramService:
    def __init__(self, nats_publisher_adapter: NatsPublisherAdapter):
        self.nats_publisher_adapter = nats_publisher_adapter

    async def reply_to_tg_user(self, message: str, chat_id: int,
                       message_id: int):

        message = TelegramUserMessageReplyRequestMessage.create_message(message, chat_id, message_id)
        await self.nats_publisher_adapter.publish(message)

    async def send_message(self, message: str, chat_id: int):
        message = TelegramMessageRequestMessage.create_message(message, chat_id)
        await self.nats_publisher_adapter.publish(message)
