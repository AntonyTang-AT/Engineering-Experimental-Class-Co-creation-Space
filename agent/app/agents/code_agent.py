"""码小助：代码上下文专属助教。"""

from __future__ import annotations

from app.agents.base import PERSONA, AgentProposal, CollabState
from app.workers import tutor as tutor_worker


def has_code_context(state: CollabState) -> bool:
    data = state.request.input or {}
    if str(data.get("code") or "").strip():
        return True
    if str(data.get("stderr") or "").strip():
        return True
    subject = str(data.get("subject") or "")
    hard = state.request.user_profile.constraints.hard
    for item in hard:
        if item.startswith("subject="):
            subject = item.split("=", 1)[1].strip() or subject
    return subject == "cs" and bool(str(data.get("message") or data.get("text") or "").strip())


def propose_code_help(state: CollabState) -> AgentProposal:
    # 确保 tutor worker 走代码系统提示：补 subject=cs
    data = dict(state.request.input or {})
    data.setdefault("subject", "cs")
    state.request.input = data
    resp = tutor_worker.handle_tutor_dialog(state.request)
    reply = (resp.output or {}).get("reply")
    card = (resp.output or {}).get("card")
    return AgentProposal(
        agent_id="code",
        persona=PERSONA["code"]["name"],
        action="code_help",
        summary=(resp.message or "已生成代码助教回复")[:160],
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
