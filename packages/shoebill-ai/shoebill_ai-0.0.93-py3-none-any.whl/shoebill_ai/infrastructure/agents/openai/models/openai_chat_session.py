from typing import List

from .openai_chat_message import OpenAIChatMessage


class OpenAIChatSession:
    def __init__(self, session_id: str, messages: List[OpenAIChatMessage]):
        self.session_id = session_id
        self.messages = messages

    def add_message(self, message: OpenAIChatMessage):
        self.messages.append(message)