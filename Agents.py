
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


"""
BASE AGENT Class which will serve as a base for different agents
"""
class BaseAgent:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt  # System prompt to guide agent's behavior
        self.message_history = {}           # Message history per user for this agent (user can be AgentA/B when they communicate with eachother)

    def query_gpt(self, user_input, user):
        # Use OpenAI API to generate a response
        answer, self.message_history = generate_script_gpt(user_input, self.message_history, user, self.system_prompt)
        return answer


"""
AGENT_A Class which interacts with the USER and AGENT_B when necessary
"""
class AgentA(BaseAgent):
    def __init__(self):
        super().__init__(
            """You are a friendly assistant with a bit of knowledge across various topics. You're goal is to answer simply and not go into too much detail about the subjects discussed.
You are not expected to have the specific answer to all questions.
If the subject matter becomes too complex or requires specific troubleshooting, you should analyse the message and print in your answer the most relevant topic from the following list of possible troubleshooting scenarios:

- Computer won't turn on
- No internet connection
- Computer running slow
- Unable to print
- Software application crashes frequently
- Audio not working
- Blue Screen of Death (BSOD) error
- USB device not recognized

Always print the most relevant troubleshooting scenario exactly as shown in the list and in between double square brackets.
For example, if you believe the most relevant issue is No internet connection, you should include [[No internet connection]] in your answer.
Your message MUST always contain the troubleshooting scenario as described above as [[<issue>]]."""
        )

    def handle(self, user_input, user):
        response = self.query_gpt(user_input, user)
        issue = re.findall(r'\[\[(.*?)\]\]', response)
        if issue:
            response = re.sub(r'\[\[.*?\]\]', '', response)
            issue = issue[0]
        return response, issue

"""
AGENT_B Class which interacts with AGENT_A
"""
class AgentB(BaseAgent):
    def __init__(self):
        super().__init__(
            """You are a knowledgeable and friendly assistant who's role is to describe some steps that will be given to you.
You will always receive messages in the format: "Here are the troubleshooting steps: <steps>".
Print exactly the steps you receive numbered and in order."""
        )

    def handle(self, user_input, user):
        return self.query_gpt(user_input, user)



"""
Script generation function to handle OpenAI interactions
"""
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