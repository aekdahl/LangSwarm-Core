from langswarm.core.registry.agents import AgentRegistry

def test_register_agent():
    mock_agent = {"name": "test_agent"}
    AgentRegistry.register(name="test_agent", agent=mock_agent, agent_type="langchain")
    assert "test_agent" in AgentRegistry.list()

def test_get_registered_agent():
    mock_agent = {"name": "test_agent"}
    AgentRegistry.register(name="test_agent", agent=mock_agent, agent_type="langchain")
    agent = AgentRegistry.get("test_agent")
    assert agent["agent"] == mock_agent

def test_remove_agent():
    mock_agent = {"name": "test_agent"}
    AgentRegistry.register(name="test_agent", agent=mock_agent, agent_type="langchain")
    AgentRegistry.remove("test_agent")
    assert "test_agent" not in AgentRegistry.list()
