import logging
from typing import List, Tuple

class Conversation:
    def __init__(self, max_tokens: int = 1548, debug = False):
        self.debug = debug
        self.history: List[Tuple[str, str]] = []
        self.max_tokens = max_tokens

    def add_user_message(self, text: str):
        self.history.append(("user", text))

    def add_assistant_message(self, text: str):
        self.history.append(("assistant", text))

    def get_history(self) -> List[Tuple[str, str]]:
        return self.history

    def clear_history(self):
        self.history.clear()

    def truncate_history(self, system_prompt: str, count_tokens_func):
        system_tokens = count_tokens_func(system_prompt)
        total_tokens = system_tokens
        truncated_history = []

        for role, message in reversed(self.history):
            message_tokens = count_tokens_func(message)
            if total_tokens + message_tokens <= self.max_tokens:
                truncated_history.insert(0, (role, message))
                total_tokens += message_tokens
            else:
                break

        removed_messages = len(self.history) - len(truncated_history)
        self.history = truncated_history

        # Log token usage information
        history_tokens = total_tokens - system_tokens
        fill_percentage = (total_tokens / self.max_tokens) * 100

        if self.debug:
            print(f"Token usage: {total_tokens}/{self.max_tokens} ({fill_percentage:.2f}%)")
            print(f"System prompt tokens: {system_tokens}")
            print(f"History tokens: {history_tokens}")
            print(f"Remaining tokens for response: {self.max_tokens - total_tokens}")

            if removed_messages > 0:
                print(f"History truncated. {removed_messages} messages removed.")

        return total_tokens