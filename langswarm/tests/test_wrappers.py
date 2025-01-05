import pytest
from langswarm.core.wrappers.generic import AgentWrapper

class MockAgent:
    __module__ = "langchain.agents.mock_agent"
    
    def run(self, query):
        return f"Mock response to: {query}"

def test_agent_wrapper_basic_interaction():
    mock_agent = MockAgent()
    wrapper = AgentWrapper(name="mock_agent", agent=mock_agent, memory=None)
    
    response = wrapper.chat("What is LangSwarm?")
    assert "Mock response to: What is LangSwarm?" in response
    assert wrapper.name == "mock_agent"

def test_agent_wrapper_with_memory():
    mock_agent = MockAgent()
    wrapper = AgentWrapper(name="mock_agent", agent=mock_agent, memory=[])
    
    wrapper.chat("Remember this: LangSwarm is cool.")
    assert len(wrapper.in_memory) == 1
    assert wrapper.in_memory[0]["content"] == "Remember this: LangSwarm is cool."
