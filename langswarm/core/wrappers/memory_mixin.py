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

        If the agent already have memory initialized, we used that.
        If the memory is a LangChain memory instance, we use that.
        If non of these are available we return None. No external memory in use.

        :ToDo - Initialize LangChain memory (or other external memory) upon request.
        """
        if hasattr(agent, "memory") and agent.memory:
            return agent.memory

        if memory:
            if BaseMemory and isinstance(memory, BaseMemory):
                return memory
            raise ValueError(f"Invalid memory instance provided. Memory: {memory}")

        return None
