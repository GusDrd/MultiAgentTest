from streamlit_chat import message
from Agents import AgentA, AgentB
import streamlit as st
import random
import string
import json
import os


# Function to generate a random user ID
def generate_user_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

# Set up the page configuration & title
st.set_page_config(page_title="MultiAgent App", page_icon=":speech_balloon:", layout="wide")
st.title("MultiAgent Test")

# Session state to store messages and user ID
if "user_id" not in st.session_state:
    st.session_state.user_id = generate_user_id()
    st.session_state.messages = []


# Function to reset the conversation and user ID
def reset_conversation():
    st.session_state.user_id = generate_user_id()
    st.session_state.messages = []

# Button to reset the conversation and user ID
st.button("Reset Conversation", on_click=reset_conversation)


# Retrieve troubleshooting information from json
json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_test_python.json')
with open(json_path, 'r') as file:
    troubleshooting = json.load(file)

# Function to retrieve steps by issue
def get_troubleshooting_steps(issue):
    for scenario in troubleshooting.get("troubleshooting_scenarios", []):
        if issue.lower() in scenario["issue"].lower():
            return "\n".join(scenario["steps"])
    return None


# Function to handle the user message and agent response
def handle_message():
    message_input = st.session_state.message_input
    if message_input:
        # Add the user's message to the session state
        st.session_state.messages.append({"user_id": st.session_state.user_id, "message": message_input})

        # Process the message using AgentA (simulated here)
        agent_A_response, issue = AgentA().handle(message_input, st.session_state.user_id)

        # Add AgentA's response to the conversation
        st.session_state.messages.append({"user_id": "Agent A", "message": agent_A_response})

        # If an issue is detected in Agent A's answer, we consult Agent B to answer with the specific information fetched from the json file.
        if issue:
            steps = get_troubleshooting_steps(issue)
            agent_B_response = AgentB().handle(f"Here are the troubleshooting steps: {steps}", "Agent A")

            # Add AgentA's response to the conversation
            st.session_state.messages.append({"user_id": "Agent B", "message": agent_B_response})

        # Clear the input field after sending
        st.session_state.message_input = ""


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


# Display all messages in the conversation
for msg in st.session_state.messages:
    is_user_message = msg["user_id"] != "Agent A" and msg["user_id"] != "Agent B"
    message(msg["message"], key=generate_user_id(), is_user=is_user_message)


# Text input box for sending messages
st.text_input("Text Input", key="message_input", on_change=handle_message, placeholder="Type here and press Enter...", label_visibility='hidden')
