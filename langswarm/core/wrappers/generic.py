from typing import Any, Optional, Dict, Callable, List

from ..base.bot import LLM
from .base_wrapper import BaseWrapper
from .logging_mixin import LoggingMixin
from .memory_mixin import MemoryMixin
from .util_mixin import UtilMixin
from .middleware import MiddlewareMixin

try:
    from langswarm.cortex.defaults.prompts.system import PluginInstructions
except ImportError:
    PluginInstructions = None
    
try:
    from langswarm.memory.defaults.prompts.system import RagInstructions
except ImportError:
    RagInstructions = None

try:
    from langswarm.synapse.defaults.prompts.system import ToolInstructions
except ImportError:
    ToolInstructions = None


class AgentWrapper(LLM, BaseWrapper, LoggingMixin, MemoryMixin, UtilMixin, MiddlewareMixin):
    """
    A unified wrapper for LLM agents, combining memory management, logging, and LangSmith integration.
    """
    __allow_middleware = True  # Private class-level flag
    
    def __init_subclass__(cls, **kwargs):
        """Disable feature in subclasses at the class level."""
        super().__init_subclass__(**kwargs)
        cls.__allow_middleware = False  # Enforce restriction in all subclasses

    def __init__(
        self, 
        name, 
        agent, 
        memory=None, 
        is_conversational=False, 
        langsmith_api_key=None, 
        rag_registry=None, 
        context_limit=None,
        system_prompt=None,
        tool_registry=None, 
        plugin_registry=None, 
        plugin_instruction=None,
        tool_instruction=None,
        rag_instruction=None,
        **kwargs
    ):
        kwargs.pop("provider", None)  # Remove `provider` if it exists
        if memory and hasattr(memory, "input_key"):
            memory.input_key = memory.input_key or "input"
            
        if memory and hasattr(memory, "output_key"):
            memory.output_key = memory.output_key or "output"

        
        super().__init__(
            name=name, 
            agent=agent,  
            memory=memory,
            provider="wrapper",
            system_prompt=system_prompt,
            rag_instruction=(
                (
                    f"{rag_instruction or RagInstructions} \n\n"
                    f"-- AVAILABLE RAGS AND RETRIEVERS -- \n"
                    f"{'\n\n'.join(rag_registry.list_rags())}"
                )
                if (rag_instruction or RagInstructions) 
                and rag_registry is not None 
                and rag_registry.count_rags() > 0
                else None
            ),
            tool_instruction = (
                (
                    f"{tool_instruction or ToolInstructions} \n\n"
                    f"-- AVAILABLE TOOLS -- \n"
                    f"{'\n\n'.join(tool_registry.list_tools())}"
                )
                if (tool_instruction or ToolInstructions) 
                and tool_registry is not None 
                and tool_registry.count_tools() > 0
                else None
            ),
            plugin_instruction=(
                (
                    f"{plugin_instruction or PluginInstructions} \n\n"
                    f"-- AVAILABLE PLUGINS -- \n"
                    f"{'\n\n'.join(plugin_registry.list_plugins())}"
                )
                if (plugin_instruction or PluginInstructions) 
                and plugin_registry is not None 
                and plugin_registry.count_plugins() > 0
                else None
            ),
            **kwargs
        )
        
        UtilMixin.__init__(self)  # Initialize UtilMixin
        MiddlewareMixin.__init__(
            self, 
            tool_registry=tool_registry, 
            plugin_registry=plugin_registry,
            rag_registry=rag_registry 
        )  # Initialize MiddlewareMixin
                
        self.timeout = kwargs.get("timeout", 60) # 60 second timeout.
        self._initialize_logger(name, agent, langsmith_api_key)  # Use LoggingMixin's method
        self.memory = self._initialize_memory(agent, memory, self.in_memory)
        self.is_conversational = is_conversational
        self.model_details = self._get_model_details(model=kwargs.get("model", None))
        self.model_details["limit"] = context_limit or self.model_details["limit"]

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
                self.remove()
            elif q:
                self.add_message(response, role="assistant", remove_linebreaks=remove_linebreaks)
                #self.log_event(f"Response sent back from Agent {self.name}: {response}", "info")

            return response

        except Exception as e:
            self.log_event(f"Error for agent {self.name}: {str(e)}", "error")
            raise
        
    def chat(self, q=None, reset=False, erase_query=False, remove_linebreaks=False, **kwargs):
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

        if q:
            #q = "\n\nINITIAL QUERY\n\n"+q
            response = self._call_agent(q, erase_query=erase_query, remove_linebreaks=remove_linebreaks)

            if self.__allow_middleware:
                # MIDDLEWARE IMPLEMENTATION
                middleware_status, middleware_response = self.to_middleware(response)
                if middleware_status == 201:  # Middleware used tool successfully
                    #middleware_response = "\n\nTOOL OR CAPABILITY OUTPUT\n\n"+middleware_response
                    response = self._call_agent(
                        middleware_response, erase_query=erase_query, remove_linebreaks=remove_linebreaks)

        return response
    
    def _format_final_response(self, query: List[str]) -> str:
        """
        Parse the response from multi-steps.

        Parameters:
        - query: The agent's raw response.

        Returns:
        - str: The final response.
        """
        joined = "\n\n".join(query)
        final_query = f"Please summarize and format the following response history into one coherent response back to the user. \n\n-- RESPONSE HISTORY --\n\n{joined}"
        return self._call_agent(final_query)

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
