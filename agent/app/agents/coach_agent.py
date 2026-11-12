"""安节：节奏干预 + 对计划草案的负荷意见。"""

from __future__ import annotations

from typing import Any

from app.agents.base import PERSONA, AgentProposal, CollabState
from app.workers import evaluator as evaluator_worker


def _max_day_minutes(plan: dict[str, Any] | None) -> int:
    if not plan:
        return 0
    tasks = plan.get("tasks") or []
    return max((int(t.get("minutes") or 0) for t in tasks), default=0)


def propose_load_opinion(state: CollabState) -> AgentProposal:
    """读程计草案，给出负荷意见（结构化，供编排器写入 output）。"""
    plan = state.plan_draft or (state.output or {}).get("plan")
    budget = int((plan or {}).get("daily_minutes_budget") or 0)
    peak = _max_day_minutes(plan if isinstance(plan, dict) else None)
    conflict = state.status == "conflict"

    if conflict or (budget and peak > budget):
        opinion = {
            "overload": True,
            "peak_minutes": peak,
            "budget": budget,
            "advice": "今晚峰值已顶破预算，建议用户三选一：加时 / 降深度 / 缩目标。",
        }
        summary = "负荷偏高：峰值超时，建议保留三选一而不是硬砍整晚。"
    elif peak >= max(40, int(budget * 0.85) if budget else 40):
        opinion = {
            "overload": False,
            "peak_minutes": peak,
            "budget": budget,
            "advice": "接近预算上限，拔高题可挪到状态更好的一天。",
        }
        summary = "负荷临界：可完成，但建议把拔高题后移。"
    else:
        opinion = {
            "overload": False,
            "peak_minutes": peak,
            "budget": budget,
            "advice": "负荷可接受，按草案执行即可。",
        }
        summary = "负荷可接受，同意按当前草案推进。"

    return AgentProposal(
        agent_id="coach",
        persona=PERSONA["coach"]["name"],
        action="load_review",
        summary=summary,
        load_opinion=opinion,
    )


def propose_intervention(state: CollabState) -> AgentProposal:
    resp = evaluator_worker.handle_proactive_intervention(state.request)
    card = (resp.output or {}).get("card")
    return AgentProposal(
        agent_id="coach",
        persona=PERSONA["coach"]["name"],
        action="proactive_intervention",
        summary=(resp.message or "已评估干预条件")[:160],
        card=card if isinstance(card, dict) else None,
        user_options=list(resp.user_options or []),
        blackboard_entries=list(resp.blackboard_entries or []),
        output_patch={
            k: v for k, v in (resp.output or {}).items() if k not in {"card"}
        },
        status_hint=resp.status.value if hasattr(resp.status, "value") else str(resp.status),
        message_hint=resp.message,
        requires_approval=bool(resp.requires_approval),
    )


def maybe_pace_nudge(state: CollabState) -> AgentProposal | None:
    """教学流水线尾声：仅在断练/过载信号时补一句节奏提醒。"""
    jump = int(state.request.demo.time_jump_days or 0)
    load = (state.request.trace_snapshot or {}).get("load_signals") or {}
    overload = bool(load.get("overload")) or jump >= 2
    if not overload:
        return None
    summary = (
        f"检测到节奏风险（time_jump={jump}），建议先完成 15 分钟热身再加深。"
    )
    return AgentProposal(
        agent_id="coach",
        persona=PERSONA["coach"]["name"],
        action="pace_nudge",
        summary=summary,
        output_patch={"pace_nudge": summary},
    )
