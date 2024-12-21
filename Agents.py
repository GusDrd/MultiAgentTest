from ChatUtils import generate_script_gpt
import re


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
            """You are a friendly assistant with a bit of knowledge across various topics. You're goal is provide simple answer and to never go into too much detail about the subjects discussed.
You are not expected to have the specific answer to all questions.
Keep your answers short.

If the subject matter is too complex or requires troubleshooting, you should analyse the message to see if fits an issue from the following list of issues:

- Computer won't turn on
- No internet connection
- Computer running slow
- Unable to print
- Software application crashes frequently
- Audio not working
- Blue Screen of Death (BSOD) error
- USB device not recognized

If the message is specifically linked to one of these issues, you should print it in between double square brackets at the end of your message like this: [[<issue>]].
For example, if the message explicitly contains the keywords "no internet connection", you should print [[No internet connection]] at the end of your answer.
If the user mentions an issue that is not close enough to the listed ones, you should never include the tag.
Be aware of mixed keywords. For example, if the message contains "slow connection", this isn't linked to any issue although it contains "slow" and "connection".
This [[<issue>]] tag is not meant for the user and will be removed from the answer so simply add it at the end of your sentence and don't mention it.
This tag will trigger another agent to answer with specific troubleshooting steps to which you will have access."""
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
You will always receive messages in the format: "Here are the troubleshooting steps for the <issue> issue: <steps>".
Simply present the steps to the user as: "Troubleshooting steps: <steps>"
If you think that this will benefit the user at all, include a very small technical explanation after the steps."""
        )

    # Handle request received from Agent A's trigger
    def handle(self, user_input, user):
        return self.query_gpt(user_input, user)