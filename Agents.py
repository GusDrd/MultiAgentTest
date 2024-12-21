
# Imports
from dotenv import load_dotenv
from openai import OpenAI
import os
import re



# Construct the path to the .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

# Find environment variables
load_dotenv(env_path)

# Load OpenAI API key
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))



# ------------------
# BASE AGENT Class   (Serves as a template for different agents)
# ------------------
class BaseAgent:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt  # System prompt to guide agent's behavior
        self.message_history = {}           # Message history per user for this agent (user can be AgentA/B when they communicate with eachother)

    def query_gpt(self, user_input, user):
        # Use OpenAI API to generate a response
        answer, user_message_history = generate_script_gpt(user_input, self.message_history, user, self.system_prompt)
        # Update the user's conversation history with the agent
        self.message_history[user] = user_message_history

        return answer

# ---------------
# AGENT_A Class   (Interacts with the user and can request information from AGENT_B)
# ---------------
class AgentA(BaseAgent):
    def __init__(self):
        super().__init__(
            """You are a friendly assistant with a bit of knowledge across various topics. You're goal is to answer simply and not go into too much detail about the subjects discussed.
You are not expected to have the specific answer to all questions.
If the subject matter becomes too complex or requires specific troubleshooting, you should analyse the message to find the most relevant issue from the following list of possible issues:

- Computer won't turn on
- No internet connection
- Computer running slow
- Unable to print
- Software application crashes frequently
- Audio not working
- Blue Screen of Death (BSOD) error
- USB device not recognized

Always print the most relevant issue exactly as shown in the list and in between double square brackets [[<issue>]].
For example, if the most relevant issue is No internet connection, you should print[[No internet connection]] at the end of your answer.
Only print the issue if the subject matter is part of the list of issues provided above."""
        )

    # Handle message received from users
    def handle(self, user_input, user):
        response = self.query_gpt(user_input, user)     # Process response through ChatGpt and update knowledge
        issue = re.findall(r'\[\[(.*?)\]\]', response)  # Look for a trigger request from Agent A in the format [[<issue>]]
        if issue:
            response = re.sub(r'\[\[.*?\]\]', '', response)  # Clear trigger request from response
            issue = issue[0]  # Retrieve issue
        return response, issue
    
    # Append message from Agent B to Agent A's knowledge
    def add_knowledge(self, message, user):
        self.message_history[user].append({"role": "assistant", "content": f"""{message}"""})  # Append new knowledge

# ---------
# AGENT_B   (Provides information to AGENT_A when triggered to)
# ---------
class AgentB(BaseAgent):
    def __init__(self):
        super().__init__(
            """You are a knowledgeable and friendly assistant who's role is to describe some steps that will be given to you.
You will always receive messages in the format: "Here are the troubleshooting steps: <steps>".
Nicely format the steps in order and present them to the user."""
        )

    # Handle request received from Agent A's trigger
    def handle(self, user_input, user):
        return self.query_gpt(user_input, user)


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

    # Used to clear entries. First entry (system prompt) should never be deleted.
    """
    if len(past_messages) > 4:
        past_messages = past_messages[:-4]
    """

    return final_response, past_messages