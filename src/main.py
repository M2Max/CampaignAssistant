import os
import time
import streamlit as st
from dotenv import load_dotenv
from Agent.CampaignAgent import CampaignAgent

load_dotenv()

assets_path = os.path.join(os.path.dirname(__file__), "assets")
assitant_avatar: str = os.path.join(assets_path, "assistant.png")
user_avatar: str = os.path.join(assets_path, "user.png")
logo: str = os.path.join(assets_path, "logo.png")


st.set_page_config(
    page_title="CampaignChamp",
    page_icon=os.path.join(assets_path, "logo.ico"),
    layout="centered"
)

@st.cache_resource(show_spinner="Initizializing CampaignChamp...")
def get_agent():
    return CampaignAgent()

agent = get_agent()

st.title("CampaignChamp")
st.caption("A calm space to revisit past campaign work.")


if "messages" not in st.session_state:
    st.session_state.messages = []

if "past_chats" not in st.session_state:
    st.session_state.past_chats = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to know about your campaigns?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=assitant_avatar):
        final_response = ""
        response_placeholder = st.empty()
        
        try:
            with st.spinner("Processing your request..."):
                result = agent.invoke(prompt)
                final_response = result["messages"][-1].content
            
            displayed_text = ""
            for char in final_response:
                displayed_text += char
                response_placeholder.markdown(displayed_text + "▌")
                time.sleep(0.01)
            
            response_placeholder.markdown(final_response)
            
        except Exception as e:
            final_response = f"An error occurred: {str(e)}"
            response_placeholder.error(final_response)
            print(f"Error: {e}")
    
    
    
    st.session_state.messages.append({"role": "assistant", "content": final_response if final_response else "No response generated"})

@st.dialog("Upload new data into the campaign history database")
def upload_data():
    file = st.file_uploader("Upload a file", type=["txt", "md", "pdf"])
    if file:
        try:
            with st.spinner("Analyzing the file..."):
                agent.campaign_history.add_documents([file])
            st.success("File uploaded successfully")
        except Exception as e:
            st.error(f"Error analyzing the file: {e}")
    else:
        st.error("No file uploaded")

with st.sidebar:
    st.image(os.path.join(assets_path, "logo.png"), width=150)
    if st.button("New chat", use_container_width=True):      
        st.session_state.past_chats.append(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    if st.button("Upload data", use_container_width=True):
        upload_data()

    st.divider()

    st.markdown("**Previous chats**")
    st.caption("Select a thread to revisit (coming soon).")
    placeholder_chats = [
        "Autumn brand refresh",
        "Q2 nurture recap",
        "Channel mix audit",
    ]
    def load_selected_chat_history():
        selected_chat = st.session_state.get("sidebar_history_placeholder")
        if isinstance(selected_chat, dict):
            selected_messages = selected_chat
        elif isinstance(selected_chat, list):
            selected_messages = selected_chat
        else:
            return

        # Copy to avoid mutating the stored history entry
        st.session_state.messages = selected_messages.copy()

    st.radio(
        "Previous chats",
        reversed(st.session_state.past_chats),
        index=0,
        label_visibility="collapsed",
        key="sidebar_history_placeholder",
        on_change=load_selected_chat_history,
    )