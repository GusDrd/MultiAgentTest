from streamlit_chat import message
from Agents import AgentA, AgentB
import streamlit as st
import random
import string
import json
import os


# Function to retrieve steps by issue
def get_troubleshooting_steps(issue):
    for scenario in st.session_state.troubleshooting.get("troubleshooting_scenarios", []):
        if issue.lower() in scenario["issue"].lower():
            return "\n".join(scenario["steps"])
    return None

# Function to start a new conversation
def start_new_conversation():
    # Increment conversation ID to maintain a unique integer ID
    conversation_id = len(st.session_state.conversations) + 1
    st.session_state.conversations[conversation_id] = {"user_id": generate_user_id(), "messages": []}
    st.session_state.current_conversation = conversation_id  # Switch to the new conversation

# Function to generate a random user ID
def generate_user_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

# Function to handle the user message and agent response
def handle_message():
    message_input = st.session_state.message_input
    if message_input:
        # Retrieve user_id of the ongoing conversation
        user = st.session_state.conversations[st.session_state.current_conversation]["user_id"]

        # Add the user's message to the current conversation
        st.session_state.conversations[st.session_state.current_conversation]["messages"].append({"user_id": user, "message": message_input})

        # Process the message using Agent A
        agent_A_response, issue = agent_A.handle(message_input, user)

        # Add Agent A's response to the current conversation
        st.session_state.conversations[st.session_state.current_conversation]["messages"].append({"user_id": "Agent A", "message": agent_A_response})

        # If Agent A issued a request, we consult Agent B to answer with the specific information fetched from the json file.
        if issue:
            # Retrieve steps for a given issue from the troubleshooting json
            steps = get_troubleshooting_steps(issue)
            # Request Agent B to handle the json data
            agent_B_response = agent_B.handle(f"Here are the troubleshooting steps for the '{issue}' issue:\n{steps}", "Agent A")
            # Add Agent B's response to Agent A's knowledge to make it aware of what was sent.
            agent_A.add_knowledge(agent_B_response, user)

            # Add Agent B's response to the current conversation
            st.session_state.conversations[st.session_state.current_conversation]["messages"].append({"user_id": "Agent B", "message": agent_B_response})

        # Clear the input field after sending
        st.session_state.message_input = ""



# Initialize agents in session state
if "agent_A" not in st.session_state:
    st.session_state.agent_A = AgentA()
if "agent_B" not in st.session_state:
    st.session_state.agent_B = AgentB()

# Initialize troubleshooting json in session state
if "troubleshooting" not in st.session_state:
    # Retrieve troubleshooting information from json
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_test_python.json')
    with open(json_path, 'r') as file:
        troubleshooting = json.load(file)
    st.session_state.troubleshooting = troubleshooting

# Initialize conversation storage in session state
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
    st.session_state.current_conversation = 1  # Use integer for conversation ID
    st.session_state.conversations[st.session_state.current_conversation] = {"user_id": generate_user_id(), "messages": []}



# Set up the page configuration & title
st.set_page_config(page_title="MultiAgent App", page_icon=":speech_balloon:", layout="wide")
st.title("MultiAgent Test")

# Access agents from session state
agent_A = st.session_state.agent_A
agent_B = st.session_state.agent_B

# Dropdown to select an existing conversation
conversation_id = st.selectbox(
    "Select a conversation",
    options=list(st.session_state.conversations.keys()),
    index=list(st.session_state.conversations.keys()).index(st.session_state.current_conversation),
)
# Update current conversation when dropdown selection changes
if conversation_id != st.session_state.current_conversation:
    st.session_state.current_conversation = conversation_id

# Button to start a new conversation
if st.button("Start New Conversation"):
    start_new_conversation()  # Create a new conversation
    st.success(f"Started a new conversation: {st.session_state.current_conversation}")


# CSS to fix the input box below the display area
st.markdown(
    """
    <style>
    .css-1d391kg {height: 100vh; display: flex; flex-direction: column; justify-content: flex-end;}
    .stTextInput>div>input {position: fixed; bottom: 0; width: 100%; left: 0; z-index: 10;}
    .stTextArea {height: calc(100vh - 90px); overflow-y: auto;}
    </style>
    """,
    unsafe_allow_html=True
)


# Display all messages in the current conversation
for msg in st.session_state.conversations[st.session_state.current_conversation]["messages"]:
    is_user_message = msg["user_id"] != "Agent A" and msg["user_id"] != "Agent B"
    message(msg["message"], key=f"{st.session_state.current_conversation}-{msg['user_id']}-{msg['message']}", is_user=is_user_message)


# Text input box for sending messages
st.text_input("Text Input", key="message_input", on_change=handle_message, placeholder="Type here and press Enter...", label_visibility='hidden')