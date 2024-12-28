from ..registry.agents import AgentRegistry
from typing import Any

class BaseWrapper:
    """
    Base class for wrapping agents, providing initialization and validation.
    """

    def __init__(self, name: str, agent: Any, **kwargs):
        self.name = name
        self.agent = agent
        self.kwargs = kwargs

        # Register the agent in the global registry
        AgentRegistry.register(
            name=name,
            agent=self,
            agent_type=type(agent).__name__,
            metadata=kwargs.get('metadata', {})
        )

    @staticmethod
    def _get_module_path(module_class: Any) -> str:
        """
        Returns the full module path of a given class or callable.
        :param module_class: The class or callable to get the module path for.
        :type module_class: Any
        :return: The module path
        :rtype: str
        """
        return (
            getattr(module_class, "__module__", "")
            + "."
            + getattr(module_class, "__name__", "")
        ).strip(".")
        
    @staticmethod
    def _is_openai_llm(agent: Any) -> bool:
        """
        Determine if the agent is an OpenAI LLM.
        Parameters:
        - agent: The agent to check.
        Returns:
        - bool: True if the agent is an OpenAI LLM, False otherwise.
        """
        return hasattr(agent, "model") and "openai" in str(type(agent)).lower()

    @staticmethod
    def _is_llamaindex_agent(agent):
        """
        Determine if the given agent is a LlamaIndex agent.
    
        Parameters:
        - agent: The agent to check.
    
        Returns:
        - bool: True if the agent is a LlamaIndex agent, False otherwise.
        """
        module_name = getattr(agent.__class__, "__module__", "")
        if "llama_index" in module_name:
            return True
        return callable(getattr(agent, "query", None))

    def _validate_agent(self):
        if not callable(self.agent) and not hasattr(self.agent, "run"):
            raise ValueError(f"Unsupported agent type: {type(self.agent)}")
