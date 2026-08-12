import sys
from pathlib import Path

import requests
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from src.pipeline import prepare_current_repository


st.set_page_config(
    page_title="PMI",
    page_icon="🤖",
    layout="centered",
)


# ============================================================
# Chat Storage
# ============================================================

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "chat_1"
    st.session_state.chats["chat_1"] = {
        "title": "New Chat",
        "messages": [],
    }


def create_new_chat():
    chat_number = len(st.session_state.chats) + 1
    chat_id = f"chat_{chat_number}"

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": [],
    }

    st.session_state.current_chat_id = chat_id


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.title("PMI")
    st.caption("Project Memory Intelligence")

    if st.button("＋ New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.divider()

    st.subheader("Chats")

    for chat_id, chat in st.session_state.chats.items():
        title = chat["title"]

        if st.button(
            title,
            key=f"chat_button_{chat_id}",
            use_container_width=True,
        ):
            st.session_state.current_chat_id = chat_id
            st.rerun()


# ============================================================
# Current Chat
# ============================================================

current_chat = st.session_state.chats[
    st.session_state.current_chat_id
]


# ============================================================
# Tabs
# ============================================================

tab_chat, tab_retrieve = st.tabs(
    ["💬 Chatbot", "📥 Retrieve Data from Current Repo"]
)


# ============================================================
# Chatbot Tab
# ============================================================

with tab_chat:
    st.title("🤖 PMI")
    st.caption("Project Memory Intelligence")

    # Display current conversation
    for message in current_chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# ============================================================
# Retrieve Data from Current Repo
# ============================================================

with tab_retrieve:
    st.header("📥 Retrieve Data from Current Repo")

    st.write(
        "Prepare the current GitHub repository for PMI "
        "by collecting data, building the knowledge base, "
        "generating embeddings, and updating the vector database."
    )

    if st.button(
        "🚀 Prepare Repository",
        use_container_width=True,
    ):
        try:
            with st.spinner(
                "Preparing repository... "
                "This may take a few minutes."
            ):
                prepare_current_repository()

            st.success(
                "✅ Repository is ready. "
                "You can now use the Chatbot."
            )

        except Exception as e:
            st.error(
                f"❌ Repository preparation failed: {e}"
            )


# ============================================================
# Chat Input
# ============================================================

question = st.chat_input(
    "Ask PMI about your project..."
)


# ============================================================
# Process Question
# ============================================================

if question:
    messages = current_chat["messages"]

    # Save user message
    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    # Show user message
    with tab_chat:
        with st.chat_message("user"):
            st.markdown(question)

        # Send previous conversation history to API
        history = messages[:-1]

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={
                        "question": question,
                        "history": history,
                    },
                )

                response.raise_for_status()

                answer = response.json()["answer"]

            st.markdown(answer)

    # Save assistant response
    messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    # Use first question as chat title
    if current_chat["title"] == "New Chat":
        current_chat["title"] = question[:35]

    st.rerun()