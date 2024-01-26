import streamlit as st
import requests

# Function to simulate different styling for user and bot messages
def display_chat_message(user, message, is_typing=False):
    if is_typing:
        st.markdown(f"<div style='color: gray;'>{message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"**{user}**: {message}")

# Initialize session state for conversation history and typing status
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'typing' not in st.session_state:
    st.session_state.typing = False

# Set up the layout
st.title("Chat with Lucy")

# Conversation display area
with st.container():
    for user, message in st.session_state.conversation:
        display_chat_message(user, message)
    if st.session_state.typing:
        display_chat_message('', 'Lucy is typing...', is_typing=True)

# User input area
with st.container():
    user_input = st.text_input("Type your message:", key="user_input")
    send_button = st.button("Send")

# Backend API URL (adjust as needed)
API_URL = "http://localhost:5000/chat"

# Send message and display response
if send_button and user_input:
    # Update conversation with user's message and clear input
    st.session_state.conversation.append(("You", user_input))

    # Simulate typing indicator
    st.session_state.typing = True

    # Send the message to the backend and get the response
    response = requests.post(API_URL, json={"message": user_input})
    if response.status_code == 200:
        gpt4_response = response.json().get("message")
        st.session_state.conversation.append(("GPT-4", gpt4_response))
    else:
        st.session_state.conversation.append(("Error", "Failed to get response from the server."))
    
    # Hide typing indicator
    st.session_state.typing = False

    # Rerun the app to update the conversation display
    st.rerun()
