from typing import Any, Optional, Dict, Callable

from ..base.bot import LLM
from .base_wrapper import BaseWrapper
from .logging_mixin import LoggingMixin
from .memory_mixin import MemoryMixin
from .rag_mixin import RAGMixin
from .util_mixin import UtilMixin

# ToDo: import the langswarm.memory features for RAG
# If not available, RAG and thereby also tools will not be available..

try:
    from langswarm.memory.defaults.prompts import RagInstructions
except ImportError:
    RagInstructions = None

try:
    from langswarm.synapse.defaults.prompts import ToolInstructions
except ImportError:
    ToolInstructions = None

class AgentWrapper(LLM, BaseWrapper, LoggingMixin, MemoryMixin, RAGMixin, UtilMixin):
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
        retrievers=None, 
        middleware=None, 
        context_limit=None,
        system_prompt=None,
        capability_instruction=None,
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
            provider="wrapper", 
            memory=memory,
            system_prompt=system_prompt,
            capability_instruction=capability_instruction,
            tool_instruction=tool_instruction or ToolInstructions,
            rag_instruction=rag_instruction or RagInstructions,
            **kwargs
        )
        
        RAGMixin.__init__(self)  # Initialize RAGMixin
        UtilMixin.__init__(self)  # Initialize UtilMixin

        # Automatically add provided retrievers
        if retrievers:
            for retriever_name, retriever_config in retrievers.items():
                adapter = retriever_config.get("adapter")
                collection_name = retriever_config.get("collection_name", "default")
                self.add_retriever(retriever_name, adapter, collection_name)
                
        self._initialize_logger(name, agent, langsmith_api_key)  # Use LoggingMixin's method
        self.memory = self._initialize_memory(agent, memory, self.in_memory)
        self.is_conversational = is_conversational
        self.middleware = middleware
        self.model_details = self._get_model_details(model=kwargs.get("model", None))
        self.model_details["limit"] = context_limit or self.model_details["limit"]
        
        # ToDo: Move to agent creation and setup..
        #from ..middleware.layer import MiddlewareLayer
        #self.tools = tools or {}
        #self.capabilities = capabilities or {}
        #self.middleware = MiddlewareLayer(capability_registry=self.capabilities, tools=self.tools)  # Middleware initialized
        
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
                self.log_event(f"Response sent back from Agent {self.name}: {response}", "info")

            return response

        except Exception as e:
            self.log_event(f"Error for agent {self.name}: {str(e)}", "error")
            raise
        
    def chat(self, q=None, reset=False, erase_query=False, remove_linebreaks=False, use_rag=False, retriever_names=None, **kwargs):
        """
        Process a query using the wrapped agent, optionally using RAG.

        Parameters:
        - q (str): Query string.
        - reset (bool): Whether to reset memory before processing.
        - erase_query (bool): Whether to erase the query after processing.
        - remove_linebreaks (bool): Remove line breaks from the query.
        :param use_rag: Whether to use RAG for the query.
        :param retriever_names: Names of retrievers to use if use_rag is True.

        Returns:
        - str: The agent's response.
        """
        response = "No Query was submitted."
        
        if reset:
            self.in_memory = []
            if self.memory and hasattr(self.memory, clear):
                self.memory.clear()

        rag = ""
        rag_tools = ""
        rag_capabilities = ""
        middleware_response = ""
        if q:
            if use_rag:
                
                if self.dynamic_retrieval_decision:
                    # Make a decision to retrieve or not.
                    if self.dynamic_retrieval_decision.retrieve(self.share_conversation(), q):
                
                        # ToDo: Consider re-writing the query optimized for RAG..
                        # rag_query = ... <-- Probably using an agent.

                        rag = self.use_rag(query=q, use_all=not retriever_names, retriever_names=retriever_names)
                        if rag != "":
                            rag = "\n\nRETRIEVED INFORMATION\n\n"+rag
            
            if self.middleware:
                # - Retrieve usable tools
                # - Create a new retriever only for this
                if self.indexing_is_available:
                    results = self.query_index(q)
                    rag_tools = "\n".join([res["text"] for res in results]) if results else ""
                    if rag_tools != "":
                        rag = "\n\nAVAILABLE TOOLS\n\n"+rag_tools+rag

                # - Retrieve usable capabilities (later)
                # - Create a new retriever only for this
                if self.indexing_is_available:
                    results = self.query_index(q)
                    rag_capabilities = "\n".join([res["text"] for res in results]) if results else ""
                    if rag_capabilities != "":
                        rag = "\n\nAVAILABLE CAPABILITIES\n\n"+rag_capabilities+rag

            q = "\n\nINITIAL QUERY\n\n"+q
            response = self._call_agent(rag+q, erase_query=erase_query, remove_linebreaks=remove_linebreaks)

            if self.middleware:
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
