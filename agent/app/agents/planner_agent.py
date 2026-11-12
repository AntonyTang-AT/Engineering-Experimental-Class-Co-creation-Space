"""程计：计划草案与仲裁（封装现有 planner/arbitrate workers）。"""

from __future__ import annotations

from app.agents.base import PERSONA, AgentProposal, CollabState
from app.schemas.response import ResponseStatus
from app.workers import arbitrate as arbitrate_worker
from app.workers import planner as planner_worker


def propose_create_plan(state: CollabState) -> AgentProposal:
    resp = planner_worker.handle_create_plan(state.request)
    persona = PERSONA["planner"]["name"]
    plan = (resp.output or {}).get("plan")
    summary = resp.message or "已生成计划草案"
    if resp.status == ResponseStatus.conflict:
        summary = f"发现计划冲突：{resp.message}"
    elif (resp.output or {}).get("error_strategy"):
        tag = (resp.output.get("error_strategy") or {}).get("error_tag")
        summary = f"计划草案已出；并按错因 {tag} 插入补救任务"

    return AgentProposal(
        agent_id="planner",
        persona=persona,
        action="create_plan",
        summary=summary[:160],
        plan_draft=plan if isinstance(plan, dict) else None,
        user_options=list(resp.user_options or []),
        blackboard_entries=list(resp.blackboard_entries or []),
        output_patch={
            k: v
            for k, v in (resp.output or {}).items()
            if k != "plan"
        },
        status_hint=resp.status.value if hasattr(resp.status, "value") else str(resp.status),
        message_hint=resp.message,
        requires_approval=bool(resp.requires_approval),
    )


def propose_arbitrate(state: CollabState) -> AgentProposal:
    resp = arbitrate_worker.handle_arbitrate(state.request)
    persona = PERSONA["planner"]["name"]
    plan = (resp.output or {}).get("plan")
    return AgentProposal(
        agent_id="planner",
        persona=persona,
        action="arbitrate",
        summary=(resp.message or "已按用户选项更新计划")[:160],
        plan_draft=plan if isinstance(plan, dict) else None,
        output_patch={k: v for k, v in (resp.output or {}).items() if k != "plan"},
        status_hint=resp.status.value if hasattr(resp.status, "value") else str(resp.status),
        message_hint=resp.message,
        requires_approval=bool(resp.requires_approval),
    )
