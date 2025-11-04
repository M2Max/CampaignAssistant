import os
from typing import Literal
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain_ollama import ChatOllama
from VectorStore.CampaignHistory import CampaignHistory

class CampaignAgent:

    def __init__(self):
        prompt_path = os.path.join(os.path.dirname(__file__), "AgentPrompt.txt")
        with open(prompt_path, "r") as f:
            self.research_instructions = f.read().replace("\n", " ")
        
        # Construct correct path to CampaignTxts directory
        txt_directory = os.path.join(os.path.dirname(__file__), "..", "VectorStore", "CampaignTxts")
        self.campaign_history = CampaignHistory(txt_directory=txt_directory, persist_directory="/home/mamox/Documents/Repos/CampaignAssistant/ChromaDB")

        model = init_chat_model("google_genai:gemini-flash-lite-latest")
        # Try to use Ollama model, fallback to Google if needed
        # try:
        #     model = ChatOllama(model="qwen3:1.7b", temperature=0)
        #     # Test the model
        #     model.invoke("test")
        #     print("Using Ollama model (qwen3:1.7b)")
        # except Exception as e:
        #     print(f"Ollama not available, trying Google Gemini: {str(e)[:50]}")
        #     try:
        #         model = init_chat_model("google_genai:gemini-flash-lite-latest")
        #     except Exception as e2:
        #         print(f"Google Gemini not available either, using fallback")
        #         # Use a fallback model

        self.agent = create_deep_agent(
            tools=[self.campaign_history.get_retriever_tool()],
            system_prompt=self.research_instructions,
            model=model
        )

    def invoke(self, message: str):
        return self.agent.invoke(input={"messages": [{"role": "user", "content": message}]})


