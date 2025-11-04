import os
from typing import Literal
from deepagents import create_deep_agent


class CampaignAgent:

    def __init__(self):
        with open("AgentPrompt.txt", "r") as f:
            self.research_instructions = f.read().replace("\n", " ")

        self.agent = create_deep_agent(
            tools=[self.lookup_campaigns_history],
            system_prompt=self.research_instructions
        )
    
    
    def lookup_campaigns_history(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
    ):
        """Run a web search"""
        return tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )

    def invoke(self, message: str):
        return self.agent.invoke(inputs={"messages": [{"role": "user", "content": message}]})


