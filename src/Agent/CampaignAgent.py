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
        
        txt_directory = os.path.join(os.path.dirname(__file__), "..", "VectorStore", "CampaignTxts")
        persist_directory = os.path.join(os.path.dirname(__file__), "..", "VectorStore", "ChromaDB")
        self.campaign_history = CampaignHistory(txt_directory=txt_directory, persist_directory=persist_directory)

        # model = init_chat_model("google_genai:gemini-flash-lite-latest")

        try:
            model = init_chat_model(
                model="qwen/qwen3-4b-2507", 
                model_provider="openai", 
                base_url="http://localhost:1234/v1",
                api_key="not-needed" 
            )
            model.invoke("test")
            print("Using LM Studio model (qwen3:4b)")
        except Exception as e:
            print(f"LM Studio not available, trying Google Gemini: {str(e)[:50]}")
            try:
                model = init_chat_model("google_genai:gemini-flash-lite-latest")
            except Exception as e2:
                print(f"Google Gemini not available either, using fallback")

        self.agent = create_deep_agent(
            tools=[self.campaign_history.get_retriever_tool()],
            system_prompt=self.research_instructions,
            model=model
        )

    def invoke(self, message: str):
        return self.agent.invoke(input={"messages": [{"role": "user", "content": message}]})


