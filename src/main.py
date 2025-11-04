import os
from dotenv import load_dotenv
from Agent.CampaignAgent import CampaignAgent

load_dotenv()

def main():
    agent = CampaignAgent()
    result = agent.invoke("What is the history of the campaign?")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    print("This is the main module.")
    main()