# app.py
import os
import yaml
from google.adk.apps import App
from google.adk.sessions import VertexAiSessionService  # Agent Engine uses this
from google.adk.runners import Runner

from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/cmart/google-agents/code-git/.env")

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

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/config.yaml")


def _load_config(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


config = _load_config(CONFIG_PATH)

APP_NAME = os.getenv("APP_NAME", config.get("app_name", "sciagent_system"))
DEFAULT_MODEL = os.getenv(
    "DEFAULT_MODEL",
    config.get("default_model", "gemini-2.0-flash"),
)

# Tell google-genai / ADK to use Vertex AI
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")

def build_app() -> App:
    # Session service – when running in Agent Engine, this will
    # get bound to VertexAiSessionService automatically.
    session_service = VertexAiSessionService()

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

    # Runner to connect the agent + session service
    # runner = Runner(
    #     agent=coordinator_agent,
    #     app_name=APP_NAME,
    #     session_service=session_service,
    # )

    # Wrap in App
    return App(
        name=APP_NAME,
        root_agent=coordinator_agent,
    )


# Agent Engine will look for a variable named `app`
app = build_app()
