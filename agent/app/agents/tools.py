"""确定性工具：审计 / 校验 / 黑板构造（非 Agent）。"""

from __future__ import annotations

from typing import Any

from app.blackboard.entries import challenge_entry, conflict_entry, intervention_entry
from app.rules.constraints import parse_daily_minutes
from app.rules.plan_audit import audit_plan
from app.schemas.request import AgentRequest
from app.schemas.response import BlackboardEntry
from app.workers import verifier as verifier_worker


def tool_parse_daily_minutes(req: AgentRequest) -> int:
    return parse_daily_minutes(req.user_profile.constraints.hard)


def tool_audit_plan(
    plan: dict[str, Any],
    *,
    daily_minutes: int,
    force_conflict: bool = False,
) -> Any:
    return audit_plan(plan, daily_minutes=daily_minutes, force_conflict=force_conflict)


def tool_verify_answer(req: AgentRequest) -> Any:
    return verifier_worker.handle_verify_answer(req)


def tool_conflict_entry(
    *,
    entry_id: str,
    summary: str,
    evidence_refs: list[str] | None = None,
) -> BlackboardEntry:
    return conflict_entry(entry_id=entry_id, summary=summary, evidence_refs=evidence_refs)


def tool_challenge_entry(
    *,
    entry_id: str,
    summary: str,
    evidence_refs: list[str] | None = None,
) -> BlackboardEntry:
    return challenge_entry(entry_id=entry_id, summary=summary, evidence_refs=evidence_refs)


def tool_intervention_entry(
    *,
    entry_id: str,
    summary: str,
    evidence_refs: list[str] | None = None,
) -> BlackboardEntry:
    return intervention_entry(
        entry_id=entry_id, summary=summary, evidence_refs=evidence_refs
    )


def append_thread_from_trace(
    entry: BlackboardEntry,
    trace_rows: list[dict[str, str]],
) -> BlackboardEntry:
    """把协作 trace 写成传话行（若尚无传话）。"""
    refs = list(entry.evidence_refs or [])
    if any(str(r).startswith("传话") for r in refs):
        return entry
    thread = [
        f"传话 · {row.get('persona') or row.get('agent_id')}:{row.get('summary')}"
        for row in trace_rows
        if row.get("summary")
    ]
    entry.evidence_refs = [*thread, *refs]
    return entry
