import time
import hashlib
from io import StringIO
from html.parser import HTMLParser

# pip install pyyaml
import yaml
import ast
import uuid
import json
import re
import os

#%pip install --upgrade tiktoken
import tiktoken

try:
    from transformers import GPT2Tokenizer
except ImportError:
    GPT2Tokenizer = None

class Utils:
    def __init__(self, ppm=None):
        self.ppm = ppm
        self.total_tokens_estimate = 0
        self.total_price_estimate = 0
        if GPT2Tokenizer:
            self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        else:
            self.gpt2_tokenizer = None
        self.bot_logs = []

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
            "langchain": "OPENAI_API_KEY",
            "langchain-openai": "OPENAI_API_KEY",
            "langchain-anthropic": "ANTHROPIC_API_KEY",
            "langchain-cohere": "COHERE_API_KEY",
            "langchain-google-palm": "GOOGLE_CLOUD_API_KEY",
            "langchain-azure-openai": "AZURE_OPENAI_API_KEY",
            "langchain-writer": "WRITER_API_KEY",
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_PALM_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }
        env_var = env_var_map.get(provider.lower())

        if env_var and (key_from_env := os.getenv(env_var)):
            return key_from_env

        if api_key:
            return api_key

        raise ValueError(f"API key for {provider} not found. Set {env_var} or pass the key explicitly.")
        
    def bot_log(self, bot, message):
        self.bot_logs.append((bot, message))

    def print_current_estimates(self):
        """Print the current estimates of total tokens and price."""
        print("Estimated total tokens:", self.total_tokens_estimate)
        print("Estimated total price: $", self.total_price_estimate)

    def update_price_tokens_use_estimates(self, string, model="gpt-4-1106-preview", price=0.150, verbose=False):
        """Update the total token and price estimates based on a string."""
        tokens, price = self.price_tokens_from_string(string, model, price, verbose)
        self.total_tokens_estimate += tokens
        self.total_price_estimate += price
        if verbose:
            self.print_current_estimates()

    def price_tokens_from_string(self, string, encoding_name="gpt-4-1106-preview", price=0.150, verbose=False):
        """
        Returns the number of tokens in a text string and its estimated price.
        
        Uses tiktoken as the primary tokenizer and GPT2Tokenizer as a fallback.
        """
        encoding_name = encoding_name or "gpt-4-1106-preview"
        try:
            # Attempt to use tiktoken for tokenization
            encoding = tiktoken.encoding_for_model(encoding_name)
            num_tokens = len(encoding.encode(string))
        except Exception:
            if verbose:
                print("tiktoken failed, falling back to GPT2Tokenizer.")
            # Fallback to GPT2Tokenizer
            if GPT2Tokenizer:
                num_tokens = len(self.gpt2_tokenizer.encode(string))
            else:
                print("No token counter found, install tiktoken or GPT2Tokenizer to get correct token count.")
                num_tokens = len(string)

        # Calculate price
        price = round(num_tokens * price / 1000000, 4)

        if verbose:
            print("Estimated tokens:", num_tokens)
            print("Estimated price: $", price)
        
        return num_tokens, price
    
    def truncate_text_to_tokens(self, text, max_tokens, tokenizer_name="gpt2", current_conversation=""):
        """
        Truncate text to fit within the allowed number of tokens.

        Args:
            text (str): The input text to truncate.
            max_tokens (int): The maximum allowed number of tokens.
            tokenizer_name (str): The name of the tokenizer to use (default: "gpt2").

        Returns:
            str: The truncated text that fits within the token limit.
        """
        tokenizer_name = tokenizer_name or "gpt2"
        try:
            # Attempt to use tiktoken for tokenization
            tokenizer = tiktoken.encoding_for_model(tokenizer_name)
            # Tokenize the text
            tokens = tokenizer.encode(text)
            current_tokens = len(tokenizer.encode(current_conversation))
        except Exception:
            if verbose:
                print("tiktoken failed, falling back to GPT2Tokenizer.")
            # Load the tokenizer
            if GPT2Tokenizer:
                tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
                # Tokenize the text
                tokens = tokenizer.encode(text)
                current_tokens = len(tokenizer.encode(current_conversation))
            else:
                return text
            
        # Check if any space is left?
        max_remaining_tokens = max_tokens - current_tokens
        
        if max_remaining_tokens <= 0:
            return text

        # Truncate tokens to the allowed limit
        truncated_tokens = tokens[:max_remaining_tokens]

        try:
            # Decode the truncated tokens back into text
            truncated_text = tokenizer.decode(truncated_tokens)
        except Exception:
            # Decode the truncated tokens back into text
            truncated_text = tokenizer.decode(truncated_tokens, skip_special_tokens=True)

        return truncated_text

    def is_valid_json(self, json_string):
        try:
            json.loads(json_string)
        except ValueError:
            return False

        return True

    def is_valid_python(self, code):
        try:
            ast.parse(code)
        except SyntaxError:
            return False

        return True

    def is_valid_yaml(self, code):
        try:
            yaml.safe_load(code)
        except yaml.YAMLError:
            return False

        return True
    
    def clear_markdown(self, text):
        
        # Remove starting code markup
        if text.startswith('```python'):
            text = text.split('```python',1)[-1]
        elif text.startswith('```json'):
            text = text.split('```json',1)[-1]
        elif text.startswith('```yaml'):
            text = text.split('```yaml',1)[-1]
        elif text.startswith('```plaintext'):
            text = text.split('```plaintext',1)[-1]
        elif text.startswith('```javascript'):
            text = text.split('```javascript',1)[-1]
        elif text.startswith('```html'):
            text = text.split('```html',1)[-1]
        elif text.startswith('```css'):
            text = text.split('```css',1)[-1]
        elif text.startswith('```'):
            text = text.split('```',1)[-1]

        # Remove ending code markup
        if text.endswith('```'):
            text = text.rsplit('```',1)[0]

        return text

    def clean_text(self, text, remove_linebreaks = False):
        txt = text.encode('ascii', 'ignore').decode()
        txt = txt.replace('\\n',' ')
        if remove_linebreaks:
            txt = txt.replace('\n',' ')
        return txt.replace('\\u00a0',' ')

    def strip_tags(self, text, remove_linebreaks = False):
        strip_tags = StripTags()
        strip_tags.reset()
        strip_tags.feed(text)
        txt = strip_tags.get_data().encode('ascii', 'ignore').decode()
        txt = txt.replace('\\n',' ')
        if remove_linebreaks:
            txt = txt.replace('\n',' ')
        return txt.replace('\\u00a0',' ')
    
    def generate_short_uuid(self, length = 8):
        # Generate a UUID and return a shortened version (min. 2 characters)
        return 'z'+str(uuid.uuid4())[:max(1,length-1)]
    
    def generate_md5_hash(self, query):
        return hashlib.md5(str(query).encode('utf-8')).hexdigest()
    
    def safe_str_to_int(self, s):
        # Extract numeric part using regex
        match = re.search(r"[-+]?\d*\.?\d+", s)
        if match:
            return int(match.group())
        return 0  # Return 0 if no valid number is found


class StripTags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

class SafeMap(dict):
    def __missing__(self, key):
        return f'{{{key}}}'
