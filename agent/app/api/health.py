"""GET /health"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.config import get_settings
from app.llm import is_configured

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "up",
        "version": settings.agent_version,
        "runtime": {
            "mode": "multi_agent",
            "agents": ["planner", "pedagogy", "coach", "code"],
            "pipelines": [
                "plan_negotiate",
                "teach_loop",
                "code_help",
                "intervention",
            ],
        },
        "llm": {
            "provider": "openai_compatible",
            "configured": is_configured(),
            "model": settings.model_name,
        },
    }
