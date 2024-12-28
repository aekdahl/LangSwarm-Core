
import os
import json
import logging

try:
    from langchain.memory import BaseMemory
except ImportError:
    BaseMemory = None  # Fallback if BaseMemory is not available

from ..utils.utilities import Utils

class LLM:
    """
    A class to interact with Large Language Models (LLMs) using LangChain or OpenAI.
    
    Provides methods for managing conversations, sending queries, and handling memory.
    """
    
    def __init__(
        self, 
        provider='langchain-openai',
        model='gpt-4o-mini-2024-07-18', 
        api_key=None,
        temperature=0.0,
        response_format='auto',
        system_prompt=None,
        utils=None,
        verbose=False,
        name=None, 
        team=None,
        memory=None,
        specialization=None
    ):
        """
        Initialize the LLM instance.

        Args:
            provider (str): LLM provider ('langchain-openai' or 'openai').
            model (str): Model name to use.
            api_key (str): API key for the provider.
            temperature (float): Sampling temperature for response variability.
            response_format (str): Expected format of the response.
            system_prompt (str): Initial system prompt to set the model context.
            utils (Utils): Utility instance for logging and text processing.
            verbose (bool): Verbosity flag for debugging and logs.
            name (str): Name of the bot.
            team (str): Associated team for the bot.
            specialization (str): Bot's area of expertise.
        """

        if provider == 'langchain-openai':
            self.api_key = self._get_api_key(provider, api_key)
            try:
                from langchain.chat_models import ChatOpenAI
            except ImportError:
                raise ImportError(
                    "Neither LangChain nor OpenAI is available. Please install them:\n"
                    "  pip install langchain langchain-openai"
                )
            self.client = ChatOpenAI(model=model, openai_api_key=self.api_key, temperature=temperature)
        elif provider == 'openai':
            self.api_key = self._get_api_key(provider, api_key)
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "OpenAI is not available. Please install it:\n"
                    "  pip install openai"
                )
            openai.api_key = self.api_key
            self.client = openai
        elif provider == 'wrapper':
            self.api_key = api_key
            team = team or 'wrappers'
        else:
            raise ValueError(f"Unsupported provider: {provider}.")

        self.provider = provider
        self.utils = utils or Utils()
        self.memory = memory if not isinstance(memory, list) else None
        self.in_memory = memory if isinstance(memory, list) else []
        self.model = model
        self.name = name
        self.team = team
        self.last_in_memory = ''
        self.verbose = verbose
        self.system_prompt = system_prompt
        self.specialization = specialization

        self.update_system_prompt()
        self.utils.bot_log(self.name, {"role": "admin", "content": "Bot was created."})
        
        self.logger = logging.getLogger("LangSwarm.Bot")
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        self.logger.info("Bot logger initialized.")

    def _get_api_key(self, provider, api_key):
        """
        Retrieve the API key from environment variables or fallback to the provided key.

        Args:
            provider (str): LLM provider.
            api_key (str): Provided API key.

        Returns:
            str: Resolved API key.
        """
        env_var_map = {
            "langchain-openai": "OPENAI_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_PALM_API_KEY",
        }
        env_var = env_var_map.get(provider.lower())

        if env_var and (key_from_env := os.getenv(env_var)):
            return key_from_env

        if api_key:
            return api_key

        raise ValueError(f"API key for {provider} not found. Set {env_var} or pass the key explicitly.")
    
    def update_system_prompt(self, system_prompt=None):
        """
        Update the system prompt for the conversation.

        Args:
            system_prompt (str): New system prompt to set.
        """
        if system_prompt:
            self.system_prompt = system_prompt

        if self.system_prompt:
            if self.memory:
                if hasattr(self.memory, "messages"):
                    messages = self.memory.messages  # Fetch current messages
                    if len(messages) > 0:
                        messages[0] = self.system_prompt
                    else:
                        messages = [self.system_prompt]
                    self.memory.clear()       # Clear the persistent store
                    for message in messages:
                        self.memory.add_message(message)  # Re-save the updated list

                    self.in_memory = messages
                    
                    self.utils.bot_log(self.name, {"role": "admin", "content": "Updated system prompt."})
                elif hasattr(self.memory, "chat_memory") and self.memory.chat_memory.messages:
                    messages = self.memory.chat_memory.messages  # Fetch current messages
                    if len(messages) > 0:
                        messages[0] = self.system_prompt
                    else:
                        messages = [self.system_prompt]
                    self.memory.clear()       # Clear the persistent store
                    for message in messages:
                        self.memory.add_message(message)  # Re-save the updated list

                    self.in_memory = messages
                    
                    self.utils.bot_log(self.name, {"role": "admin", "content": "Updated system prompt."})
            
                else:
                    raise ValueError('The memory instance has no attribute messages.')
            else:
                if self.in_memory and len(self.in_memory) > 0:
                    self.in_memory[0] = self.system_prompt
                else:
                    self.in_memory = [self.system_prompt]
                        
                self.utils.bot_log(self.name, {"role": "admin", "content": "Updated system prompt."})
            

    def add_message(self, content, role='assistant', remove_linebreaks=False):
        """
        Add a message to memory, if memory is enabled.

        Parameters:
        - role (str): The role of the message sender (e.g., "user", "assistant").
        - content (str): The message content.
        """
        if self.memory:
            self.memory.add_message(role, content)
            
        self.last_in_memory = content
        cleaned_message = self.utils.clean_text(content, remove_linebreaks=remove_linebreaks)
        if self.in_memory:
            self.in_memory.append({"role": role, "content": cleaned_message})
        else:
            self.in_memory = [{"role": role, "content": cleaned_message}]
        
        self.utils.bot_log(self.name, cleaned_message)
        
        if self.verbose:
            print(f"[{role}] {content}")
            
    def add_response(self, message, role='assistant', remove_linebreaks=False):
        """
        Temporary patch.
        """
        self.add_message(message, role=role, remove_linebreaks=remove_linebreaks)

    def clear_memory(self):
        """
        Clear the stored memory.
        """
        self.reset(clear = True)
        
    def remove(self, index=-1, query_and_response=False):
        """
        Remove a message from memory.

        Args:
            index (int): Index of the message to remove.
            query_and_response (bool): Whether to remove both query and response.
        """
        
        if self.memory:
            if hasattr(self.memory, "messages"):
                messages = self.memory.messages  # Fetch current messages
                if index < len(messages) and len(messages) > 0:
                    messages.pop(index)  # Remove the message
                if query_and_response and index < len(messages) and len(messages) > 0:
                    messages.pop(index)  # Remove the message
                self.memory.clear()       # Clear the persistent store
                for message in messages:
                    self.memory.add_message(message)  # Re-save the updated list
                
                self.in_memory = messages
            
            elif hasattr(self.memory, "chat_memory") and self.memory.chat_memory.messages:
                messages = self.memory.chat_memory.messages  # Fetch current messages
                if index < len(messages) and len(messages) > 0:
                    messages.pop(index)  # Remove the message
                if query_and_response and index < len(messages) and len(messages) > 0:
                    messages.pop(index)  # Remove the message
                self.memory.clear()       # Clear the persistent store
                for message in messages:
                    self.memory.add_message(message)  # Re-save the updated list
                
                self.in_memory = messages
            else:
                raise ValueError('The memory instance has no attribute messages.')
    
        elif self.in_memory and index < len(self.in_memory):
            del self.in_memory[index]
            self.utils.bot_log(self.name, {"role": "admin", "content": "Bot removed memory."})

            if query_and_response and index < len(self.in_memory) and self.in_memory:
                del self.in_memory[index]
                self.utils.bot_log(self.name, {"role": "admin", "content": "Bot removed memory again."})

    def chat(self, q=None, as_json=False, reset=False, erase_query=False, remove_linebreaks=False):
        """
        Send a query to the LLM and receive a response.

        Args:
            q (str): Query to send.
            as_json (bool): Whether to return the response as JSON.
            reset (bool): Whether to reset memory before sending the query.
            erase_query (bool): Whether to remove the query from memory after processing.
            remove_linebreaks (bool): Whether to remove line breaks from the query.

        Returns:
            str: The response from the LLM.
        """
        if reset:
            self.reset()

        if q:
            self.add_message(q, role='user', remove_linebreaks=remove_linebreaks)

        if self.provider == 'langchain-openai':
            if self.memory and BaseMemory is not None and isinstance(self.memory, BaseMemory):
                response = self.client.run(q).content
            else:
                response = self.client.invoke(self.in_memory).content
        elif self.provider == 'openai':
            completion = self.client.ChatCompletion.create(
                model=self.model,
                messages=self.in_memory,
                temperature=0.0
            )
            response = completion['choices'][0]['message']['content']
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        if q and erase_query:
            self.remove()

        self.utils.bot_log(self.name, response)

        if self.utils:
            self.utils.update_price_tokens_use_estimates(str(self.in_memory) + response, model=self.model, verbose=False)

        return response

    def reset(self, clear = False):
        """
        Reset the LLM state, including clearing memory and reset the system prompt.
        """
        if self.memory:
            self.memory.clear()
        
        self.utils.bot_log(self.name, {"role": "admin", "content": "Bot was reset."})
        self.in_memory = []
        self.last_in_memory = ''
                                                      
        if not clear:
            self.update_system_prompt()
        
        if self.verbose:
            print(f"Resetting {self.name} state.")

    def share_conversation(self):
        """
        Share the current conversation as a JSON string.

        Returns:
            str: JSON string of conversation memory (excluding system prompt).
        """
        return "".join(json.dumps(x) for x in self.in_memory[1:]) if self.in_memory else ""

    def get_last_in_memory(self):
        """
        Get the last message stored in memory.

        Returns:
            str: Content of the last message.
        """
        return self.last_in_memory or (self.in_memory[-1]['content'] if self.in_memory else "")

    def get_memory(self, start=1, stop=None):
        """
        Retrieve a subset of the conversation memory.

        Args:
            start (int): Start index for the memory slice.
            stop (int): End index for the memory slice.

        Returns:
            list: Subset of the conversation memory.
        """
        if self.memory:
            if hasattr(self.memory, "chat_memory") and self.memory.chat_memory.messages:
                return self.memory.chat_memory.messages[start:stop]
            elif hasattr(self.memory, "messages") and self.memory.messages:
                return self.memory.messages[start:stop]
            else:
                return []

        return self.in_memory[start:stop] if self.in_memory else []

    def set_memory(self, memory, clear=True):
        """
        Set the conversation memory.

        Args:
            memory (list): List of memory items to set.
            clear (bool): Whether to clear existing memory before setting.
        """
        
        if self.memory:
            if clear:
                self.memory.clear()
                self.in_memory = messages
                self.utils.bot_log(self.name, {"role": "admin", "content": "Cleared all memories."})
            else:
                self.in_memory.extend(memory)
                
            for mem in memory:
                self.memory.add_message(mem)
                self.utils.bot_log(self.name, mem)
            
        else:
            if clear:
                self.in_memory = [self.in_memory[0]] + memory if self.in_memory else memory
                self.utils.bot_log(self.name, {"role": "admin", "content": "Cleared all memories."})
            else:
                self.in_memory.extend(memory)
            
            for mem in memory:
                self.utils.bot_log(self.name, mem)
