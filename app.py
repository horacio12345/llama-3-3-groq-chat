import streamlit as st
from groq import Groq, Client
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
from datetime import datetime

# Cargar las variables de entorno desde .env
load_dotenv()

# Configurar la API key de Groq
api_key = os.environ.get("GROQ_API_KEY")

# Inicializar cliente Groq
if not api_key:
    st.error("🔑 API key no encontrada. Asegúrate de que 'GROQ_API_KEY' esté configurada correctamente.")
    st.stop()
else:
    client = Groq(api_key=api_key)

# Función para convertir mensajes de LangChain al formato requerido por Groq
def format_messages_for_groq(messages):
    formatted = []
    for msg in messages:
        if hasattr(msg, "content"):
            role = "user" if msg.type == "human" else "assistant"
            formatted.append({"role": role, "content": msg.content})
    return formatted

# Función para asignar título a la conversación
def assign_conversation_title(conversation):
    if conversation:
        first_user_message = next((msg["content"] for msg in conversation if msg["role"] == "user"), "Conversación sin título")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{first_user_message[:30]}... ({timestamp})"
    return "Conversación vacía"

# Inicializar variables de estado
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)
if 'saved_conversations' not in st.session_state:
    st.session_state.saved_conversations = []
if 'current_messages' not in st.session_state:
    st.session_state.current_messages = []

# Título principal de la aplicación
st.markdown("<h1>💬 <span style='background: linear-gradient(to right, #FF0000, #FF7F00, #FFFF00, #00FF00, #0000FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Llama 3.3-70b y Groq</span> ⚡</h1>", unsafe_allow_html=True)
st.markdown("---")

# Configuración de la barra lateral
with st.sidebar:
    st.title("🎯\u2004Opciones")
    
    if st.button("💾 \u2004Guardar conversación"):
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
            st.success("✅ ¡Conversación guardada!")
    
    # Mostrar conversaciones guardadas
    if st.session_state.saved_conversations:
        st.markdown("📚 ### Conversaciones guardadas:")
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

# Mostrar mensajes previos
for message in st.session_state.current_messages:
    with st.chat_message(message["role"]):
        icon = "👤" if message["role"] == "user" else "🤖"
        st.markdown(f"{icon} {message['content']}")

# Entrada de chat para el usuario
if user_input := st.chat_input("💭 Escribe tu mensaje aquí..."):
    # Añadir el mensaje del usuario al historial
    st.session_state.current_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"👤 {user_input}")

    # Añadir el mensaje del usuario a la memoria
    st.session_state.memory.chat_memory.add_user_message(user_input)

    try:
        # Extraer contexto desde la memoria
        raw_context = st.session_state.memory.chat_memory.messages
        context = format_messages_for_groq(raw_context)

        # Enviar contexto al cliente Groq
        chat_completion = client.chat.completions.create(
            messages=context,
            model="llama-3.3-70b-versatile",
            max_tokens=8000,
            temperature=0,
        )

        # Procesar la respuesta
        if chat_completion.choices:
            respuesta = chat_completion.choices[0].message.content

            # Añadir la respuesta al historial
            st.session_state.current_messages.append({"role": "assistant", "content": respuesta})
            with st.chat_message("assistant"):
                st.markdown(f"🤖 {respuesta}")

            # Añadir la respuesta a la memoria
            st.session_state.memory.chat_memory.add_ai_message(respuesta)
        else:
            st.warning("⚠️ El modelo no devolvió ninguna respuesta.")
    except Exception as e:
        st.error(f"❌ Se produjo un error: {e}")