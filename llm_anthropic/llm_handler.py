import json
import os
import time
from typing import Callable, Dict, Any, List
from anthropic import Anthropic
from lib.conversation import Conversation

class LLMHandler:
    def __init__(
            self,
            completion_params_file: str = "llm_anthropic/completion_params.json",
            max_tokens: int = 1000,
            log_stats: bool = False):

        self.completion_params = self.load_completion_params(completion_params_file)
        self.max_tokens = max_tokens
        self.conversation = Conversation(max_tokens)
        self.log_stats = log_stats
        
        # Initialize Anthropic client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = Anthropic(api_key=api_key)

    def load_completion_params(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            return json.load(f)

    def add_user_text(self, text: str):
        self.conversation.add_user_message(text)

    def add_assistant_text(self, text: str):
        self.conversation.add_assistant_message(text)

    def create_messages(self, system_prompt: str) -> Dict[str, Any]:
        messages = []
        for role, message in self.conversation.get_history():
            if role != "system":
                messages.append({"role": role, "content": message})
        
        return {
            "system": system_prompt,
            "messages": messages
        }

    def generate_response(
            self,
            system_prompt: str,
            on_token: Callable[[str], None] = None):

        message_data = self.create_messages(system_prompt)
        
        payload = {
            "model": self.completion_params["model"],
            "max_tokens": self.max_tokens,
            **message_data,
            **self.completion_params.get("parameters", {})
        }

        start_time = time.time()
        collected_messages = []

        try:
            with self.client.messages.stream(**payload) as stream:
                for text in stream.text_stream:
                    collected_messages.append(text)
                    if on_token:
                        on_token(text)
                    
                    if self.log_stats:
                        chunk_time = time.time() - start_time
                        print(f"Token received {chunk_time:.2f} seconds after request: {text}")

            full_response = ''.join(collected_messages)
            self.add_assistant_text(full_response)

            if self.log_stats:
                total_time = time.time() - start_time
                print(f"Full response received {total_time:.2f} seconds after request")
                print(f"Full response: {full_response}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def write_payload(self, file_path: str = 'payload.txt', mode='w'):
        message_data = self.create_messages("You are a helpful assistant.")
        payload = {
            "model": self.completion_params["model"],
            "max_tokens": self.max_tokens,
            **message_data,
            **self.completion_params.get("parameters", {})
        }
        with open(file_path, mode) as f:
            json.dump(payload, f, indent=4)