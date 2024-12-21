# MultiAgent Test

[![](https://img.shields.io/badge/-Python%203.11-ffd343?logo=python)](https://www.python.org/)
[![](https://img.shields.io/badge/-Streamlit%201.41-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![](https://img.shields.io/badge/-ChatGPT%20-74aa9c?logo=openai&logoColor=white)](https://chatgpt.com/)

This project explores the use of OpenAI's API to create 2 agents and make them communicate to answer complex queries.

> Time taken for the base implementation (agents, streamlit): **1h45**.  
> Time taken for optional changes (messages history, QoL changes, debug): **~2h**


## Setup

To setup the project, navigate to the project's directory and run the following command to install the necessary dependencies to run the project.  
``pip install --upgrade -r requirements.txt``


You should also make sure that a correct ``OPENAI_API_KEY`` key is provided in the ``.env`` environment file.


## Run the app
To run the project, navigate to the project's directory and run the following command:  
``streamlit run main.py``


## Implementation

**Agent A** is the base conversational agent which interacts directly with the user. If a subject from the json file is addressed and requires troubleshooting, **Agent A** can trigger a request for **Agent B** by providing the issue presented as ``[[<ISSUE>]]`` inside the message.

This issue tag will trigger a message to be sent to **Agent B** requesting to format the information from the json file. This information is then transmitted to the user and **Agent A** is made aware of **Agent B**'s answer so that it isn't lost if prompted about it.

### Further Improvements

Further features could include additional tags such as ``[[FOLLOW_UP]]`` so that **Agent B** provides additional information to **Agent A**. This would make **Agent B** more useful since its only role is to treat information from the json file. Although I haven't implemented this, I prompted **Agent B** to provide a small justification sentence and debated whether to only pass this information to **Agent A** and not the user.

A **Mediator Agent** could also be implemented to orchestrate the information transmission between **Agent A** and **Agent B**, only sharing information with one or the other if it deems it necessary.

And for the most obvious improvement, better and more carefully crafted system prompts will always help make the conversation flow smoother between both agents and the user.
