from typing import Any, Optional

try:
    from langchain.memory import BaseMemory
except ImportError:
    BaseMemory = None

class MemoryMixin:
    """
    Mixin for memory management.
    """

    def _initialize_memory(self, agent: Any, memory: Optional[Any], in_memory: list) -> Optional[Any]:
        """
        Initialize or validate memory for the agent.
        """
        if hasattr(agent, "memory") and agent.memory:
            return agent.memory

        if memory:
            if BaseMemory and isinstance(memory, BaseMemory):
                return memory
            raise ValueError("Invalid memory instance provided.")

        return in_memory
