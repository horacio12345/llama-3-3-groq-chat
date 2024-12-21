import streamlit as st
from groq import Groq, Client
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Configure Groq API key
api_key = os.environ.get("GROQ_API_KEY")

# Initialize Groq client
if not api_key:
    st.error("🔑 API key not found. Make sure 'GROQ_API_KEY' is properly configured.")
    st.stop()
else:
    client = Groq(api_key=api_key)

# Function to convert LangChain messages to Groq format
def format_messages_for_groq(messages):
    formatted = []
    for msg in messages:
        if hasattr(msg, "content"):
            role = "user" if msg.type == "human" else "assistant"
            formatted.append({"role": role, "content": msg.content})
    return formatted

# Function to assign title to conversation
def assign_conversation_title(conversation):
    if conversation:
        first_user_message = next((msg["content"] for msg in conversation if msg["role"] == "user"), "Untitled Conversation")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{first_user_message[:30]}... ({timestamp})"
    return "Empty Conversation"

# Initialize state variables
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)
if 'saved_conversations' not in st.session_state:
    st.session_state.saved_conversations = []
if 'current_messages' not in st.session_state:
    st.session_state.current_messages = []

# Main application title
st.markdown("<h1>💬 <span style='background: linear-gradient(to right, #FF0000, #FF7F00, #FFFF00, #00FF00, #0000FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Llama 3.3-70b and Groq</span> ⚡</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.title("🎯\u2004Options")
    
    if st.button("💾 \u2004Save conversation"):
        if st.session_state.current_messages:
            title = assign_conversation_title(st.session_state.current_messages)
            
            for idx, conv in enumerate(st.session_state.saved_conversations):
                if conv['title'].split('...')[0] == title.split('...')[0]:
                    st.session_state.saved_conversations.pop(idx)
                    break
            
            st.session_state.saved_conversations.append({
                "title": title, 
                "messages": st.session_state.current_messages.copy()
            })
            
            st.session_state.current_messages = []
            st.session_state.memory = ConversationBufferMemory(return_messages=True)
            st.success("✅ Conversation saved!")
    
    # Display saved conversations
    if st.session_state.saved_conversations:
        st.markdown("📚 ### Saved Conversations:")
        for idx, conv in enumerate(st.session_state.saved_conversations):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📜 {conv['title']}", key=f"restore_{idx}"):
                    st.session_state.current_messages = conv["messages"].copy()
                    st.session_state.memory = ConversationBufferMemory(return_messages=True)
                    for msg in conv["messages"]:
                        if msg["role"] == "user":
                            st.session_state.memory.chat_memory.add_user_message(msg["content"])
                        else:
                            st.session_state.memory.chat_memory.add_ai_message(msg["content"])
            with col2:
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.session_state.saved_conversations.pop(idx)
                    st.rerun()

# Display previous messages
for message in st.session_state.current_messages:
    with st.chat_message(message["role"]):
        icon = "👤" if message["role"] == "user" else "🤖"
        st.markdown(f"{icon} {message['content']}")

# Chat input for user
if user_input := st.chat_input("💭 Write your message here..."):
    # Add user message to history
    st.session_state.current_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"👤 {user_input}")

    # Add user message to memory
    st.session_state.memory.chat_memory.add_user_message(user_input)

    try:
        # Extract context from memory
        raw_context = st.session_state.memory.chat_memory.messages
        context = format_messages_for_groq(raw_context)

        # Send context to Groq client
        chat_completion = client.chat.completions.create(
            messages=context,
            model="llama-3.3-70b-versatile",
            max_tokens=8000,
            temperature=0,
        )

        # Process response
        if chat_completion.choices:
            response = chat_completion.choices[0].message.content

            # Add response to history
            st.session_state.current_messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(f"🤖 {response}")

            # Add response to memory
            st.session_state.memory.chat_memory.add_ai_message(response)
        else:
            st.warning("⚠️ The model didn't return any response.")
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
