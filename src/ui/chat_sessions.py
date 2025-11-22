import time
from typing import Optional
from uuid import uuid4

import streamlit as st


def ensure_session_state() -> None:
    """Initialize Streamlit session variables required for chat management."""
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []
    if "active_chat_id" not in st.session_state:
        st.session_state.active_chat_id = None
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False
    if "ingestion_feedback" not in st.session_state:
        st.session_state.ingestion_feedback = None
    if "vectorstore_uploader_key" not in st.session_state:
        st.session_state.vectorstore_uploader_key = "vectorstore_uploader"
    if "chat_selector_index" not in st.session_state:
        st.session_state.chat_selector_index = 0
    if "chat_selector" not in st.session_state:
        st.session_state.chat_selector = 0

    if not st.session_state.chat_sessions:
        create_new_chat()
    else:
        sync_selector_index()


def create_new_chat() -> dict:
    """Create a new empty chat session and activate it."""
    chat_id = str(uuid4())
    new_chat = {
        "id": chat_id,
        "title": f"Untitled chat {len(st.session_state.chat_sessions) + 1}",
        "messages": [],
        "created_at": time.time(),
    }
    st.session_state.chat_sessions.insert(0, new_chat)
    set_active_chat_by_index(0)
    return new_chat


def get_chat_sessions() -> list[dict]:
    """Return all chat sessions."""
    return st.session_state.chat_sessions


def get_active_chat() -> Optional[dict]:
    """Return the currently active chat session (if any)."""
    active_id = st.session_state.active_chat_id
    for chat in st.session_state.chat_sessions:
        if chat["id"] == active_id:
            return chat
    return None


def rename_chat_if_needed(chat: dict, prompt: str) -> None:
    """Rename a newly created chat based on the user's first message."""
    if chat["title"].startswith("Untitled"):
        trimmed = prompt.strip().splitlines()[0]
        if trimmed:
            chat["title"] = (trimmed[:32] + "…") if len(trimmed) > 32 else trimmed


def set_active_chat_by_index(index: int) -> None:
    """Activate a chat session by its index."""
    sessions = get_chat_sessions()
    if not sessions:
        return
    clamped_index = max(0, min(index, len(sessions) - 1))
    st.session_state.active_chat_id = sessions[clamped_index]["id"]
    st.session_state.chat_selector_index = clamped_index
    st.session_state.chat_selector = clamped_index


def set_active_chat(chat_id: str) -> None:
    """Activate a chat session by its identifier."""
    for idx, chat in enumerate(get_chat_sessions()):
        if chat["id"] == chat_id:
            set_active_chat_by_index(idx)
            return


def sync_selector_index() -> None:
    """Ensure the sidebar selector index matches the active chat."""
    sessions = get_chat_sessions()
    if not sessions:
        st.session_state.chat_selector_index = 0
        st.session_state.chat_selector = 0
        return

    for idx, chat in enumerate(sessions):
        if chat["id"] == st.session_state.active_chat_id:
            st.session_state.chat_selector_index = idx
            st.session_state.chat_selector = idx
            return

    # If we reach this point the active chat is missing—fallback to the first one.
    set_active_chat_by_index(0)


def rotate_uploader_key() -> None:
    """Force the Streamlit file uploader to reset after ingest."""
    st.session_state.vectorstore_uploader_key = f"vectorstore_uploader_{uuid4().hex}"
