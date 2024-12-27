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

#%pip install --upgrade tiktoken
import tiktoken

class Utils:
    def __init__(self):
        self.total_tokens_estimate = 0
        self.total_price_estimate = 0
        self.bot_logs = []
        
    def bot_log(self, bot, message):
        self.bot_logs.append((bot, message))

    def print_current_estimates(self):
        print('Estimated total tokens:', self.total_tokens_estimate)
        print('Estimated total price: $', self.total_price_estimate)

    def update_price_tokens_use_estimates(self, string, model = 'gpt-4-1106-preview', price = 0.150, verbose = False):
        tokens, price = self.price_tokens_from_string(string, model, price, verbose)
        self.total_tokens_estimate = self.total_tokens_estimate + tokens
        self.total_price_estimate = self.total_price_estimate + price
        if verbose:
            self.print_current_estimates()

    def price_tokens_from_string(self, string, encoding_name, price = 0.150, verbose = False):
        """Returns the number of tokens in a text string."""
        try:
            encoding = tiktoken.encoding_for_model(encoding_name)
        except:
            encoding = tiktoken.encoding_for_model('gpt-4-1106-preview')
        num_tokens = len(encoding.encode(string))
        price = round(num_tokens*price/1000000, 4)
        if verbose:
            print('Estimated tokens:', num_tokens)
            print('Estimated price: $', price)
        
        return num_tokens, price

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
            yaml.load(code)
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
