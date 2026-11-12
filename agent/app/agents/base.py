"""多 Agent 共享状态与提案协议。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.schemas.request import AgentRequest
from app.schemas.response import BlackboardEntry, UserOption


PERSONA = {
    "planner": {"id": "planner", "name": "程计", "title": "计划助手"},
    "tutor": {"id": "tutor", "name": "温题", "title": "习题助教"},
    "analyst": {"id": "analyst", "name": "析因", "title": "学情分析"},
    "coach": {"id": "coach", "name": "安节", "title": "节奏教练"},
    "code": {"id": "code", "name": "码小助", "title": "代码助教"},
}


@dataclass
class TraceItem:
    agent_id: str
    persona: str
    action: str
    summary: str

    def to_dict(self) -> dict[str, str]:
        return {
            "agent_id": self.agent_id,
            "persona": self.persona,
            "action": self.action,
            "summary": self.summary,
        }


@dataclass
class AgentProposal:
    """Agent 向编排器提交的结构化提案（禁止纯闲聊互 @）。"""

    agent_id: str
    persona: str
    action: str
    summary: str
    plan_draft: dict[str, Any] | None = None
    card: dict[str, Any] | None = None
    reply: str | None = None
    user_options: list[UserOption] = field(default_factory=list)
    blackboard_entries: list[BlackboardEntry] = field(default_factory=list)
    output_patch: dict[str, Any] = field(default_factory=dict)
    status_hint: str | None = None
    message_hint: str | None = None
    requires_approval: bool | None = None
    load_opinion: dict[str, Any] | None = None


@dataclass
class CollabState:
    request: AgentRequest
    goal: str = ""
    pipeline: str = ""
    plan_draft: dict[str, Any] | None = None
    card: dict[str, Any] | None = None
    reply: str | None = None
    user_options: list[UserOption] = field(default_factory=list)
    blackboard_entries: list[BlackboardEntry] = field(default_factory=list)
    output: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"
    message: str = ""
    requires_approval: bool = False
    trace: list[TraceItem] = field(default_factory=list)
    agents_involved: list[str] = field(default_factory=list)
    load_opinion: dict[str, Any] | None = None

    def record(self, proposal: AgentProposal) -> None:
        if proposal.agent_id not in self.agents_involved:
            self.agents_involved.append(proposal.agent_id)
        self.trace.append(
            TraceItem(
                agent_id=proposal.agent_id,
                persona=proposal.persona,
                action=proposal.action,
                summary=proposal.summary,
            )
        )
        if proposal.plan_draft is not None:
            self.plan_draft = proposal.plan_draft
            self.output["plan"] = proposal.plan_draft
        if proposal.card is not None:
            self.card = proposal.card
            self.output["card"] = proposal.card
        if proposal.reply is not None:
            self.reply = proposal.reply
            self.output["reply"] = proposal.reply
        if proposal.user_options:
            self.user_options = list(proposal.user_options)
        if proposal.blackboard_entries:
            self.blackboard_entries.extend(proposal.blackboard_entries)
        if proposal.output_patch:
            self.output.update(proposal.output_patch)
        if proposal.status_hint:
            self.status = proposal.status_hint
        if proposal.message_hint is not None:
            self.message = proposal.message_hint
        if proposal.requires_approval is not None:
            self.requires_approval = proposal.requires_approval
        if proposal.load_opinion is not None:
            self.load_opinion = proposal.load_opinion
            self.output["load_opinion"] = proposal.load_opinion

    def collaboration_payload(self) -> dict[str, Any]:
        return {
            "collaboration_trace": [t.to_dict() for t in self.trace],
            "agents_involved": list(self.agents_involved),
            "pipeline": self.pipeline,
        }
