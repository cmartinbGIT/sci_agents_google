import os
from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor

from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/cmart/google-agents/code-git/.env")

def build_math_worker(
    default_model: str,
    code_executor: BuiltInCodeExecutor,
) -> LlmAgent:
    """
    MathWorker: safe, precise math & basic data manipulation using code execution.
    """
    model = os.getenv("MATH_WORKER_MODEL", default_model)

    instruction = (
        "You are a math specialist agent. "
        "You solve mathematical and numerical problems step by step. "
        "For anything non-trivial, you should write Python code and rely on "
        "the code execution environment for exact results. "
        "Return a short explanation plus final result."
    )

    return LlmAgent(
        name="MathWorker",
        model=model,
        instruction=instruction,
        description="Math specialist using Gemini code execution.",
        code_executor=code_executor,
    )
