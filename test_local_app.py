import os
import asyncio
import uuid
import yaml

from google.genai import types
from google.adk.sessions import InMemorySessionService
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
    build_code_executor,
)

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/config.yaml")

import logging

logging.basicConfig(
    level=logging.DEBUG,  # or INFO if DEBUG is too noisy
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def _load_config(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


async def main():
    config = _load_config(CONFIG_PATH)

    app_name = os.getenv("APP_NAME", config.get("app_name", "sciagent_system_local"))
    default_model = os.getenv(
        "DEFAULT_MODEL",
        config.get("default_model", "gemini-2.0-flash"),
    )

    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")

    # --- Session service ---
    session_service = InMemorySessionService()

    # --- Tools ---
    vertex_search_cfg = config.get("vertex_search", {}) if isinstance(config, dict) else {}
    vertex_search_data_store = vertex_search_cfg.get("data_store_id")
    vertex_search_tool = build_vertex_ai_search_tool(data_store_id=vertex_search_data_store)
    code_executor = build_code_executor()

    # --- Workers ---
    math_agent = build_math_worker(default_model, code_executor)
    physics_agent = build_physics_worker(default_model, code_executor)
    general_agent = build_general_worker(
        default_model=default_model,
        vertex_search_tool=vertex_search_tool,
    )

    # --- Coordinator ---
    coordinator_agent = build_coordinator_agent(
        default_model=default_model,
        math_agent=math_agent,
        physics_agent=physics_agent,
        general_agent=general_agent,
    )

    # --- Runner ---
    runner = Runner(
        agent=coordinator_agent,
        app_name=app_name,
        session_service=session_service,
    )

    user_id = "local-user"
    # you can choose a session id or let ADK generate one
    session_id = f"carbon-session-{uuid.uuid4().hex[:8]}"

    # ✅ CREATE THE SESSION (this is async – MUST await)
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={},   # optional initial state
    )

    print(f"Created session: id={session.id}, app_name={session.app_name}, user_id={session.user_id}")

    # Now send a carbon-capture query using run_async
    query = (
        "Estimate the energy penalty (GJ per ton CO2) and main loss mechanisms "
        "for amine-based post-combustion CO2 capture on a 500 MW coal plant."
        #2 "What are the latest advancements in solid sorbent materials for direct air capture of CO2?"
        #3 "Given a 100-unit apartment building in Barcelona, design a retrofit (insulation + heat pumps + solar + storage) " 
        #3 "that cuts annual CO₂ emissions by at least 70%, and estimate costs + payback."
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text=query)],
    )

    final_answer = None

    print(f"\n=== Running query in session {session.id} ===\n")

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        # 🔍 raw event object
        print("EVENT:", repr(event))

        # Optional: pretty classify by type
        etype = getattr(event, "event_type", None) or event.__class__.__name__
        agent_name = getattr(event, "agent_name", None)
        print(f"- type: {etype}  agent: {agent_name}")

        # If it's an LLM request/response, show the prompt/answer
        if hasattr(event, "content") and event.content and event.content.parts:
            text_parts = [p.text for p in event.content.parts if getattr(p, "text", None)]
            if text_parts:
                print("  text:", "\n  ".join(text_parts[:1]))  # first part only

        # Keep your final-answer extraction
        if event.is_final_response() and event.content and event.content.parts:
            final_answer = event.content.parts[0].text

    print("\n=== FINAL ANSWER ===")
    print(final_answer or "⚠️ No final answer returned.")


if __name__ == "__main__":
    asyncio.run(main())
