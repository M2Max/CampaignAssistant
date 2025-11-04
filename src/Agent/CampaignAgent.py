import os
from typing import Literal
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from VectorStore.CampaignHistory import CampaignHistory

class CampaignAgent:

    def __init__(self):
        prompt_path = os.path.join(os.path.dirname(__file__), "AgentPrompt.txt")
        with open(prompt_path, "r") as f:
            self.research_instructions = f.read().replace("\n", " ")
        
        # Construct correct path to CampaignTxts directory
        txt_directory = os.path.join(os.path.dirname(__file__), "..", "VectorStore", "CampaignTxts")
        self.campaign_history = CampaignHistory(txt_directory=txt_directory)

        model = init_chat_model("google_genai:gemini-flash-lite-latest")

        self.agent = create_deep_agent(
            tools=[self.campaign_history.get_retriever_tool()],
            system_prompt=self.research_instructions,
            model=model
        )

    def invoke(self, message: str):
        return self.agent.invoke(input={"messages": [{"role": "user", "content": message}]})


