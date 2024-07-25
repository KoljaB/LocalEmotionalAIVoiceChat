import json
import os
import time
from typing import Callable, Dict, Any, List
from openai import OpenAI
from lib.conversation import Conversation

class LLMHandler:
    def __init__(
            self,
            completion_params_file: str = "llm_openai/completion_params.json",
            max_tokens: int = 1548,
            log_stats: bool = False):

        self.completion_params = self.load_completion_params(completion_params_file)
        self.max_tokens = max_tokens
        self.conversation = Conversation(max_tokens)
        self.log_stats = log_stats
        
        # Initialize OpenAI client
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)

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

        start_time = time.time()
        collected_messages = []

        try:
            response = self.client.chat.completions.create(**payload)
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    token = chunk.choices[0].delta.content
                    collected_messages.append(token)
                    if on_token:
                        on_token(token)
                    
                    if self.log_stats:
                        chunk_time = time.time() - start_time
                        print(f"Token received {chunk_time:.2f} seconds after request: {token}")

            full_response = ''.join(collected_messages)
            self.add_assistant_text(full_response)

            if self.log_stats:
                total_time = time.time() - start_time
                print(f"Full response received {total_time:.2f} seconds after request")
                print(f"Full response: {full_response}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def write_payload(self, file_path: str = 'payload.txt', mode='w'):
        payload = {
            "model": self.completion_params["model"],
            "messages": self.create_messages("You are a helpful assistant."),
            "stream": True,
            **self.completion_params.get("parameters", {})
        }
        with open(file_path, mode) as f:
            json.dump(payload, f, indent=4)

            
# import json
# import os
# import openai
# from typing import Callable, Dict, Any, List
# from transformers import GPT2Tokenizer
# from lib.conversation import Conversation

# class LLMHandler:
#     def __init__(
#             self,
#             completion_params_file: str = "openai/completion_params.json",
#             max_tokens: int = 1548,
#             log_stats: bool = False):

#         self.completion_params = self.load_completion_params(completion_params_file)
#         self.max_tokens = max_tokens
#         self.conversation = Conversation(max_tokens)
#         self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
#         self.log_stats = log_stats
        
#         # Set up OpenAI API key
#         openai.api_key = os.getenv("OPENAI_API_KEY")
#         if not openai.api_key:
#             raise ValueError("OPENAI_API_KEY environment variable is not set")

#     def load_completion_params(self, file_path: str) -> Dict[str, Any]:
#         with open(file_path, 'r') as f:
#             return json.load(f)

#     def add_user_text(self, text: str):
#         self.conversation.add_user_message(text)

#     def add_assistant_text(self, text: str):
#         self.conversation.add_assistant_message(text)

#     def count_tokens(self, text: str) -> int:
#         return len(self.tokenizer.encode(text))

#     def create_messages(self, system_prompt: str) -> List[Dict[str, str]]:
#         self.conversation.truncate_history(system_prompt, self.count_tokens)
#         messages = [{"role": "system", "content": system_prompt}]
#         for role, message in self.conversation.get_history():
#             messages.append({"role": role, "content": message})
#         return messages

#     def generate_response(
#             self,
#             system_prompt: str,
#             on_token: Callable[[str], None] = None):

#         messages = self.create_messages(system_prompt)
        
#         payload = {
#             "model": self.completion_params["model"],
#             "messages": messages,
#             **self.completion_params.get("parameters", {})
#         }

#         try:
#             response = openai.ChatCompletion.create(**payload, stream=True)
            
#             full_response = ""
#             for chunk in response:
#                 if chunk['choices'][0]['finish_reason'] is not None:
#                     if self.log_stats:
#                         print(f"Generation complete. Finish reason: {chunk['choices'][0]['finish_reason']}")
#                     break
                
#                 token = chunk['choices'][0]['delta'].get('content', '')
#                 full_response += token
#                 if on_token:
#                     on_token(token)
            
#             self.add_assistant_text(full_response)
            
#         except Exception as e:
#             print(f"An error occurred: {e}")

#     def write_payload(self, file_path: str = 'payload.txt', mode='w'):
#         payload = {
#             "model": self.completion_params["model"],
#             "messages": self.create_messages("You are a helpful assistant."),
#             **self.completion_params.get("parameters", {})
#         }
#         with open(file_path, mode) as f:
#             json.dump(payload, f, indent=4)