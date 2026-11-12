"""多 Agent 执行引擎：共享 CollabState，汇总 AgentResponse。"""

from __future__ import annotations

from typing import Callable

from app.agents.base import AgentProposal, CollabState
from app.agents.tools import append_thread_from_trace
from app.schemas.request import AgentRequest
from app.schemas.response import AgentResponse, ResponseStatus


StepFn = Callable[[CollabState], AgentProposal | None]


def new_state(req: AgentRequest, *, pipeline: str, goal: str = "") -> CollabState:
    return CollabState(
        request=req,
        goal=goal or str((req.input or {}).get("goal") or req.intent),
        pipeline=pipeline,
    )


def run_steps(state: CollabState, steps: list[StepFn]) -> CollabState:
    for step in steps:
        proposal = step(state)
        if proposal is None:
            continue
        state.record(proposal)
    return state


def enrich_blackboard_with_trace(state: CollabState) -> None:
    if not state.blackboard_entries or not state.trace:
        return
    trace_rows = [t.to_dict() for t in state.trace]
    updated = []
    for entry in state.blackboard_entries:
        updated.append(append_thread_from_trace(entry, trace_rows))
    state.blackboard_entries = updated


def to_response(state: CollabState) -> AgentResponse:
    enrich_blackboard_with_trace(state)
    output = dict(state.output)
    output.update(state.collaboration_payload())

    try:
        status = ResponseStatus(state.status)
    except ValueError:
        status = ResponseStatus.ok

    return AgentResponse(
        request_id=state.request.request_id,
        task_id=state.request.task_id,
        status=status,
        message=state.message
        or (f"多智能体流水线 {state.pipeline} 已完成"),
        output=output,
        blackboard_entries=list(state.blackboard_entries),
        user_options=list(state.user_options),
        requires_approval=bool(state.requires_approval),
    )
