import os
from typing import List

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/cmart/google-agents/code-git/.env")

def build_coordinator_agent(
    default_model: str,
    math_agent,
    physics_agent,
    general_agent,
) -> LlmAgent:
    """
    CoordinatorAgent orchestrates:
      - MathWorker
      - PhysicsWorker
      - GeneralSciWorker (RAG + web search)

    It decides which specialist(s) to delegate to based on the user request.
    """
    model = os.getenv("COORDINATOR_MODEL", default_model)

    tools: List[object] = [
        AgentTool(agent=math_agent),
        AgentTool(agent=physics_agent),
        AgentTool(agent=general_agent),
    ]

    instruction = (
        "You are the coordinator agent in a scientific multi-agent system focused "
        "on carbon capture and climate-relevant engineering.\n\n"
        "Your responsibilities:\n"
        "- If the question is primarily numeric or algebraic, delegate to MathWorker.\n"
        "- If the question is about physics/engineering phenomena or process design "
        "  (e.g., mass/energy balance, reactor sizing, separations), delegate "
        "  to PhysicsWorker.\n"
        "- If the question is about literature, policies, or high-level scientific "
        "  reasoning, delegate to GeneralSciWorker.\n"
        "- You may call multiple workers and then synthesize a final answer.\n\n"
        "Always return a clear, structured answer suitable for an engineer or "
        "researcher. Mention which agents and tools you used."
    )

    return LlmAgent(
        name="CoordinatorAgent",
        model=model,
        instruction=instruction,
        description="Coordinator for scientific multi-agent team focused on carbon capture.",
        tools=tools,
    )
