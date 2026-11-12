"""命名协作流水线。"""

from __future__ import annotations

from app.agents import coach_agent, code_agent, pedagogy_agent, planner_agent
from app.agents.base import CollabState
from app.orchestrator.runtime import new_state, run_steps, to_response
from app.schemas.request import AgentRequest
from app.schemas.response import AgentResponse


def pipeline_plan_negotiate(req: AgentRequest) -> AgentResponse:
    state = new_state(req, pipeline="plan_negotiate", goal="排出可执行计划")

    def step_planner(s: CollabState):
        return planner_agent.propose_create_plan(s)

    def step_coach(s: CollabState):
        return coach_agent.propose_load_opinion(s)

    def step_analyst(s: CollabState):
        return pedagogy_agent.propose_remediation_note(s)

    run_steps(state, [step_planner, step_coach, step_analyst])
    if state.load_opinion and state.status == "conflict":
        advice = state.load_opinion.get("advice")
        if advice and advice not in state.message:
            state.message = f"{state.message}（安节：{advice}）"
    return to_response(state)


def pipeline_teach_loop(req: AgentRequest, *, mode: str) -> AgentResponse:
    state = new_state(req, pipeline="teach_loop", goal=mode)

    def step_main(s: CollabState):
        if mode == "challenge":
            return pedagogy_agent.propose_challenge(s)
        if mode == "metacognitive_feedback":
            return pedagogy_agent.propose_metacognitive(s)
        return pedagogy_agent.propose_tutor_dialog(s)

    def step_coach(s: CollabState):
        return coach_agent.maybe_pace_nudge(s)

    run_steps(state, [step_main, step_coach])
    if state.output.get("pace_nudge") and state.reply:
        state.reply = f"{state.reply}\n\n（节奏提醒）{state.output['pace_nudge']}"
        state.output["reply"] = state.reply
        if isinstance(state.card, dict):
            state.card = {**state.card, "message": state.reply}
            state.output["card"] = state.card
    return to_response(state)


def pipeline_code_help(req: AgentRequest) -> AgentResponse:
    state = new_state(req, pipeline="code_help", goal="代码辅导")
    run_steps(state, [code_agent.propose_code_help])
    return to_response(state)


def pipeline_intervention(req: AgentRequest) -> AgentResponse:
    state = new_state(req, pipeline="intervention", goal="节奏干预")
    run_steps(state, [coach_agent.propose_intervention])
    return to_response(state)


def resolve_tutor_pipeline(req: AgentRequest) -> AgentResponse:
    state_probe = new_state(req, pipeline="probe")
    if code_agent.has_code_context(state_probe):
        return pipeline_code_help(req)
    return pipeline_teach_loop(req, mode="tutor_dialog")


def run_collaborate(req: AgentRequest) -> AgentResponse:
    name = str((req.input or {}).get("pipeline") or "").strip()
    if name == "plan_negotiate":
        return pipeline_plan_negotiate(req)
    if name == "teach_loop":
        mode = str((req.input or {}).get("mode") or "tutor_dialog")
        return pipeline_teach_loop(req, mode=mode)
    if name == "code_help":
        return pipeline_code_help(req)
    if name == "intervention":
        return pipeline_intervention(req)
    # 默认：按输入推断
    if (req.input or {}).get("option_id"):
        # 非协作仲裁，交回失败提示
        return pipeline_plan_negotiate(req)
    if code_agent.has_code_context(new_state(req, pipeline="probe")):
        return pipeline_code_help(req)
    if (req.input or {}).get("question") or (req.input or {}).get("claim"):
        return pipeline_teach_loop(req, mode="challenge")
    return pipeline_teach_loop(req, mode="tutor_dialog")
