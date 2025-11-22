import streamlit as st
from dotenv import load_dotenv

from Agent.CampaignAgent import CampaignAgent
from ui.chat_sessions import (
    create_new_chat,
    ensure_session_state,
    get_active_chat,
    get_chat_sessions,
    rename_chat_if_needed,
    rotate_uploader_key,
    set_active_chat_by_index,
    sync_selector_index,
)
from ui.document_ingestion import SUPPORTED_FILE_TYPES, ingest_documents
from ui.theme import inject_minimal_theme

load_dotenv()

st.set_page_config(
    page_title="Campaign Assistant",
    page_icon="📊",
    layout="wide",
)


@st.cache_resource
def get_agent():
    return CampaignAgent()


def handle_chat_selection():
    sessions = get_chat_sessions()
    if not sessions:
        return

    sync_selector_index()

    selection = st.radio(
        "Previous chats",
        options=list(range(len(sessions))),
        index=st.session_state.chat_selector_index,
        format_func=lambda idx: sessions[idx]["title"],
        label_visibility="collapsed",
    )

    if selection != st.session_state.chat_selector_index:
        set_active_chat_by_index(selection)
        st.rerun()


def render_sidebar(agent: CampaignAgent):
    with st.sidebar:
        st.markdown("### Workspace")
        new_chat_clicked = st.button("＋ New Chat", use_container_width=True)
        add_docs_clicked = st.button("⬆️ Add documents to vectorstore", use_container_width=True)

        if new_chat_clicked:
            create_new_chat()
            st.rerun()

        if add_docs_clicked:
            st.session_state.show_uploader = not st.session_state.show_uploader

        if st.session_state.show_uploader:
            st.write("Upload .txt, .md, .json, .yaml/.yml, .pdf, .docx")
            uploaded_files = st.file_uploader(
                "Select documents",
                type=SUPPORTED_FILE_TYPES,
                accept_multiple_files=True,
                key=st.session_state.vectorstore_uploader_key,
            )
            if uploaded_files:
                success, error = ingest_documents(uploaded_files, agent.campaign_history)
                st.session_state.ingestion_feedback = {"success": success, "error": error}
                st.session_state.show_uploader = False
                rotate_uploader_key()
                st.rerun()

        if st.session_state.ingestion_feedback:
            feedback = st.session_state.ingestion_feedback
            if feedback.get("success"):
                st.success(feedback["success"])
            if feedback.get("error"):
                st.warning(feedback["error"])

        st.markdown("---")
        st.markdown("### Past chats")
        handle_chat_selection()


def render_chat_ui(agent: CampaignAgent):
    active_chat = get_active_chat()
    if not active_chat:
        active_chat = create_new_chat()

    st.title("📊 Campaign Assistant")
    st.markdown(
        '<div class="minimal-card">Ask anything about your marketing campaign history. '
        "Responses will use the current vectorstore context.</div>",
        unsafe_allow_html=True,
    )

    for message in active_chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about your campaigns…"):
        active_chat["messages"].append({"role": "user", "content": prompt})
        rename_chat_if_needed(active_chat, prompt)

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            final_response = ""
            response_placeholder = st.empty()

            try:
                with st.spinner("Thinking through your campaign data…"):
                    result = agent.invoke(prompt)
                    final_response = result["messages"][-1].content

                response_placeholder.markdown(final_response)

            except Exception as e:
                final_response = f"An error occurred: {str(e)}"
                response_placeholder.error(final_response)
                print(f"Error: {e}")

        active_chat["messages"].append(
            {
                "role": "assistant",
                "content": final_response if final_response else "No response generated",
            }
        )


def main():
    inject_minimal_theme()
    ensure_session_state()
    agent = get_agent()
    render_sidebar(agent)
    render_chat_ui(agent)


if __name__ == "__main__":
    main()