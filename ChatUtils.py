from dotenv import load_dotenv
from openai import OpenAI
import os


# Construct the path to the .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

# Find environment variables
load_dotenv(env_path)

# Load OpenAI API key
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# -----------------------------------
# OpenAI Script Generation Function
# -----------------------------------
def generate_script_gpt(message, 
                        message_history, 
                        user, 
                        system_prompt):
    """
    Args:
        message (string): Message sent to OpenAI for processing.
        message_history (list): List of messages an agent has with different users.
        user (string): User who sent the message and waits for a response.
        system_prompt (string): The system prompt to condition the agent. Used only once at the start of each conversation.

    Returns:
        final_response (string): The agent's response to the user message based on the given message_history.
        past_messages (list): Updated list of messages the agent has with the given user.
    """
    past_messages = []

    # If user had a conversation, get back this history
    if user in message_history:
        past_messages = message_history[user]

    # Check for first message of the conversation
    if len(past_messages) == 0:

        # Setup system prompt to condition model for new conversation
        past_messages = [
            {
                "role": "system",
                "content": f"""{system_prompt}"""
            },
            {
                "role": "user",
                "content": f"""{message}"""
            }]
    else:
        # Continue the conversation
        past_messages.append(
            {
                "role": "user",
                "content": f"""{message}"""
            })

    # Generate the model's response
    response = openai_client.chat.completions.create(model = "gpt-4o-mini",
                                              max_tokens = 500,
                                              temperature = 1,
                                              messages = past_messages)

    # Prepare response to add it to list of previous entries
    final_response = response.choices[0].message.content
    past_messages.append({"role": "assistant", "content": f"""{final_response}"""})

    return final_response, past_messages