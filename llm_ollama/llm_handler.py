import json
import requests
import logging
from typing import Callable, Dict, Any, List
from transformers import GPT2Tokenizer
from lib.conversation import Conversation

class LLMHandler:
    def __init__(
            self,
            url: str = "http://localhost:11434/api/chat",
            completion_params_file: str = "llm_ollama/completion_params.json",
            max_tokens: int = 1548,
            log_stats: bool = False):  # New parameter to control logging

        self.url = url
        self.completion_params = self.load_completion_params(completion_params_file)
        self.max_tokens = max_tokens
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.conversation = Conversation(max_tokens)
        self.log_stats = log_stats  # Store the logging preference
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def load_completion_params(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            return json.load(f)

    def add_user_text(self, text: str):
        self.conversation.add_user_message(text)

    def add_assistant_text(self, text: str):
        self.conversation.add_assistant_message(text)

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def create_messages(self, system_prompt: str) -> List[Dict[str, str]]:
        self.conversation.truncate_history(system_prompt, self.count_tokens)
        messages = [{"role": "system", "content": system_prompt}]
        for role, message in self.conversation.get_history():
            messages.append({"role": role, "content": message})
        return messages

    def generate_response(
            self,
            system_prompt: str,
            on_token: Callable[[str], None] = None):

        payload = {
            "model": self.completion_params["model"],
            "messages": self.create_messages(system_prompt),
            "stream": True,
            **self.completion_params.get("parameters", {})  # Unpack parameters at the top level
        }

        self.payload = json.dumps(payload, indent=4)

        headers = {
            "Content-Type": "application/json"
        }

        with requests.post(self.url, data=json.dumps(payload), headers=headers, stream=True) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        try:
                            json_obj = json.loads(decoded_line)
                            if 'message' in json_obj:
                                token = json_obj['message'].get('content', '')
                                if on_token:
                                    on_token(token)
                            if json_obj.get('done', False) and self.log_stats:  # Only log if log_stats is True
                                self.logger.info(f"Generation complete. Stats: {json_obj}")
                        except json.JSONDecodeError:
                            self.logger.error(f"Error decoding JSON: {decoded_line}")
            else:
                self.logger.error(f"Error: {response.status_code}")
                self.logger.error(response.text)

    def write_payload(self, file_path: str = 'payload.txt', mode='w'):
        with open(file_path, mode) as f:
            f.write(self.payload)

