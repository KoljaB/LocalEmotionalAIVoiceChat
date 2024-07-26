import json
import os
import time
import requests
from typing import Callable, Dict, Any, List
from lib.conversation import Conversation

class LLMHandler:
    def __init__(
            self,
            completion_params_file: str = "llm_lmstudio/completion_params.json",
            max_tokens: int = 1000,
            log_stats: bool = False):

        self.completion_params = self.load_completion_params(completion_params_file)
        self.max_tokens = max_tokens
        self.conversation = Conversation(max_tokens)
        self.log_stats = log_stats
        
        # LMStudio typically runs on localhost:1234
        self.api_url = "http://localhost:1234/v1/chat/completions"

    def load_completion_params(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            return json.load(f)

    def add_user_text(self, text: str):
        self.conversation.add_user_message(text)

    def add_assistant_text(self, text: str):
        self.conversation.add_assistant_message(text)

    def create_messages(self, system_prompt: str) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": system_prompt}]
        for role, message in self.conversation.get_history():
            messages.append({"role": role, "content": message})
        return messages

    def generate_response(
            self,
            system_prompt: str,
            on_token: Callable[[str], None] = None):

        messages = self.create_messages(system_prompt)
        
        payload = {
            "model": self.completion_params["model"],
            "messages": messages,
            "stream": True,
            **self.completion_params.get("parameters", {})
        }

        self.payload = json.dumps(payload, indent=4)

        start_time = time.time()
        collected_messages = []

        try:
            response = requests.post(self.api_url, json=payload, stream=True)
            # response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if data['choices'][0]['finish_reason'] is not None:
                            break
                        token = data['choices'][0]['delta'].get('content', '')
                        collected_messages.append(token)
                        if on_token:
                            on_token(token)
                        
                        if self.log_stats:
                            chunk_time = time.time() - start_time
                            print(f"Token received {chunk_time:.2f} seconds after request: {token}")

            full_response = ''.join(collected_messages)

            if self.log_stats:
                total_time = time.time() - start_time
                print(f"Full response received {total_time:.2f} seconds after request")
                print(f"Full response: {full_response}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def write_payload(self, file_path: str = 'payload.txt', mode='w'):
        with open(file_path, mode) as f:
            f.write(self.payload)