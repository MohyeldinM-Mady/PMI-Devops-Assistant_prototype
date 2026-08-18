import os
import sys
import time
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_cookies_manager import EncryptedCookieManager


load_dotenv()


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from src.pipeline import prepare_current_repository
from src.Database.chat_repository import (
    add_message,
    create_chat,
    ensure_first_chat,
    init_chat_tables,
    list_chats,
    update_chat,
)


st.set_page_config(
    page_title="PMI",
    page_icon="🤖",
    layout="centered",
)


API_URL = "http://127.0.0.1:8000"


# ============================================================
# Persistent Authentication Cookie
# ============================================================

COOKIE_NAME = "pmi_access_token"
COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days

COOKIES_PASSWORD = os.getenv("COOKIES_PASSWORD")

if not COOKIES_PASSWORD:
    st.error(
        "COOKIES_PASSWORD is missing. "
        "Add it to your .env file before starting PMI."
    )
    st.stop()

cookies = EncryptedCookieManager(
    prefix="pmi/",
    password=COOKIES_PASSWORD,
)

# IMPORTANT:
# The cookie component needs one run to load the browser cookies.
# Without this guard, an F5 refresh can temporarily look like
# the user is logged out before the cookie arrives from the browser.
if "cookie_ready_attempts" not in st.session_state:
    st.session_state.cookie_ready_attempts = 0

if not cookies.ready():

    # The cookie component can need one or more browser round-trips
    # after a hard refresh. Give it a few attempts instead of treating
    # the temporary "not ready" state as a logged-out state.
    st.session_state.cookie_ready_attempts += 1

    if st.session_state.cookie_ready_attempts <= 10:
        time.sleep(0.3)
        st.rerun()

    st.error(
        "Could not load the authentication cookie. "
        "Please refresh the page once."
    )
    st.stop()

# Cookie component is ready; reset the retry counter.
st.session_state.cookie_ready_attempts = 0


# ============================================================
# Authentication State
# ============================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "signin"


# ============================================================
# Restore Session From Persistent Cookie
# ============================================================

if not st.session_state.access_token:

    saved_token = cookies.get(COOKIE_NAME)

    if saved_token:

        try:

            user_response = requests.get(
                f"{API_URL}/Auth/me",
                headers={
                    "Authorization": f"Bearer {saved_token}",
                },
                timeout=30,
            )

            if user_response.status_code == 200:

                st.session_state.access_token = saved_token
                st.session_state.authenticated_user = (
                    user_response.json()
                )

            else:

                if COOKIE_NAME in cookies:
                    del cookies[COOKIE_NAME]

                cookies.save()

        except requests.RequestException:
            pass


# ============================================================
# Authentication Functions
# ============================================================

def signup(
    username: str,
    email: str,
    password: str,
):
    return requests.post(
        f"{API_URL}/Auth/signup",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
        timeout=30,
    )


def signin(
    email: str,
    password: str,
):
    return requests.post(
        f"{API_URL}/Auth/signin",
        json={
            "email": email,
            "password": password,
        },
        timeout=30,
    )


def get_current_user(token: str):
    return requests.get(
        f"{API_URL}/Auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
        timeout=30,
    )


def logout():

    token = st.session_state.access_token

    # Revoke the token on the backend first.
    # Even if an old browser cookie survives briefly, /Auth/me
    # will reject it after this request.
    if token:

        try:

            response = requests.post(
                f"{API_URL}/Auth/logout",
                headers={
                    "Authorization": f"Bearer {token}",
                },
                timeout=30,
            )

            if response.status_code not in (200, 401):
                st.error(
                    "Could not complete logout on the server."
                )

        except requests.RequestException:
            # Local logout still happens. The old token will expire
            # normally if the API was unavailable during logout.
            pass

    st.session_state.access_token = None
    st.session_state.authenticated_user = None
    st.session_state.auth_page = "signin"

    st.session_state.pop("chats", None)
    st.session_state.pop("current_chat_id", None)
    st.session_state.pop("chat_db_user_id", None)

    if COOKIE_NAME in cookies:
        del cookies[COOKIE_NAME]

    cookies.save()


# ============================================================
# Authentication UI
# ============================================================

if not st.session_state.access_token:

    st.title("🤖 PMI")
    st.caption("Project Memory Intelligence")

    # ========================================================
    # Sign In
    # ========================================================

    if st.session_state.auth_page == "signin":

        st.subheader("Welcome back")

        with st.form("signin_form"):

            email = st.text_input(
                "Email",
                placeholder="you@example.com",
                key="signin_email",
                autocomplete="username",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="signin_password",
                autocomplete="current-password",
            )

            submitted = st.form_submit_button(
                "Sign In",
                use_container_width=True,
            )

        if submitted:

            if not email or not password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                try:

                    response = signin(
                        email,
                        password,
                    )

                    if response.status_code == 200:

                        token = response.json()["access_token"]

                        user_response = get_current_user(token)

                        if user_response.status_code == 200:

                            # Save token in session.
                            st.session_state.access_token = token

                            # Save user information.
                            st.session_state.authenticated_user = (
                                user_response.json()
                            )

                            # Persist the JWT in the browser.
                            cookies[COOKIE_NAME] = token
                            cookies.save()

                            # Let the browser commit the cookie before rerun.
                            time.sleep(1)

                            st.rerun()

                        else:

                            st.error(
                                "Could not load user information."
                            )

                    else:

                        try:

                            error = response.json().get(
                                "detail",
                                "Invalid email or password.",
                            )

                        except Exception:

                            error = (
                                "Invalid email or password."
                            )

                        st.error(error)

                except requests.RequestException:

                    st.error(
                        "Could not connect to the PMI API. "
                        "Make sure FastAPI is running."
                    )

        st.divider()

        st.write("Don't have an account?")

        if st.button(
            "Create Account",
            use_container_width=True,
        ):

            st.session_state.auth_page = "signup"

            st.rerun()

    # ========================================================
    # Sign Up
    # ========================================================

    else:

        st.subheader("Create your PMI account")

        with st.form("signup_form"):

            username = st.text_input(
                "Username",
                placeholder="Your username",
                key="signup_username",
            )

            email = st.text_input(
                "Email",
                placeholder="you@example.com",
                key="signup_email",
                autocomplete="off",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="signup_password",
                autocomplete="off",
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                key="signup_confirm_password",
                autocomplete="off",
            )

            submitted = st.form_submit_button(
                "Create Account",
                use_container_width=True,
            )

        if submitted:

            if not username or not email or not password:

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 8:

                st.error(
                    "Password must be at least 8 characters."
                )

            else:

                try:

                    response = signup(
                        username,
                        email,
                        password,
                    )

                    if response.status_code == 201:

                        # Clear Sign Up fields
                        st.session_state.pop(
                            "signup_username",
                            None,
                        )

                        st.session_state.pop(
                            "signup_email",
                            None,
                        )

                        st.session_state.pop(
                            "signup_password",
                            None,
                        )

                        st.session_state.pop(
                            "signup_confirm_password",
                            None,
                        )

                        # Success message
                        st.success(
                            "✅ Account created successfully!"
                        )

                        # Keep message visible
                        time.sleep(2)

                        # Route to Sign In
                        st.session_state.auth_page = "signin"

                        st.rerun()

                    else:

                        try:

                            error = response.json().get(
                                "detail",
                                "Could not create account.",
                            )

                        except Exception:

                            error = (
                                "Could not create account."
                            )

                        st.error(error)

                except requests.RequestException:

                    st.error(
                        "Could not connect to the PMI API. "
                        "Make sure FastAPI is running."
                    )

        st.divider()

        st.write("Already have an account?")

        if st.button(
            "Sign In",
            use_container_width=True,
        ):

            st.session_state.auth_page = "signin"

            st.rerun()

    # Stop here until user signs in
    st.stop()


# ============================================================
# Chat Storage
# ============================================================

user = st.session_state.authenticated_user

try:
    user_id = int(user.get("id") or user.get("user_id"))
except (TypeError, ValueError, AttributeError):
    st.error("Could not determine the authenticated user.")
    st.stop()

# Chat history is persisted in SQLite.
init_chat_tables()

# Always make sure the in-memory state exists.
# A browser refresh can recreate part of session_state, and logout/login
# can intentionally clear the chat state. The database remains the source
# of truth, so restoring it here is safe.
if (
    "chats" not in st.session_state
    or "chat_db_user_id" not in st.session_state
    or st.session_state.chat_db_user_id != user_id
):

    st.session_state.chat_db_user_id = user_id

    chats = list_chats(user_id)

    if not chats:
        chat_id = ensure_first_chat(user_id)
        chats = list_chats(user_id)
    else:
        chat_id = next(iter(chats))

    st.session_state.chats = chats
    st.session_state.current_chat_id = str(chat_id)

# Defensive fallback in case session_state was cleared while the user
# is still authenticated.
if "chats" not in st.session_state:
    chats = list_chats(user_id)

    if not chats:
        chat_id = ensure_first_chat(user_id)
        chats = list_chats(user_id)
    else:
        chat_id = next(iter(chats))

    st.session_state.chats = chats
    st.session_state.current_chat_id = str(chat_id)

if (
    "current_chat_id" not in st.session_state
    or st.session_state.current_chat_id not in st.session_state.chats
):
    st.session_state.current_chat_id = next(
        iter(st.session_state.chats)
    )


def create_new_chat():
    chat_id = create_chat(user_id)
    st.session_state.chats = list_chats(user_id)
    st.session_state.current_chat_id = str(chat_id)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.title("PMI")
    st.caption("Project Memory Intelligence")

    user = st.session_state.authenticated_user

    if user:

        st.write(
            f"👤 **{user['username']}**"
        )

    if st.button(
        "🚪 Logout",
        key="logout_button",
        use_container_width=True,
    ):
        logout()
        st.rerun()

    st.divider()

    if st.button(
        "＋ New Chat",
        use_container_width=True,
    ):

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
    [
        "💬 Chatbot",
        "📥 Retrieve Data from Current Repo",
    ]
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

            st.markdown(
                message["content"]
            )


# ============================================================
# Retrieve Data from Current Repo
# ============================================================

with tab_retrieve:

    st.header(
        "📥 Retrieve Data from Current Repo"
    )

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

    chat_id = int(st.session_state.current_chat_id)
    messages = current_chat["messages"]

    # Persist the user message in SQLite.
    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    add_message(
        chat_id=chat_id,
        user_id=user_id,
        role="user",
        content=question,
    )

    # Show user message
    with tab_chat:

        with st.chat_message("user"):

            st.markdown(question)

        # Send previous conversation history
        history = messages[:-1]

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    response = requests.post(
                        f"{API_URL}/chat",
                        headers={
                            "Authorization": (
                                f"Bearer "
                                f"{st.session_state.access_token}"
                            )
                        },
                        json={
                            "question": question,
                            "history": history,
                            "active_reference": (
                                current_chat.get(
                                    "active_reference"
                                )
                            ),
                        },
                        timeout=120,
                    )

                    # Token expired or became invalid
                    if response.status_code == 401:

                        logout()

                        st.warning(
                            "Your session has expired. "
                            "Please sign in again."
                        )

                        st.rerun()

                    response.raise_for_status()

                    payload = response.json()

                    answer = payload["answer"]

                    current_chat["active_reference"] = (
                        payload.get(
                            "active_reference"
                        )
                    )

                    st.markdown(answer)

                except requests.RequestException:

                    answer = (
                        "❌ Could not connect to the PMI API. "
                        "Please make sure the FastAPI server "
                        "is running."
                    )

                    st.error(answer)

    # Save assistant response in SQLite.
    messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    add_message(
        chat_id=chat_id,
        user_id=user_id,
        role="assistant",
        content=answer,
    )

    # Use first question as chat title.
    if current_chat["title"] == "New Chat":

        current_chat["title"] = question[:35]

        update_chat(
            chat_id=chat_id,
            user_id=user_id,
            title=current_chat["title"],
        )

    # Persist the latest active reference.
    update_chat(
        chat_id=chat_id,
        user_id=user_id,
        active_reference=current_chat.get("active_reference"),
    )

    st.session_state.chats = list_chats(user_id)

    st.rerun()