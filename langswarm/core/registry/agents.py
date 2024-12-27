# agents.py
class AgentRegistry:
    """
    Centralized registry for managing available LLM agents.
    """

    _registry = {}

    @classmethod
    def register(cls, name, agent, agent_type, metadata=None):
        """
        Register an agent with the registry.

        Parameters:
        - name (str): Unique identifier for the agent.
        - agent: The agent instance to register.
        - agent_type (str): Type of the agent (e.g., 'langchain', 'huggingface').
        - metadata (dict): Optional additional metadata about the agent.
        """
        cls._registry[name] = {
            "agent": agent,
            "type": agent_type,
            "metadata": metadata or {},
        }

    @classmethod
    def get(cls, name):
        """
        Retrieve an agent's details by name.

        Parameters:
        - name (str): The name of the agent.

        Returns:
        - dict: Agent details, or None if not found.
        """
        return cls._registry.get(name)

    @classmethod
    def list(cls):
        """
        List all registered agents.

        Returns:
        - dict: All agents in the registry.
        """
        return cls._registry

    @classmethod
    def remove(cls, name):
        """
        Remove an agent from the registry.

        Parameters:
        - name (str): The name of the agent.
        """
        if name in cls._registry:
            del cls._registry[name]
