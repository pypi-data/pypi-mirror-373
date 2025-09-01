import pytest

from src.shoebill_ai.domain import LlmChatRepository
from src.shoebill_ai.domain.agents.text_agent import TextAgent


@pytest.fixture
def text_agent(mocker):
    """
    Fixture to create a TextAgent instance with necessary dependencies mocked.
    """
    mock_ollama_factory = mocker.patch(
        "src.shoebill_ai.domain.agents.text_agent.OllamaFactory"
    )
    mock_llm_chat_repository = mocker.Mock(spec=LlmChatRepository)
    mock_ollama_factory.return_value.create_chat_repository.return_value = mock_llm_chat_repository

    agent = TextAgent(
        api_url="https://api.example.com",
        model_name="test-model",
        system_prompt="System Prompt",
        api_token="test-token",
        tools=[{"name": "tool1"}],
        timeout=30,
        options={"option1": "value1"},
        provider="ollama",
    )
    return agent


def test_text_agent_initialization(mocker):
    """
    Tests that the TextAgent initializes correctly with OllamaFactory and chat repository.
    """
    mock_ollama_factory = mocker.patch(
        "src.shoebill_ai.domain.agents.text_agent.OllamaFactory"
    )
    mock_llm_chat_repository = mocker.Mock(spec=LlmChatRepository)
    mock_ollama_factory.return_value.create_chat_repository.return_value = mock_llm_chat_repository

    agent = TextAgent(
        api_url="https://api.example.com",
        model_name="test-model",
        system_prompt="System Prompt",
        api_token="test-token",
        tools=[{"name": "tool1"}],
        timeout=30,
        options={"option1": "value1"},
        provider="ollama",
    )

    mock_ollama_factory.assert_called_once_with(
        api_url="https://api.example.com",
        model_name="test-model",
        system_prompt="System Prompt",
        api_token="test-token",
        tools=[{"name": "tool1"}],
        timeout=30,
        options={"option1": "value1"},
    )
    mock_ollama_factory.return_value.create_chat_repository.assert_called_once()
    assert agent.llm_chat_repository == mock_llm_chat_repository


def test_text_agent_chat_method(mocker, text_agent):
    """
    Tests that the chat method of the TextAgent calls the llm_chat_repository.chat method
    with the provided parameters.
    """
    mock_chat = text_agent.llm_chat_repository.chat

    user_message = "Hello, how are you?"
    chat_history = [{"user": "Hi"}]
    tools = [{"name": "tool2"}]
    system_prompt = "Custom System Prompt"

    text_agent.chat(
        user_message=user_message,
        system_prompt=system_prompt,
        chat_history=chat_history,
        tools=tools,
    )

    mock_chat.assert_called_once_with(
        user_message=user_message,
        system_prompt=system_prompt,
        chat_history=chat_history,
        tools=tools,
    )


def test_text_agent_chat_method_default_values(mocker, text_agent):
    """
    Tests the chat method of TextAgent with default system_prompt and tools when
    they aren't explicitly provided.
    """
    mock_chat = text_agent.llm_chat_repository.chat

    user_message = "What is the weather like today?"
    chat_history = [{"user": "What's the forecast?"}]

    text_agent.chat(user_message=user_message, chat_history=chat_history)

    mock_chat.assert_called_once_with(
        user_message=user_message,
        system_prompt=text_agent.system_prompt,
        chat_history=chat_history,
        tools=text_agent.tools,
    )
