"""多 Agent 流水线验收。"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_reports_multi_agent_runtime() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["runtime"]["mode"] == "multi_agent"
    assert "planner" in body["runtime"]["agents"]


def test_create_plan_conflict_involves_planner_and_coach() -> None:
    payload = {
        "request_id": "ma_plan_1",
        "task_id": "ma_plan_1",
        "scenario": "final_review",
        "intent": "create_plan",
        "user_profile": {
            "user_id": "u1",
            "constraints": {"hard": ["daily_minutes<=45", "subject=math"], "soft": []},
        },
        "input": {"goal": "期末过线", "days_left": 5},
        "resource_refs": [
            {"type": "knowledge", "id": "math.limit", "label": "极限"},
            {"type": "knowledge", "id": "math.derivative", "label": "导数"},
        ],
        "demo": {"force_conflict": True},
    }
    r = client.post("/agent/v1/invoke", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "conflict"
    out = body["output"]
    assert out.get("pipeline") == "plan_negotiate"
    involved = out.get("agents_involved") or []
    assert "planner" in involved
    assert "coach" in involved
    trace = out.get("collaboration_trace") or []
    personas = {t.get("persona") for t in trace}
    assert "程计" in personas
    assert "安节" in personas
    assert out.get("load_opinion")


def test_challenge_teach_loop_trace() -> None:
    payload = {
        "request_id": "ma_chal_1",
        "task_id": "ma_chal_1",
        "scenario": "catch_up",
        "intent": "challenge",
        "user_profile": {
            "user_id": "u1",
            "constraints": {"hard": ["subject=math"], "soft": []},
        },
        "input": {
            "question": {
                "question_id": "q1",
                "stem": "求极限但未说明单侧与定义域",
                "answer": "",
                "assumptions": [],
                "knowledge_ids": ["math.limit"],
                "error_tags": ["undefined_assumption"],
            }
        },
    }
    r = client.post("/agent/v1/invoke", json=payload)
    assert r.status_code == 200
    body = r.json()
    out = body["output"]
    assert out.get("pipeline") == "teach_loop"
    assert "tutor" in (out.get("agents_involved") or [])
    assert any(t.get("persona") == "温题" for t in (out.get("collaboration_trace") or []))


def test_code_help_only_activates_code_agent() -> None:
    payload = {
        "request_id": "ma_code_1",
        "task_id": "ma_code_1",
        "scenario": "catch_up",
        "intent": "tutor_dialog",
        "user_profile": {
            "user_id": "u_cs",
            "constraints": {"hard": ["subject=cs"], "soft": []},
        },
        "input": {
            "message": "自测为啥没过",
            "subject": "cs",
            "code": "def f(s):\n    return s.lower()\n",
            "stderr": "AssertionError",
            "check_passed": False,
            "local_hints": ["不该 lower"],
        },
    }
    r = client.post("/agent/v1/invoke", json=payload)
    assert r.status_code == 200
    body = r.json()
    out = body["output"]
    assert out.get("pipeline") == "code_help"
    assert out.get("agents_involved") == ["code"]
    assert any(t.get("persona") == "码小助" for t in (out.get("collaboration_trace") or []))


def test_collaborate_intent_plan_negotiate() -> None:
    payload = {
        "request_id": "ma_col_1",
        "task_id": "ma_col_1",
        "scenario": "final_review",
        "intent": "collaborate",
        "user_profile": {
            "user_id": "u1",
            "constraints": {"hard": ["daily_minutes<=45", "subject=math"], "soft": []},
        },
        "input": {
            "pipeline": "plan_negotiate",
            "goal": "期末过线",
            "days_left": 5,
        },
        "resource_refs": [
            {"type": "knowledge", "id": "math.limit", "label": "极限"},
        ],
        "demo": {"force_conflict": True},
    }
    r = client.post("/agent/v1/invoke", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["output"].get("pipeline") == "plan_negotiate"
    assert "planner" in (body["output"].get("agents_involved") or [])
