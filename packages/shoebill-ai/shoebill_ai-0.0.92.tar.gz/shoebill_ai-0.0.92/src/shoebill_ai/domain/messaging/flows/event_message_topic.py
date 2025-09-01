from enum import Enum


class EventMessageTopic(str, Enum):
    """
    Represents a collection of predefined topics as an enumeration.

    This class is an enumeration that defines constant string values for use
    as topic identifiers. These topics represent specific actions or messages
    within a messaging or vector database management context. It ensures
    consistent usage of these predefined topics across the application.

    syntax: [hai].[source].[destination].[action]

    """
    # Events
    STARTUP = "hai.startup"
    SHUTDOWN = "hai.shutdown"
    ENTITY_OFFICIAL_UPDATE = "hai.entity.official.update"
    VECTOR_STALE_INFORMATION = "hai.vector.collection.stale.information"