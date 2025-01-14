from typing import Any, Optional, Dict, Callable

from ..base.bot import LLM
from .base_wrapper import BaseWrapper
from .logging_mixin import LoggingMixin
from .memory_mixin import MemoryMixin
from .indexing_mixin import IndexingMixin
from ..middleware.layer import MiddlewareLayer


class AgentWrapper(LLM, BaseWrapper, LoggingMixin, MemoryMixin, IndexingMixin):
    """
    A unified wrapper for LLM agents, combining memory management, logging, and LangSmith integration.
    """

    def __init__(
        self, 
        name, 
        agent, 
        memory=None, 
        is_conversational=False, 
        langsmith_api_key=None, 
        tools: Optional[Dict[str, Callable]] = None,
        capabilities: Optional[Dict[str, Callable]] = None,
        **kwargs
    ):
        kwargs.pop("provider", None)  # Remove `provider` if it exists
        if memory and hasattr(memory, "input_key"):
            memory.input_key = memory.input_key or "input"
            
        if memory and hasattr(memory, "output_key"):
            memory.output_key = memory.output_key or "output"
            
        IndexingMixin.__init__(self, index_path=kwargs.get("index_path", "index.json"))
        super().__init__(name=name, agent=agent, provider="wrapper", memory=memory, **kwargs)
        
        self._initialize_logger(name, agent, langsmith_api_key)  # Use LoggingMixin's method
        self.memory = self._initialize_memory(agent, memory, self.in_memory)
        self.is_conversational = is_conversational
        self.tools = tools or {}
        self.capabilities = capabilities or {}
        self.middleware = MiddlewareLayer(capability_registry=self.capabilities, tools=self.tools)  # Middleware initialized

    def _call_agent(self, q, erase_query=False, remove_linebreaks=False):

        if q:
            self.add_message(q, role="user", remove_linebreaks=remove_linebreaks)
            self.log_event(f"Query sent to agent {self.name}: {q}", "info")
            
        try:
            # Handle different agent types
            if self._is_langchain_agent(self.agent): # hasattr(self.agent, "run"):
                # LangChain agents
                if hasattr(self.agent, "memory") and self.agent.memory:
                    # Memory is already managed by the agent
                    response = self.agent.run(q)
                else:
                    # No memory, include context manually
                    if callable(self.agent):
                        # Direct calls are deprecated, so we use .invoke() instead.
                        if self.in_memory:
                            response = self.agent.invoke(self.in_memory)
                        else:
                            response = self.agent.invoke(q)
                    else:
                        context = " ".join([message["content"] for message in self.in_memory]) if self.in_memory else q
                        response = self.agent.run(context)
            elif self._is_llamaindex_agent(self.agent):
                # LlamaIndex agents
                context = " ".join([message["content"] for message in self.in_memory])
                response = self.agent.query(context if self.memory else q).response
            elif self._is_hugging_face_agent(self.agent) and callable(self.agent):
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
            self.log_event(f"Agent {self.name} response: {response}", "info")

            if q and erase_query:
                self.remove():
            elif q:
                self.add_message(response, role="assistant", remove_linebreaks=remove_linebreaks)
                self.log_event(f"Response sent back from Agent {self.name}: {response}", "info")

            return response

        except Exception as e:
            self.log_event(f"Error for agent {self.name}: {str(e)}", "error")
            raise
        
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
        response = "No Query was submitted."
        
        if reset:
            self.in_memory = []
            if self.memory and hasattr(self.memory, clear):
                self.memory.clear()

        rag = ""
        middleware_response = ""
        if q:
            # RAG IMPLEMENTATION
            if self.indexing_is_available:
                results = self.query_index(q)
                rag = "\n".join([res["text"] for res in results]) if results else ""
                if rag != "":
                    rag = "\n\nRETRIEVED INFORMATION\n\n"+rag
        
            # ToDo: Figure out if RAG should be included when sending to middleware
        
            q = "\n\nINITIAL QUERY\n\n"+q
            response = self._call_agent(self, rag+q, erase_query=erase_query, remove_linebreaks=remove_linebreaks)

            # MIDDLEWARE IMPLEMENTATION
            middleware_result, middleware_response = self.middleware.process_input(response)
            if middleware_result == 201:  # Middleware used tool or capability successfully
                middleware_response = "\n\nTOOL OR CAPABILITY OUTPUT\n\n"+middleware_response
                response = self._call_agent(middleware_response+rag+q, erase_query=erase_query, remove_linebreaks=remove_linebreaks)

    return response

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
