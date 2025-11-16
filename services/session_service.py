import os
import logging
from typing import Optional

from google.adk.sessions import (
    InMemorySessionService,
    DatabaseSessionService,
    BaseSessionService,
)


logger = logging.getLogger(__name__)


def get_session_service() -> BaseSessionService:
    """
    Factory that returns an appropriate SessionService.

    - Prod: DATABASE_URL -> DatabaseSessionService
    - Dev:  fallback to InMemorySessionService
    """
    db_url: Optional[str] = os.getenv("DATABASE_URL")

    if db_url:
        logger.info("Using DatabaseSessionService with url=%s", db_url)
        return DatabaseSessionService(db_url=db_url)

    logger.warning(
        "DATABASE_URL not set. Using InMemorySessionService (NOT persistent, "
        "only recommended for local dev / testing)."
    )
    return InMemorySessionService()
