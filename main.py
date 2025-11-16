# main.py
# # Defines CoordinatorAgent class/logic
import os
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel

import logging
import os
from uuid import uuid4
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from google.adk.runners import Runner
from google.genai import types


load_dotenv(dotenv_path="C:/Users/cmart/google-agents/code-git/.env")

google_api_key = os.getenv("GOOGLE_API_KEY")
PROJECT_ID = os.getenv("VERTEX_PROJECT_ID")
LOCATION = os.getenv("VERTEX_LOCATION")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Choose a Gemini model deployed on Vertex AI
model = GenerativeModel("gemini-2.5-flash")

from agents import (
    build_coordinator_agent,
    build_math_worker,
    build_physics_worker,
    build_general_worker,
)
from tools import (
    build_vertex_ai_search_tool,
    build_google_search_tool,
    build_code_executor,
)
from services.session_service import get_session_service


# ---------------------------------------------------------------------------
# Logging & basic config
# ---------------------------------------------------------------------------
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("sciagent_system")

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/config.yaml")


def _load_config(path: str) -> dict:
    if not os.path.exists(path):
        logger.warning("Config file %s not found. Using env/defaults only.", path)
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


config = _load_config(CONFIG_PATH)

APP_NAME = os.getenv("APP_NAME", config.get("app_name", "sciagent_system"))
DEFAULT_MODEL = os.getenv(
    "DEFAULT_MODEL",
    config.get("default_model", "gemini-2.0-flash"),
)

# Required for ADK + Vertex AI if you’re using Vertex instead of AI Studio
# https://docs.sea-lion.ai/guides/agents/google_adk (env discussion) 
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")

# ---------------------------------------------------------------------------
# Build session service, tools, agents, runner
# ---------------------------------------------------------------------------

session_service = get_session_service()

# Tools
vertex_search_cfg = config.get("vertex_search", {}) if isinstance(config, dict) else {}
vertex_search_data_store = vertex_search_cfg.get("data_store_id")

vertex_search_tool = build_vertex_ai_search_tool(data_store_id=vertex_search_data_store)
google_search_tool = build_google_search_tool()
code_executor = build_code_executor()

# Workers
math_agent = build_math_worker(DEFAULT_MODEL, code_executor)
physics_agent = build_physics_worker(DEFAULT_MODEL, code_executor)
general_agent = build_general_worker(
    default_model=DEFAULT_MODEL,
    vertex_search_tool=vertex_search_tool,
    google_search_tool=google_search_tool,
    code_executor=code_executor,
)

# Coordinator
coordinator_agent = build_coordinator_agent(
    default_model=DEFAULT_MODEL,
    math_agent=math_agent,
    physics_agent=physics_agent,
    general_agent=general_agent,
)

# Runner
runner = Runner(
    agent=coordinator_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

# ---------------------------------------------------------------------------
# FastAPI app & models
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SciAgent System",
    description="Multi-agent scientific assistant (carbon capture focus) on Vertex AI using ADK.",
    version="0.1.0",
)


class SolveRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class SolveResponse(BaseModel):
    session_id: str
    answer: str


@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}


@app.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest) -> SolveResponse:
    """
    Single entrypoint:
      - Creates/reuses an ADK session
      - Runs the CoordinatorAgent (which delegates to workers)
      - Returns the final response text
    """
    user_id = req.user_id or "anonymous"
    session_id = req.session_id or f"session-{uuid4().hex}"

    # Ensure session exists
    try:
        session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
    except Exception:  # Session may not exist yet
        logger.info(
            "Creating new session app=%s user=%s session_id=%s",
            APP_NAME,
            user_id,
            session_id,
        )
        session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )

    content = types.Content(
        role="user",
        parts=[types.Part(text=req.query)],
    )

    final_answer: Optional[str] = None

    # Runner.run is a synchronous generator in typical ADK usage. 
    for event in runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_answer = event.content.parts[0].text

    if not final_answer:
        logger.error("CoordinatorAgent returned no final response.")
        raise HTTPException(status_code=500, detail="No response from coordinator agent")

    return SolveResponse(session_id=session_id, answer=final_answer)

