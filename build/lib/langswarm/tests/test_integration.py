import os

from langswarm.core.factory.agents import AgentFactory
from langchain.memory import ConversationBufferMemory

api_key = os.getenv("OPENAI_API_KEY_TEST")

def test_full_agent_with_memory():
    memory = ConversationBufferMemory()
    agent = AgentFactory.create(
        name="integration_test_agent",
        agent_type="langchain-openai",
        memory=memory,
        model="gpt-3.5-turbo",
        openai_api_key=api_key
    )

    response1 = agent.chat("What is LangSwarm-Core?")
    assert "LangSwarm-Core" in response1  # Simplified response assertion for mock API
    
    response2 = agent.chat("What have we discussed so far?")
    assert "LangSwarm-Core" in response2  # Memory integration validation
