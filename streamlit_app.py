import streamlit as st
import requests
from openai import OpenAI

# 1) Session state for storing keys and chat messages
if "calendar_id" not in st.session_state:
    st.session_state["calendar_id"] = ""
if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""
if "start_chat" not in st.session_state:
    st.session_state["start_chat"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 2) Title and instructions
st.title("💬 AI Agent")

st.write(
    "This simple chatbot uses OpenAI's GPT-4o-mini model to generate responses. "
    "Please enter your GHL user ID and Calendar ID, then click the 'Start Chatting' button."
)

# 3) Let the user enter tokens
st.session_state["user_id"] = st.text_input(
    "GHL User ID", 
    type="password", 
    value=st.session_state["user_id"]
)

# 4) Let the user enter tokens
st.session_state["calendar_id"] = st.text_input(
    "GHL Calendar ID", 
    type="password", 
    value=st.session_state["calendar_id"]
)

# 5) Button to start chatting
if st.button("Start Chatting"):
    user_id = st.session_state["user_id"]
    calendar_id = st.session_state["calendar_id"]
    if not user_id or not calendar_id:
        st.warning("Please provide both your GHL User ID and GHL Calendar ID.")
    else:
        st.session_state["start_chat"] = True

        # Restart the chat session using the specified endpoint
        headers = {
            "Content-Type": "application/json",
        }
        restart_resp = requests.post(
            f"https://c1d8-111-88-84-231.ngrok-free.app/api/restart/?userId={user_id}",
            headers=headers,
        )
        if restart_resp.status_code == 200:
            st.success("Chat session restarted successfully.")
        else:
            st.error(f"Failed to restart chat session: {restart_resp.text}")

# Display previous messages from session state
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5) Chat interface
if st.session_state["start_chat"]:
    calendar_id = st.session_state["calendar_id"]
    user_id = st.session_state["user_id"]

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        message = {"role": "user", "content": prompt}
        st.session_state["messages"].append(message)
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

        # Call Django endpoint with JWT
        headers = {
            "Content-Type": "application/json",
        }
        resp = requests.post(
            f"https://c1d8-111-88-84-231.ngrok-free.app/api/calendars/{st.session_state['calendar_id']}/free-slots?userId={st.session_state['user_id']}&days=7&timeout=60",
            json={"message": prompt},
            headers=headers,
        )
        if resp.status_code == 200:
            django_data = resp.json()
            bot_message = django_data.get("response", "No response")
            print(django_data)
            message = {"role": "assistant", "content": bot_message}
            st.session_state["messages"].append({"role": "assistant", "content": bot_message})
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        else:
            bot_message = f"Error calling Django API: {resp.text}"
