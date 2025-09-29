import streamlit as st
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

# -------------------------------------------------
# Initialize Azure Project Client
# -------------------------------------------------
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://sonif-mfxo70jw-eastus2.services.ai.azure.com/api/projects/sonif-mfxo70jw-eastus2_project"
)

# Load your agent
agent = project.agents.get_agent("asst_zYW7RJi5uHkcItLcH4a96eBy")

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(page_title="SonifAI Chat", page_icon="🤖", layout="wide")

# -------------------------------------------------
# CSS Styling: Glass Bubbles + Animation + Hover Glow
# -------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');

        /* App background: black gradient */
        .stApp {
            background: linear-gradient(135deg, #000000, #0a0a0a);
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Logo at top */
        .logo {
            font-family: 'Roboto Mono', monospace;
            font-size: 3rem;
            font-weight: bold;
            color: #ff4081;
            text-align: center;
            padding: 20px 0;
            letter-spacing: 2px;
            text-shadow: 0px 0px 10px #ff4081;
        }

        /* Chat bubbles - glass effect + animation */
        .chat-bubble {
            padding: 12px 18px;
            border-radius: 20px;
            margin: 8px 0;
            display: inline-block;
            max-width: 70%;
            line-height: 1.5;
            word-wrap: break-word;
            font-size: 1rem;
            backdrop-filter: blur(6px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            opacity: 0;
            transform: translateY(20px);
            animation: fadeIn 0.5s forwards;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .chat-bubble:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.6);
        }

        .user-bubble {
            background: rgba(25, 118, 210, 0.7);
            color: #fff;
        }
        .assistant-bubble {
            background: rgba(66, 66, 66, 0.7);
            color: #e0f7fa;
        }

        @keyframes fadeIn {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Sidebar */
        .sidebar .sidebar-content {
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        .sidebar .sidebar-content button {
            background-color: #333 !important;
            color: #00bcd4 !important;
            margin-bottom: 5px;
        }

        /* Divider between new chat and history */
        .sidebar-divider {
            height: 2px;
            background-color: #555;
            margin: 10px 0;
        }

        /* History header */
        .history-header {
            font-size: 1.1rem;
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 5px;
            color: #00bcd4;
        }

        /* Chat input area */
        .chat-input {
            background-color: #1f1f1f;
            color: #e0e0e0;
            padding: 12px;
            border-radius: 12px;
            margin-top: 10px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Logo at top
# -------------------------------------------------
st.markdown("<div class='logo'>🤖 SonifAI</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Sidebar: New Chat + History
# -------------------------------------------------
st.sidebar.title("📂 Chat Menu")

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# New chat button
if st.sidebar.button("➕ New Chat"):
    thread = project.agents.threads.create()
    chat_id = f"chat_{len(st.session_state.chat_sessions) + 1}"
    st.session_state.chat_sessions[chat_id] = {
        "thread_id": thread.id,
        "messages": [],
        "title": "New Chat"
    }
    st.session_state.current_chat = chat_id

# Divider
st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

# History header
st.sidebar.markdown("<div class='history-header'>🕒 Chat History</div>", unsafe_allow_html=True)

# Show chat history
if st.session_state.chat_sessions:
    for chat_id, chat_data in st.session_state.chat_sessions.items():
        display_name = chat_data.get("title", chat_id)
        if st.sidebar.button(f"💬 {display_name}", key=chat_id):
            st.session_state.current_chat = chat_id

# If no chat selected, create one
if not st.session_state.current_chat:
    thread = project.agents.threads.create()
    st.session_state.current_chat = "chat_1"
    st.session_state.chat_sessions["chat_1"] = {
        "thread_id": thread.id,
        "messages": [],
        "title": "New Chat"
    }

current_chat = st.session_state.chat_sessions[st.session_state.current_chat]

# -------------------------------------------------
# Add initial greeting if chat is empty
# -------------------------------------------------
if len(current_chat["messages"]) == 0:
    greeting = "Hello! I am SonifAI 🤖. How can I help you today?"
    current_chat["messages"].append({"role": "assistant", "content": greeting})

# -------------------------------------------------
# Chat Display: Left-right alignment with animation
# -------------------------------------------------
for msg in current_chat["messages"]:
    if msg["role"] == "user":
        st.markdown(f"""
            <div style="display:flex; justify-content:flex-end;">
                <div class='chat-bubble user-bubble'>{msg['content']}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="display:flex; justify-content:flex-start;">
                <div class='chat-bubble assistant-bubble'>{msg['content']}</div>
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------
# Chat Input
# -------------------------------------------------
if prompt := st.chat_input("Type your message..."):
    # Update chat title to first message
    if not current_chat["messages"]:
        current_chat["title"] = prompt[:20] + "..." if len(prompt) > 20 else prompt

    # Add user message
    current_chat["messages"].append({"role": "user", "content": prompt})
    st.markdown(f"""
        <div style="display:flex; justify-content:flex-end;">
            <div class='chat-bubble user-bubble'>{prompt}</div>
        </div>
    """, unsafe_allow_html=True)

    # Send message to Azure Agent
    project.agents.messages.create(
        thread_id=current_chat["thread_id"],
        role="user",
        content=prompt
    )

    # Process agent run
    run = project.agents.runs.create_and_process(
        thread_id=current_chat["thread_id"],
        agent_id=agent.id
    )

    # Handle failure
    if run.status == "failed":
        response = f"❌ Run failed: {run.last_error}"
    else:
        # Fetch latest assistant response
        messages = project.agents.messages.list(
            thread_id=current_chat["thread_id"],
            order=ListSortOrder.ASCENDING
        )
        response = ""
        for message in messages:
            if message.role == "assistant" and message.text_messages:
                response = message.text_messages[-1].text.value

    # Add assistant message
    current_chat["messages"].append({"role": "assistant", "content": response})
    st.markdown(f"""
        <div style="display:flex; justify-content:flex-start;">
            <div class='chat-bubble assistant-bubble'>{response}</div>
        </div>
    """, unsafe_allow_html=True)
