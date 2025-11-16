import os
from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor

from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/cmart/google-agents/code-git/.env")

def build_physics_worker(
    default_model: str,
    code_executor: BuiltInCodeExecutor,
) -> LlmAgent:
    """
    PhysicsWorker: handles physics / engineering calculations (e.g., energy balances),
    powered by code execution for accurate numeric work.
    """
    model = os.getenv("PHYSICS_WORKER_MODEL", default_model)

    instruction = (
        "You are a physicist and engineering calculations specialist. "
        "You help with calculations including units, dimensions, and derived equations. "
        "Use code execution for numerical work (e.g., differential equations, "
        "integrations, parameter sweeps). Be explicit about assumptions."
    )

    return LlmAgent(
        name="PhysicsWorker",
        model=model,
        instruction=instruction,
        description="Physics & engineering worker using code execution.",
        code_executor=code_executor,
    )
