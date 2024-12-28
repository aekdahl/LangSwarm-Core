from typing import Any, Optional
from ..wrappers.agent_wrapper import AgentWrapper

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

        if agent_type.lower() == "llamaindex":
            if GPTSimpleVectorIndex is None or Document is None:
                raise ImportError("LlamaIndex is not installed. Install it with 'pip install llama-index'.")
            if not documents:
                raise ValueError("Documents must be provided to create a LlamaIndex agent.")
            doc_objects = [Document(text=doc) for doc in documents]
            agent = GPTSimpleVectorIndex(doc_objects)

        elif agent_type.lower() == "langchain-openai":
            # Example: Create a LangChain agent (e.g., OpenAI model)
            from langchain.llms import OpenAI
            model = kwargs.get("model", "gpt-3.5-turbo")
            agent = OpenAI(model=model, openai_api_key=kwargs.get("openai_api_key"))

        elif agent_type.lower() == "langchain":
            # Example: Create a LangChain agent (e.g., OpenAI model)
            from langchain.llms import OpenAI
            model = kwargs.get("model", "gpt-3.5-turbo")
            agent = OpenAI(model=model, openai_api_key=kwargs.get("openai_api_key"))

        elif agent_type.lower() == "huggingface":
            # Example: Create a Hugging Face agent
            from transformers import pipeline
            task = kwargs.get("task", "text-generation")
            model = kwargs.get("model", "gpt2")
            agent = pipeline(task, model=model)

        elif agent_type.lower() == "openai":
            # Example: Create an OpenAI agent directly
            import openai
            agent = openai.ChatCompletion

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
