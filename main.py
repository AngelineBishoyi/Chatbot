import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import os
import time

load_dotenv()

st.set_page_config(page_title="Chat with Gemini Pro",
                   page_icon=":brain:",
                   layout="wide",)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel("gemini-pro")


def translate_Streamlit(user_role):
    if user_role == "model":
        return "ai"
    else:
        return user_role


# Session Management
def start_new_chat():
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []
    new_session = model.start_chat(history=[])
    st.session_state.chat_sessions.append(new_session)
    return new_session


def show_past_conversation(session_id=None):
    if "chat_sessions" in st.session_state:
        if session_id is not None:
            # Show specific past conversation based on ID
            chat_session = st.session_state.chat_sessions[session_id]
            for message in chat_session.history:
                with st.chat_message(translate_Streamlit(message.role)):
                    st.markdown(message.parts[0].text)
        else:
            # No specific ID provided, list session titles for selection
            st.write("**Past Conversations**")
            for i, chat_session in enumerate(st.session_state.chat_sessions):
                st.write(f"- Session {i+1}")
    else:
        st.write("No past conversation available.")


# Main Area Content Management
def main_area():
    # Check if there are existing sessions
    if "chat_sessions" in st.session_state:
        current_session = st.session_state.chat_sessions[-1]

        # User Input and Chat Interaction
        user_prompt = st.chat_input("Ask me anything")
        if user_prompt:
            st.chat_message("users").markdown(user_prompt)
            with st.spinner("Thinking..."):
                gemini_response = current_session.send_message(user_prompt)
            with st.chat_message("ai"):
                st.markdown(gemini_response.text)
        else:
            # If no new input, check for past conversation selection
            if st.session_state.get("show_past_conversation") is not None:
                show_past_conversation(st.session_state["show_past_conversation"])
                del st.session_state["show_past_conversation"]  # Clear temporary state
            else:
                # No new input or past conversation selection, display nothing
                pass  # Intentionally left empty

    else:
        # No sessions, display message and start new chat button
        st.write("No past conversation available.")
        if st.button("Start New Chat"):
            start_new_chat()


# Sidebar - Settings and Past Conversation List
with st.sidebar:
    st.header("Settings")
    temperature = st.slider(
        "Temperature", min_value=0.00, max_value=1.00, step=0.1, value=0.5
    )
    top_p = st.slider("Top-p", min_value=0.1, max_value=1.0, step=0.1, value=0.5)
    top_k = st.slider("Top-k", min_value=1, max_value=100, step=1, value=50)

    if st.session_state.get("chat_sessions"):
        # Button to list past conversations
        if st.sidebar.button("Past Conversations"):
            # Clear main area and show past conversation list
            st.session_state["main_area_content"] = "past_conversations"

# Main Content Area
if "main_area_content" not in st.session_state:
    st.session_state["main_area_content"] = None

if st.session_state["main_area_content"] == "past_conversations":
   main_area()