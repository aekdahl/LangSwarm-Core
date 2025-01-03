from typing import Any, Optional

from ..base.bot import LLM
from .base_wrapper import BaseWrapper
from .logging_mixin import LoggingMixin
from .memory_mixin import MemoryMixin


class AgentWrapper(LLM, BaseWrapper, LoggingMixin, MemoryMixin):
    """
    A unified wrapper for LLM agents, combining memory management, logging, and LangSmith integration.
    """

    def __init__(self, name, agent, memory=None, is_conversational=False, langsmith_api_key=None, **kwargs):
        kwargs.pop("provider", None)  # Remove `provider` if it exists
        super().__init__(name=name, agent=agent, provider="wrapper", **kwargs)
        
        self.logger = self._initialize_logger(name, langsmith_api_key)
        self.memory = self._initialize_memory(agent, memory, self.in_memory)
        self.is_conversational = is_conversational

    def chat(self, q=None, reset=False, erase_query=False, remove_linebreaks=False):
        """
        Process a query using the wrapped agent.

        Parameters:
        - q (str): Query string.
        - reset (bool): Whether to reset memory before processing.
        - erase_query (bool): Whether to erase the query after processing.
        - remove_linebreaks (bool): Remove line breaks from the query.

        Returns:
        - str: The agent's response.
        """
        if reset:
            self.in_memory = []
            if self.memory and hasattr(self.memory, clear):
                self.memory.clear()

        if q:
            self.add_message(q, role="user", remove_linebreaks=remove_linebreaks)
            self.logger.info(f"Query sent to agent {self.name}: {q}")

        try:
            # Handle different agent types
            if hasattr(self.agent, "run"):
                # LangChain agents
                response = self.agent.run(q)
                if hasattr(self.agent, "memory") and self.agent.memory:
                    # Memory is already managed by the agent
                    response = self.agent.run(q)
                else:
                    # No memory, include context manually
                    context = " ".join([message["content"] for message in self.in_memory]) if self.in_memory else ""
                    full_query = f"{context}\n{q}"
                    response = self.agent.run(full_query)
            elif self._is_llamaindex_agent(self.agent):
                # LlamaIndex agents
                context = " ".join([message["content"] for message in self.in_memory])
                response = self.agent.query(context if self.memory else q).response
            elif callable(self.agent):
                # Hugging Face agents
                context = " ".join([message["content"] for message in self.in_memory]) if self.is_conversational else q
                response = self.agent(context)
            elif self._is_openai_llm(self.agent) or hasattr(self.agent, "ChatCompletion"):
                try:
                    completion = self.agent.ChatCompletion.create(
                        model=self.model,
                        messages=self.in_memory,
                        temperature=0.0
                    )
                    response = completion['choices'][0]['message']['content']
                except:
                    completion = self.agent.chat.completions.create(
                        model=self.model,
                        messages=self.in_memory,
                        temperature=0.0
                    )
                    response = completion.choices[0].message.content
            else:
                raise ValueError(f"Unsupported agent type: {type(self.agent)} for agent: {self.agent}")

            # Parse and log response
            response = self._parse_response(response)
            self.logger.info(f"Agent {self.name} response: {response}")

            if erase_query:
                self.remove()

            return response

        except Exception as e:
            self._log_error(str(e))
            raise

    def _parse_response(self, response: Any) -> str:
        """
        Parse the response from the wrapped agent.

        Parameters:
        - response: The agent's raw response.

        Returns:
        - str: The parsed response.
        """
        if hasattr(response, "content"):
            return response.content
        elif isinstance(response, dict):
            return response.get("generated_text", "")
        return str(response)

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the wrapped agent.

        Parameters:
        - name (str): The attribute name.

        Returns:
        - The attribute from the wrapped agent.
        """
        return getattr(self.agent, name)
