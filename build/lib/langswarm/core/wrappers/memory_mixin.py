from typing import Any, Optional

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
            if hasattr(memory, "load_memory_variables") and hasattr(memory, "save_context"):
                return memory
            raise ValueError(f"Invalid memory instance provided. Memory: {str(memory)}")

        return None

    def add_user_message(self, message: str):
        """
        Custom logic for handling user messages before delegating to LangChain's memory.

        ToDo: Add custom logic for handling in-memory.
        """
        print(f"Custom handling of user message: {message}")
        if hasattr(self.memory, "chat_memory") and hasattr(self.memory.chat_memory, "add_user_message"):
            self.memory.chat_memory.add_user_message(message)
        else:
            raise ValueError("Memory instance does not support user message addition.")

    def add_ai_message(self, message: str):
        """
        Custom logic for handling AI messages before delegating to LangChain's memory.

        ToDo: Add custom logic for handling in-memory.
        """
        print(f"Custom handling of AI message: {message}")
        if hasattr(self.memory, "chat_memory") and hasattr(self.memory.chat_memory, "add_ai_message"):
            self.memory.chat_memory.add_ai_message(message)
        else:
            raise ValueError("Memory instance does not support AI message addition.")
