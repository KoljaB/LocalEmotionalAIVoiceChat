import sys
import os

# Add the parent directory to the Python path to import the LLMHandler
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from llm_handler import LLMHandler

def main():
    # Initialize the LLMHandler with log_stats set to False
    handler = LLMHandler(log_stats=False, completion_params_file="completion_params.json")

    # Define a system prompt
    system_prompt = "You are a helpful assistant."

    # Define a user message
    user_message = "Tell me a short joke about programming."

    # Add the user message to the conversation
    handler.add_user_text(user_message)

    print("Sending message to Ollama. Please wait...")

    # Function to handle incoming tokens
    def on_token(token):
        print(token, end='', flush=True)

    # Generate a response
    handler.generate_response(system_prompt, on_token=on_token)

    print("\n\nResponse complete.")

if __name__ == "__main__":
    main()
# import sys
# import os

# # Add the parent directory to the Python path to import the LLMHandler
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.append(parent_dir)

# from llm_handler import LLMHandler

# def main():
#     # Initialize the LLMHandler
#     handler = LLMHandler(completion_params_file="completion_params.json")

#     # Define a system prompt
#     system_prompt = "You are a helpful assistant."

#     # Define a user message
#     user_message = "Tell me a short joke about programming."

#     # Add the user message to the conversation
#     handler.add_user_text(user_message)

#     print("Sending message to Ollama. Please wait...")

#     # Function to handle incoming tokens
#     def on_token(token):
#         print(token, end='', flush=True)

#     # Generate a response
#     handler.generate_response(system_prompt, on_token=on_token)

#     print("\n\nResponse complete.")

# if __name__ == "__main__":
#     main()