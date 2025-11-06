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
        thinking_placeholder = st.empty()
        response_placeholder = st.empty()
        response_text = ""
        thinking_text = ""
        buffer = ""
        inside_think = False
        seen_any_ai_message = False
        
        try:
            for event in agent.stream(prompt):
                if not isinstance(event, tuple) or len(event) != 2:
                    continue
                
                stream_type, data = event
                
                if stream_type == "messages" and isinstance(data, tuple) and len(data) > 0:
                    message = data[0]
                    if "Tool" not in type(message).__name__ and hasattr(message, "content") and message.content:
                        if not seen_any_ai_message:
                            seen_any_ai_message = True
                        
                        buffer += message.content
                        
                        while len(buffer) >= 10 or "</think>" in buffer:
                            if not inside_think and "<think>" in buffer:
                                idx = buffer.index("<think>")
                                if idx > 0:
                                    response_text += buffer[:idx]
                                    response_placeholder.markdown(response_text + "▌")
                                buffer = buffer[idx + 7:]
                                inside_think = True
                                continue
                            
                            if inside_think and "</think>" in buffer:
                                idx = buffer.index("</think>")
                                thinking_text += buffer[:idx]
                                buffer = buffer[idx + 8:]
                                inside_think = False
                                if thinking_text.strip():
                                    thinking_placeholder.markdown(
                                        f'<div style="color: #888; font-size: 0.9em; font-style: italic; padding: 8px; '
                                        f'border-left: 3px solid #888; margin-bottom: 10px;">'
                                        f'💭 {thinking_text.strip()}</div>',
                                        unsafe_allow_html=True
                                    )
                                continue
                            
                            if inside_think:
                                thinking_text += buffer[0] if buffer else ""
                                buffer = buffer[1:] if buffer else ""
                                if thinking_text.strip():
                                    thinking_placeholder.markdown(
                                        f'<div style="color: #888; font-size: 0.9em; font-style: italic; padding: 8px; '
                                        f'border-left: 3px solid #888; margin-bottom: 10px;">'
                                        f'💭 {thinking_text.strip()}...</div>',
                                        unsafe_allow_html=True
                                    )
                                continue
                            
                            if buffer and not inside_think:
                                response_text += buffer[0]
                                buffer = buffer[1:]
                                response_placeholder.markdown(response_text + "▌")
                            else:
                                break
            
            if buffer and not inside_think:
                response_text += buffer
            
            if thinking_text.strip():
                thinking_placeholder.markdown(
                    f'<div style="color: #888; font-size: 0.9em; font-style: italic; padding: 8px; '
                    f'border-left: 3px solid #888; margin-bottom: 10px;">'
                    f'💭 {thinking_text.strip()}</div>',
                    unsafe_allow_html=True
                )
            
            final_response = response_text.strip()
            response_placeholder.markdown(final_response if final_response else 
                                        "I apologize, but I couldn't generate a response. Please try again.")
        
        except Exception as e:
            final_response = f"An error occurred: {str(e)}"
            response_placeholder.error(final_response)
            print(f"Error: {e}")
    
    st.session_state.messages.append({"role": "assistant", "content": final_response if final_response else "No response generated"})

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