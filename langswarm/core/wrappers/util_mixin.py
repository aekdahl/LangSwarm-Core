import re
from ..utils.utilities import Utils

class UtilMixin:
    def __init__(self):
        self.utils = Utils()
        
        # Precompiled regex patterns for efficiency
        self.INVALID_REQUEST_PATTERN = re.compile(r"request:([^\s|]+)\|.+\|")
        
    @property
    def MODEL_REGISTRY(self):
        return {
            "gpt-4o": {"limit": 128000, "ppm": 0},
            "gpt-4o-2024-08-06": {"limit": 128000, "ppm": 0},
            "chatgpt-4o-latest": {"limit": 128000, "ppm": 0},
            "gpt-4o-mini": {"limit": 128000, "ppm": 0},
            "gpt-4o-mini-2024-07-18": {"limit": 128000, "ppm": 0},
            "o1": {"limit": 200000, "ppm": 0},
            "o1-2024-12-17": {"limit": 200000, "ppm": 0},
            "o1-mini": {"limit": 128000, "ppm": 0},
            "o1-mini-2024-09-12": {"limit": 128000, "ppm": 0},
            "o1-preview": {"limit": 128000, "ppm": 0},
            "o1-preview-2024-09-12": {"limit": 128000, "ppm": 0},
            "gpt-4o-realtime-preview": {"limit": 128000, "ppm": 0},
            "gpt-4o-realtime-preview-2024-12-17": {"limit": 128000, "ppm": 0},
            "gpt-4o-mini-realtime-preview": {"limit": 128000, "ppm": 0},
            "gpt-4o-mini-realtime-preview-2024-12-17": {"limit": 128000, "ppm": 0},
            "gpt-4o-audio-preview": {"limit": 128000, "ppm": 0},
            "gpt-4o-audio-preview-2024-12-17": {"limit": 128000, "ppm": 0},
            "gpt-4-turbo": {"limit": 128000, "ppm": 0},
            "gpt-4-turbo-2024-04-09": {"limit": 128000, "ppm": 0},
            "gpt-4-turbo-preview": {"limit": 128000, "ppm": 0},
            "gpt-4-0125-preview": {"limit": 128000, "ppm": 0},
            "gpt-4-1106-preview": {"limit": 128000, "ppm": 0},
            "gpt-4": {"limit": 8192, "ppm": 0},
            "gpt-4-0613": {"limit": 8192, "ppm": 0},
            "gpt-4-0314": {"limit": 8192, "ppm": 0},
            "gpt-3.5-turbo-0125": {"limit": 16385, "ppm": 0},
            "gpt-3.5-turbo": {"limit": 16385, "ppm": 0},
            "gpt-3.5-turbo-1106": {"limit": 16385, "ppm": 0},
            "gpt-3.5-turbo-instruct": {"limit": 16385, "ppm": 0},
            "babbage-002": {"limit": 16384, "ppm": 0},
            "davinci-002": {"limit": 16384, "ppm": 0},
            "claude-3-5-sonnet-20241022": {"limit": 200000, "ppm": 3},
            "claude-3-5-sonnet-latest": {"limit": 200000, "ppm": 3},
            "anthropic.claude-3-5-sonnet-20241022-v2:0": {"limit": 200000, "ppm": 3},
            "claude-3-5-sonnet-v2@20241022": {"limit": 200000, "ppm": 3},
            "claude-3-5-haiku-20241022": {"limit": 200000, "ppm": 0.8},
            "claude-3-5-haiku-latest": {"limit": 200000, "ppm": 0.8},
            "anthropic.claude-3-5-haiku-20241022-v1:0": {"limit": 200000, "ppm": 0.8},
            "claude-3-5-haiku@20241022": {"limit": 200000, "ppm": 0.8},
            "claude-3-opus-20240229": {"limit": 200000, "ppm": 15},
            "claude-3-opus-latest": {"limit": 200000, "ppm": 15},
            "anthropic.claude-3-opus-20240229-v1:0": {"limit": 200000, "ppm": 15},
            "claude-3-opus@20240229": {"limit": 200000, "ppm": 15},
            "claude-3-sonnet-20240229": {"limit": 200000, "ppm": 3},
            "anthropic.claude-3-sonnet-20240229-v1:0": {"limit": 200000, "ppm": 3},
            "claude-3-sonnet@20240229": {"limit": 200000, "ppm": 3},
            "claude-3-haiku-20240307": {"limit": 200000, "ppm": 0.25},
            "anthropic.claude-3-haiku-20240307-v1:0": {"limit": 200000, "ppm": 0.25},
            "claude-3-haiku@20240307": {"limit": 200000, "ppm": 0.25},
            "gemini-1.5-flash": {"limit": 1000000, "ppm": 0.15},
            "gemini-1.5-flash-8b": {"limit": 1000000, "ppm": 0.075},
            "gemini-1.5-pro": {"limit": 2000000, "ppm": 2.5},
            "gemini-1.0-pro": {"limit": 120000, "ppm": 0.5},
            "mistral-large-latest": {"limit": 128000, "ppm": 2},
            "pixtral-large-latest": {"limit": 128000, "ppm": 2},
            "mistral-small-latest": {"limit": 32000, "ppm": 0.2},
            "codestral-latest": {"limit": 32000, "ppm": 0.3},
            "ministral-8b-latest": {"limit": 128000, "ppm": 0.1},
            "ministral-3b-latest": {"limit": 128000, "ppm": 0.04},
            "command-r": {"limit": 128000, "ppm": 0.15},
            "command-r-08-2024": {"limit": 128000, "ppm": 0.15},
            "command-r-03-2024": {"limit": 128000, "ppm": 0.15},
            "command-r7b": {"limit": 128000, "ppm": 0.0375},
            "command-r7b-12-2024": {"limit": 128000, "ppm": 0.0375},
            "command-r-plus": {"limit": 128000, "ppm": 2.5},
            "command-r-plus-08-2024": {"limit": 128000, "ppm": 2.5},
            "command-r-plus-04-2024": {"limit": 128000, "ppm": 2.5},
            "llama-3.3": {"limit": 128000, "ppm": 0},
            "llama-3.2": {"limit": 128000, "ppm": 0},
            "llama-3.1": {"limit": 128000, "ppm": 0},
            "llama-3": {"limit": 8000, "ppm": 0},
            "llama-2": {"limit": 4000, "ppm": 0},
            "Llama": {"limit": 128000, "ppm": 0},
            "biogpt": {"limit": 200000, "ppm": 0},
            "microsoft/biogpt": {"limit": 200000, "ppm": 0},
            "grok-beta": {"limit": 128000, "ppm": 2},
            "grok-2": {"limit": 128000, "ppm": 2},
            "grok-2-latest": {"limit": 128000, "ppm": 2},
            "grok-2-1212": {"limit": 128000, "ppm": 2},
            "grok-2-vision-1212": {"limit": 128000, "ppm": 10},
        }

    
    def _get_model_details(self, model, default=16000):
        return {"name": model, **self.MODEL_REGISTRY.get(str(model), {"limit": default, "ppm": 0})}

    def _is_valid_request_calls_in_text(self, text: str) -> bool:
        """
        Determines if all 'request:' calls in `text` are valid given the rules:

        1) If there's no 'request:' substring at all, it's valid (no calls).
        2) If we see `request:someword`, and 'someword' is not in (tools|rags|retrievers|plugins),
           then it's valid only if there are 0 pipes in that snippet.
        3) If we see `request:(tools|rags|retrievers|plugins)`, 
           it must have exactly one pipe in that snippet, 
           and the substring after that pipe can contain spaces or any text. 
           If 0 or 2+ pipes => invalid.

        Returns True if all calls are valid or if none exist, otherwise False.
        """

        # 1) Find each snippet that starts with 'request:' 
        pattern = re.compile(r"(request:[^\n]+?)(?=\s*request:|\Z)", re.IGNORECASE | re.DOTALL)
        snippets = pattern.findall(text)
        if not snippets:
            # No 'request:' => valid
            return True

        # 2) Validate each snippet
        for snippet in snippets:
            if not self._validate_single_request_snippet(snippet.strip()):
                return False

        return True

    def _validate_single_request_snippet(self, snippet: str) -> bool:
        """
        Validates a single substring that starts with 'request:' based on the rules:

        - If snippet doesn't match "request:something", we consider it not a real request => valid.
        - Otherwise parse the word after 'request:'.
          * If that word is not in (tools|rags|retrievers|plugins) => must have 0 pipes => valid, else invalid.
          * If that word is in (tools|rags|retrievers|plugins) => must have exactly 1 pipe => valid, else invalid.
        """

        # Quick prefix check
        if not snippet.lower().startswith("request:"):
            return True  # Not a 'request:' snippet => valid

        # Extract the word after 'request:' (up to space/pipe)
        match_prefix = re.match(r"^request:([^\s|]+)", snippet, re.IGNORECASE)
        if not match_prefix:
            # e.g. "request: " with a space => handle if there's a pipe => invalid, else => valid
            return not ("|" in snippet)

        found_word = match_prefix.group(1)  # e.g. 'tools', 'myword', etc.
        valid_keywords = {"tools", "rags", "retrievers", "plugins"}

        # Count total pipes in snippet
        pipe_count = snippet.count("|")

        if found_word.lower() not in valid_keywords:
            # Then must have 0 pipes
            return (pipe_count == 0)
        else:
            # found_word is in (tools|rags|retrievers|plugins)
            # must have exactly 1 pipe
            return (pipe_count == 1)


    def _is_valid_use_calls_in_text(self, text: str) -> bool:
        """
        Checks whether any 'use (tool|rag|retriever|plugin):...' calls in `text`
        are correctly formatted. If a snippet has "use tool:" (or rag/retriever/plugin)
        with fewer than 2 pipes, we decide:
            - 0 pipes => non-call => valid
            - 1 pipe => partial call => invalid
            - 2+ pipes => must strictly match a valid pattern

        Returns True if all calls are valid (or no calls exist), otherwise False.
        """

        # Regex to find each snippet starting with 'use tool|rag|retriever|plugin:'
        pattern = re.compile(
            r"(use\s+(?:tool|rag|retriever|plugin):[^\n]+?)(?=\s*use\s+(?:tool|rag|retriever|plugin)|$)",
            re.IGNORECASE | re.DOTALL
        )

        # Extract all occurrences
        matches = pattern.findall(text)
        if not matches:
            # No 'use' calls => valid
            return True

        for snippet in matches:
            if not self._validate_single_use_call(snippet.strip()):
                return False

        return True

    def _validate_single_use_call(self, use_call: str) -> bool:
        """
        Validates one snippet that starts with "use (tool|rag|retriever|plugin):".

        - 0 pipes => treat as non-call => valid
        - 1 pipe => partial call => invalid
        - 2+ pipes => must match the final pattern:
             use (tool|rag|retriever|plugin):<one_word>|<one_word>|<anything>

        Returns True if valid or no actual call, otherwise False.
        """

        prefix_pattern = re.compile(r"^use\s+(tool|rag|retriever|plugin):", re.IGNORECASE)
        prefix_match = prefix_pattern.match(use_call)
        if not prefix_match:
            # Not even starting with 'use tool|rag...', so treat as valid
            return True

        # Count how many '|' are present
        pipe_count = use_call.count('|')

        if pipe_count == 0:
            # "use tool: My favorite one" => no calls => valid
            return True
        elif pipe_count == 1:
            # "use tool:my_favorite_one|" => partial call => invalid
            return False
        else:
            # 2 or more pipes => parse strictly with a final pattern
            valid_pattern = re.compile(
                r"^use\s+(?:tool|rag|retriever|plugin):" 
                r"([A-Za-z0-9_\-]+)\|" 
                r"([A-Za-z0-9_\-]+)\|"  # second word
                r"(.*)$",
                re.IGNORECASE
            )
            return bool(valid_pattern.match(use_call))
