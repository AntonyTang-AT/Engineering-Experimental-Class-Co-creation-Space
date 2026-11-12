"""教学主脑：温题（质疑）+ 析因（复盘）+ 数理对话。"""

from __future__ import annotations

from app.agents.base import PERSONA, AgentProposal, CollabState
from app.workers import evaluator as evaluator_worker
from app.workers import tutor as tutor_worker


def propose_challenge(state: CollabState) -> AgentProposal:
    resp = evaluator_worker.handle_challenge(state.request)
    card = (resp.output or {}).get("card")
    return AgentProposal(
        agent_id="tutor",
        persona=PERSONA["tutor"]["name"],
        action="challenge",
        summary=(resp.message or "已发起结构化质疑")[:160],
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


def propose_metacognitive(state: CollabState) -> AgentProposal:
    resp = evaluator_worker.handle_metacognitive_feedback(state.request)
    card = (resp.output or {}).get("card")
    return AgentProposal(
        agent_id="analyst",
        persona=PERSONA["analyst"]["name"],
        action="metacognitive_feedback",
        summary=(resp.message or "已生成元认知复盘")[:160],
        card=card if isinstance(card, dict) else None,
        output_patch={
            k: v for k, v in (resp.output or {}).items() if k not in {"card"}
        },
        status_hint=resp.status.value if hasattr(resp.status, "value") else str(resp.status),
        message_hint=resp.message,
        requires_approval=bool(resp.requires_approval),
    )


def propose_tutor_dialog(state: CollabState) -> AgentProposal:
    resp = tutor_worker.handle_tutor_dialog(state.request)
    reply = (resp.output or {}).get("reply")
    card = (resp.output or {}).get("card")
    return AgentProposal(
        agent_id="tutor",
        persona=PERSONA["tutor"]["name"],
        action="tutor_dialog",
        summary=(resp.message or "已生成学习建议")[:160],
        reply=str(reply) if reply is not None else None,
        card=card if isinstance(card, dict) else None,
        output_patch={
            k: v
            for k, v in (resp.output or {}).items()
            if k not in {"reply", "card"}
        },
        status_hint=resp.status.value if hasattr(resp.status, "value") else str(resp.status),
        message_hint=resp.message,
        requires_approval=bool(resp.requires_approval),
    )


def propose_remediation_note(state: CollabState) -> AgentProposal | None:
    """计划流水线中：若有错因策略，由析因补一句复盘建议。"""
    meta = (state.output or {}).get("error_strategy")
    if not isinstance(meta, dict) or not meta.get("known"):
        return None
    tag = meta.get("error_tag") or "general"
    summary = f"错因 {tag} 已写入补救任务，建议今晚先做短复盘再拔高。"
    return AgentProposal(
        agent_id="analyst",
        persona=PERSONA["analyst"]["name"],
        action="remediation_note",
        summary=summary,
        output_patch={"pedagogy_note": summary},
    )
