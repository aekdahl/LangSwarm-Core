import pytest
from langswarm.core.factory.agents import AgentFactory
from langchain.memory import ConversationBufferMemory

def test_create_agent_with_memory():
    memory = ConversationBufferMemory()
    agent = AgentFactory.create(
        name="test_agent",
        agent_type="langchain-openai",
        memory=memory,
        model="gpt-3.5-turbo",
        openai_api_key="test-key"
    )
    assert agent.name == "test_agent"
    assert agent.memory == memory

def test_create_unsupported_agent_type():
    with pytest.raises(ValueError) as excinfo:
        AgentFactory.create(name="test_agent", agent_type="unsupported-type")
    assert "Unsupported agent type" in str(excinfo.value)
