"""学习对话 / 代码助教：真实调用 DeepSeek；失败时规则兜底。"""

from __future__ import annotations

from typing import Any

from app.llm import chat, is_configured
from app.schemas.request import AgentRequest
from app.schemas.response import AgentResponse, ResponseStatus

_SYSTEM = """你是「知序」学习助手，服务大一高数/大物/计概学生。
要求：
1. 用简洁中文，分点说明，不要长篇空洞鸡汤。
2. 侧重学习方法、计划取舍、错因复盘、概念卡点；不要替用户完成整份作业。
3. 若题目缺条件，明确指出缺什么，建议先补假设再算。
4. 计概/编程问题可给思路与易错点，不要大段粘贴完整可交作业代码。
5. 若用户提到时间不够，提醒可去「学习计划」做三选一确认。
6. 回答控制在 250 字以内。"""

_CODE_SYSTEM = """你是「知序」计概代码小助教，帮助学生看 Pyodide 沙箱报错与自测失败。
要求：
1. 用简洁中文，先给结论再给 1～3 条可执行修改建议。
2. 结合题面、源码、stderr/stdout、本地规则提示作答；指出高概率逻辑错（如不该 .lower()）。
3. 不要输出整份可直接交作业的完整正确代码；最多给 3～5 行关键片段。
4. 若自测失败但无异常，对照样例说明返回值可能错在哪。
5. 回答控制在 220 字以内。"""


def _fallback(user_text: str, subject: str) -> str:
    return (
        f"我先用规则模式回复（智能服务暂不可用）。"
        f"你问的是「{user_text[:40]}…」相关问题。"
        f"建议：先明确科目（当前侧重视角：{subject}）→ 写出已知/未知 → "
        f"再到练习中心做 1 道同类题验证。计划若超时，请先去计划页确认今晚安排。"
    )


def _code_context_block(data: dict[str, Any]) -> str | None:
    code = str(data.get("code") or "").strip()
    stderr = str(data.get("stderr") or "").strip()
    stdout = str(data.get("stdout") or "").strip()
    statement = str(data.get("statement") or data.get("exercise_statement") or "").strip()
    title = str(data.get("exercise_title") or data.get("title") or "").strip()
    hint = str(data.get("hint") or "").strip()
    local_hints = data.get("local_hints") or data.get("logic_tips") or []
    check_passed = data.get("check_passed")
    if not any([code, stderr, statement, title]):
        return None

    bits = ["【代码助教上下文】"]
    if title:
        bits.append(f"题目：{title}")
    if statement:
        bits.append(f"题面：{statement[:500]}")
    if hint:
        bits.append(f"题内提示：{hint[:200]}")
    if check_passed is True:
        bits.append("自测状态：通过")
    elif check_passed is False:
        bits.append("自测状态：未通过")
    if isinstance(local_hints, list) and local_hints:
        bits.append("本地规则已捕捉到的线索：")
        bits.extend(f"- {str(x)}" for x in local_hints[:5])
    if code:
        bits.append("学生源码：\n```python\n" + code[:1800] + "\n```")
    if stderr:
        bits.append("stderr（已精简）：\n" + stderr[:800])
    if stdout:
        bits.append("stdout：\n" + stdout[:400])
    return "\n".join(bits)


def handle_tutor_dialog(req: AgentRequest) -> AgentResponse:
    data = req.input or {}
    user_text = str(data.get("message") or data.get("text") or "").strip()
    if not user_text:
        return AgentResponse(
            request_id=req.request_id,
            task_id=req.task_id,
            status=ResponseStatus.failed,
            message="tutor_dialog 需要 input.message",
            output={"reply": None},
        )

    subject = "math"
    for item in req.user_profile.constraints.hard:
        if item.startswith("subject="):
            subject = item.split("=", 1)[1].strip() or subject
    subject = str(data.get("subject") or subject)

    code_block = _code_context_block(data)
    is_code = bool(code_block) or subject == "cs"

    context_bits: list[str] = [
        f"学科侧重点：{subject}",
        f"场景：{req.scenario.value}",
    ]
    if req.resource_refs:
        labels = [r.label or r.id for r in req.resource_refs[:4]]
        context_bits.append("相关知识点：" + "、".join(labels))
    focus = data.get("focus")
    if focus:
        context_bits.append(f"学生关注：{focus}")
    weak = data.get("weak_points")
    if isinstance(weak, list) and weak:
        context_bits.append("薄弱点：" + "；".join(str(x) for x in weak[:4]))
    if code_block:
        context_bits.append(code_block)

    user_payload = "\n".join(context_bits) + f"\n\n学生提问：{user_text}"
    system = _CODE_SYSTEM if is_code and code_block else _SYSTEM

    llm_meta: dict[str, Any] = {
        "configured": is_configured(),
        "used_llm": False,
        "mode": "code_tutor" if code_block else "tutor_dialog",
    }
    result = chat(system=system, user=user_payload, temperature=0.35, max_tokens=600)
    if result.used_llm:
        reply = result.text
        llm_meta.update({"used_llm": True, "model": result.model})
        message = (
            "已生成代码助教回复"
            if code_block
            else "已生成学习建议"
        )
        status = ResponseStatus.ok
    else:
        # 代码场景优先交给前端本地规则兜底；这里仍给通用兜底
        reply = _fallback(user_text, subject)
        llm_meta.update({"used_llm": False, "error": result.error})
        message = "智能服务暂不可用，已用规则兜底"
        status = ResponseStatus.ok

    return AgentResponse(
        request_id=req.request_id,
        task_id=req.task_id,
        status=status,
        message=message,
        output={
            "reply": reply,
            "card": {
                "type": "tutor_dialog",
                "title": "代码助教" if code_block else "学习对话",
                "message": reply,
            },
            "llm": llm_meta,
        },
        requires_approval=False,
    )
