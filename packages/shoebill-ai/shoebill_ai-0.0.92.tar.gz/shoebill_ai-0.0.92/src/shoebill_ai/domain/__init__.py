"""
Domain layer for the shoebill_ai package.

This package contains domain models, interfaces, and business logic.
It defines the core abstractions and rules of the application.
"""

__all__ = [
    # Agent interfaces
    'ModelFactory',
    'LlmChatRepository',
    'LlmEmbeddingRepository',

    # Agent classes
    'EmbeddingAgent',
    'MultimodalAgent',
    'TextAgent',
    'VisionAgent',
]

# Import agent interfaces
from .agents.interfaces.model_factory import ModelFactory
from .agents.interfaces.llm_chat_repository import LlmChatRepository
from .agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository
# Import agent classes
from .agents.embedding_agent import EmbeddingAgent
from .agents.multimodal_agent import MultimodalAgent
from .agents.text_agent import TextAgent
from .agents.vision_agent import VisionAgent


