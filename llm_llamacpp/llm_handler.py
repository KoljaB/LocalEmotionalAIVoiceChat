import json
import requests
import logging
from typing import Callable, Dict, Any
from transformers import GPT2Tokenizer
from lib.conversation import Conversation

class LLMHandler:
    def __init__(
            self,
            url: str = "http://localhost:8000/v1/completions",
            completion_params_file: str = "llm_llamacpp/completion_params.json",
            max_tokens: int = 1548):

        self.url = url
        self.payload = ""
        self.completion_params = self.load_completion_params(completion_params_file)
        self.max_tokens = max_tokens
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.conversation = Conversation(max_tokens)
        
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

    def create_prompt(self, system_prompt: str) -> str:
        self.conversation.truncate_history(system_prompt, self.count_tokens)
        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        for role, message in self.conversation.get_history():
            prompt += f"<|im_start|>{role}\n{message}<|im_end|>\n"
        prompt += "<|im_start|>assistant"
        return prompt

    def generate_response(
            self,
            system_prompt: str,
            on_token: Callable[[str], None] = None):

        payload = {
            "prompt": self.create_prompt(system_prompt),
            **self.completion_params
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
                        if decoded_line.startswith("data: "):
                            json_str = decoded_line[6:]
                            if json_str.strip() == "[DONE]":
                                break
                            try:
                                json_obj = json.loads(json_str)
                                token = json_obj['choices'][0]['text']
                                if on_token:
                                    on_token(token)
                            except json.JSONDecodeError:
                                self.logger.error(f"Error decoding JSON: {json_str}")
            else:
                self.logger.error(f"Error: {response.status_code}")
                self.logger.error(response.text)

    def write_payload(self, file_path: str = 'payload.txt', mode='w'):
        with open(file_path, mode) as f:
            f.write(self.payload)