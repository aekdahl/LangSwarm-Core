from typing import Any, Optional
from ..wrappers.generic import AgentWrapper
from ..utils.utilities import Utils

try:
    from llama_index import GPTSimpleVectorIndex, Document
except ImportError:
    GPTSimpleVectorIndex = None
    Document = None

class AgentFactory:
    """
    A factory for creating LangSwarm agents, including LangChain, Hugging Face, OpenAI, and LlamaIndex agents.
    """

    @staticmethod
    def create(
        name: str,
        agent_type: str,
        documents: Optional[list] = None,
        memory: Optional[Any] = None,
        langsmith_api_key: Optional[str] = None,
        **kwargs,
    ) -> AgentWrapper:
        """
        Create an agent with the given parameters.

        Parameters:
        - name (str): The name of the agent.
        - agent_type (str): The type of agent ("langchain", "huggingface", "openai", "llamaindex", etc.).
        - documents (list, optional): Documents for LlamaIndex agents.
        - memory (optional): A memory instance to use with the agent.
        - langsmith_api_key (str, optional): API key for LangSmith logging.
        - kwargs: Additional parameters for the agent.

        Returns:
        - AgentWrapper: A wrapped agent ready for use.
        """
        agent = None
        utils = Utils()

        if agent_type.lower() == "llamaindex":
            if GPTSimpleVectorIndex is None or Document is None:
                raise ImportError("LlamaIndex is not installed. Install it with 'pip install llama-index'.")
            if not documents:
                raise ValueError("Documents must be provided to create a LlamaIndex agent.")
            doc_objects = [Document(text=doc) for doc in documents]
            agent = GPTSimpleVectorIndex(doc_objects)

        elif agent_type.lower() == "langchain-openai" or agent_type.lower() == "langchain":
            # Example: Create a LangChain agent (e.g., OpenAI model)
            model = kwargs.get("model", "gpt-3.5-turbo")
            api_key = utils._get_api_key('langchain-openai', kwargs.get("openai_api_key"))
            
            # Use ChatOpenAI for chat models
            if model.lower().startswith("gpt-"):
                try:
                    from langchain_openai import ChatOpenAI
                except ImportError:
                    from langchain.chat_models import ChatOpenAI
                agent = ChatOpenAI(model=model, openai_api_key=api_key)
            # Use OpenAI for text models
            else:
                try:
                    from langchain_community.llms import OpenAI
                except ImportError:
                    from langchain.llms import OpenAI
                agent = OpenAI(model=model, openai_api_key=api_key)

        elif agent_type.lower() == "huggingface":
            # Example: Create a Hugging Face agent
            from transformers import pipeline
            task = kwargs.get("task", "text-generation")
            model = kwargs.get("model", "gpt2")
            agent = pipeline(task, model=model)

        elif agent_type.lower() == "openai":
            # Example: Create an OpenAI agent directly
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "OpenAI is not available. Please install it:\n"
                    "  pip install openai"
                )
                
            openai.api_key = utils._get_api_key('openai', kwargs.get("openai_api_key"))
            agent = openai
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        # Wrap the agent using AgentWrapper
        return AgentWrapper(
            name=name,
            agent=agent,
            memory=memory,
            langsmith_api_key=langsmith_api_key,
            **kwargs,
        )
