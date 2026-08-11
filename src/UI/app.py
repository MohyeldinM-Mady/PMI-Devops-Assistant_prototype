import requests
import streamlit as st


st.set_page_config(
    page_title="PMI",
    page_icon="🤖",
    layout="centered",
)


# Initialize chat storage
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


# Sidebar
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


# Current chat
current_chat = st.session_state.chats[
    st.session_state.current_chat_id
]

st.title("🤖 PMI")
st.caption("Project Memory Intelligence")


# Display current conversation
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# User input
question = st.chat_input("Ask PMI about your project...")


if question:
    messages = current_chat["messages"]

    # Save user message
    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

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