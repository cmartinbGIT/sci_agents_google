import os
from typing import Optional, List

from google.adk.agents import LlmAgent
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools.tool_context import ToolContext

from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/cmart/google-agents/code-git/.env")

def build_general_worker(
    default_model: str,
    vertex_search_tool: VertexAiSearchTool,
    google_search_tool: Optional[GoogleSearchTool] = None,
    code_executor: Optional[BuiltInCodeExecutor] = None,
) -> LlmAgent:
    """
    GeneralSciWorker: scientific reasoning + literature/policy lookup.

    Tools:
      - Vertex AI Search for private carbon-capture / internal docs RAG
      - Google Search (optional) for public web info
      - Code executor (optional) for light data analysis
    """
    model = os.getenv("GENERAL_WORKER_MODEL", default_model)

    tools: List[object] = [vertex_search_tool]
    if google_search_tool is not None:
        tools.append(google_search_tool)

    instruction = (
        "You are a domain-general scientific assistant with a focus on "
        "carbon capture, climate, and engineering. "
        "Use Vertex AI Search to retrieve relevant technical documents "
        "(papers, reports, design guides) from the configured corpus. "
        "If the user explicitly asks for up-to-date public information, "
        "you may use Google Search. "
        "Always cite which source (RAG document, web) you relied on in your answer."
    )

    return LlmAgent(
        name="GeneralSciWorker",
        model=model,
        instruction=instruction,
        description="General science worker (RAG + web search) with carbon-capture focus.",
        tools=tools,
        code_executor=code_executor,
    )
