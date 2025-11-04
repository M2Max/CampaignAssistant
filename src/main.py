import os
import streamlit as st
from dotenv import load_dotenv
from Agent.CampaignAgent import CampaignAgent

load_dotenv()

st.set_page_config(
    page_title="Campaign Assistant",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Campaign Assistant")
st.markdown("Ask questions about your marketing campaign history")

@st.cache_resource
def get_agent():
    return CampaignAgent()

agent = get_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to know about your campaigns?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing campaign data..."):
            result = agent.invoke(prompt)
            response = result["messages"][-1].content
            print(response)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

with st.sidebar:
    st.header("Example Questions")
    st.markdown("""
    - What are the Top Performing Segments in the Wellness campaign?
    - Compare email vs social media campaigns by engagement rate
    - What were the key success factors in the TechStart campaign?
    - Show me campaigns with the highest ROI
    - What channels performed best for the Gaming Launch?
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()