from typing import Literal

import anthropic
from pydantic import BaseModel

from agents.code_agent import CodeAgent
from agents.email_agent import EmailAgent
from agents.research_agent import ResearchAgent
from agents.travel_agent import TravelAgent


class _Route(BaseModel):
    agent: Literal["code", "email", "research", "travel"]


_ROUTING_SYSTEM = """You are a task router. Classify the user request into exactly one category:
- code: writing, debugging, explaining, or reviewing code
- email: checking inbox, finding urgent/pending emails, email summaries
- research: finding information, explaining topics, fact-checking, general knowledge
- travel: flights, hotels, destinations, itineraries, travel planning and advice"""


class Orchestrator:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.agents: dict[str, CodeAgent | EmailAgent | ResearchAgent | TravelAgent] = {
            "code": CodeAgent(),
            "email": EmailAgent(),
            "research": ResearchAgent(),
            "travel": TravelAgent(),
        }

    def route(self, user_input: str) -> str:
        response = self.client.messages.parse(
            model="claude-opus-4-7",
            max_tokens=64,
            output_config={"effort": "low"},
            system=_ROUTING_SYSTEM,
            messages=[{"role": "user", "content": user_input}],
            output_format=_Route,
        )
        agent_name = response.parsed_output.agent
        print(f"[→ {agent_name} agent]\n")
        return self.agents[agent_name].run(user_input)
