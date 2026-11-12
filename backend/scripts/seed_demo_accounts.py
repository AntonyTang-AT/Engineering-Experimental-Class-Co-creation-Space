"""预置工试2501真实花名册与样例学习数据。

用法（在 backend/ 下）::

    python -m scripts.seed_demo_accounts

- 20 名真实学生：账号=学号，密码=学号后六位，仅存姓名
- 样例：张思睿（高数计划冲突）、唐铭鑫（大物跟课质疑）
- 保留 admin
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import delete, select  # noqa: E402

from app.db.models import AiCallLog, Attempt, BlackboardEntry, Plan, User  # noqa: E402
from app.db.session import SessionLocal, init_db  # noqa: E402
from app.services.security import hash_password  # noqa: E402

ROSTER_PATH = BACKEND_ROOT / "data" / "cohort" / "roster_2501.json"
ADMIN_PASSWORD = "admin"

SAMPLE_ZHANG = "202593020403"  # 张思睿 · 高数
SAMPLE_WANG = "202593020409"  # 汪佳文 · 大物
SAMPLE_HAO = "202507020403"  # 郝梓博 · 计概
SAMPLE_TANG = "202593020126"  # 唐铭鑫 · 科研竞赛
UID_ZHANG = f"u_{SAMPLE_ZHANG}"
UID_WANG = f"u_{SAMPLE_WANG}"
UID_HAO = f"u_{SAMPLE_HAO}"
UID_TANG = f"u_{SAMPLE_TANG}"
UID_ADMIN = "u_admin"

MATH_OPTIONS = [
    {"id": "extend_time", "label": "每天多挤出 20 分钟"},
    {"id": "reduce_depth", "label": "证明改成例题精读，先保过线"},
    {"id": "adjust_goal", "label": "连续性章节挪到周末集中看"},
]


def _load_roster() -> dict:
    return json.loads(ROSTER_PATH.read_text(encoding="utf-8"))


def _password_for_sid(student_id: str) -> str:
    return student_id[-6:]


def _uid_for_sid(student_id: str) -> str:
    return f"u_{student_id}"


def _task(
    day: int,
    action: str,
    obj: str,
    minutes: int,
    criteria: str,
    load: str,
    knowledge_id: str,
    subject: str,
    error_tag: str | None = None,
    status: str = "todo",
) -> dict:
    item = {
        "day": day,
        "action": action,
        "object": obj,
        "minutes": minutes,
        "completion_criteria": criteria,
        "load": load,
        "knowledge_ids": [knowledge_id],
        "subject": subject,
        "status": status,
    }
    if error_tag:
        item["error_tag"] = error_tag
    return item



def _upsert_user(db, spec: dict) -> User:
    user = db.scalar(select(User).where(User.username == spec["username"]))
    if user is None:
        user = db.get(User, spec["id"])
    if user is None:
        user = User(id=spec["id"])
        db.add(user)
    user.id = spec["id"]
    user.username = spec["username"]
    user.display_name = spec["display_name"]
    user.role = spec["role"]
    user.password_hash = hash_password(spec["password"])
    user.demo_time_jump_days = int(spec.get("demo_time_jump_days", 0) or 0)
    return user



def _upsert_plan(db, user_id: str, plan: dict) -> None:
    row = db.scalar(select(Plan).where(Plan.user_id == user_id))
    payload = json.dumps(plan, ensure_ascii=False)
    if row is None:
        db.add(Plan(user_id=user_id, snapshot=payload))
    else:
        row.snapshot = payload



def _upsert_bb(db, entry_id: str, fields: dict) -> None:
    bb = db.get(BlackboardEntry, entry_id)
    if bb is None:
        db.add(BlackboardEntry(id=entry_id, **fields))
    else:
        for key, value in fields.items():
            setattr(bb, key, value)



def _reset_user_learning_state(db, user_id: str) -> None:
    """清掉该账号演示过程中产生的脏黑板 / 额外作答，再由 seed 写回基线。"""
    db.execute(delete(BlackboardEntry).where(BlackboardEntry.user_id == user_id))
    db.execute(delete(Attempt).where(Attempt.user_id == user_id))
    db.execute(delete(AiCallLog).where(AiCallLog.user_id == user_id))
    db.flush()
    db.expire_all()



def _replace_attempts(db, user_id: str, rows: list[dict]) -> None:
    db.execute(delete(Attempt).where(Attempt.user_id == user_id))
    for row in rows:
        db.add(Attempt(**row))



def _ensure_ai_log(
    db,
    *,
    user_id: str,
    intent: str,
    request_id: str,
    status: str,
    response: dict,
) -> None:
    exists = db.scalar(select(AiCallLog).where(AiCallLog.request_id == request_id))
    if exists is not None:
        return
    db.add(
        AiCallLog(
            user_id=user_id,
            intent=intent,
            request_id=request_id,
            status=status,
            request_body="{}",
            response_body=json.dumps(response, ensure_ascii=False),
        )
    )



def _seed_math_conflict(db, user_id: str) -> None:
    """张思睿：高数期末冲刺，今晚计划超时需调整。"""
    _reset_user_learning_state(db, user_id)
    plan = {
        "scenario": "final_review",
        "goal": "11 月 22 日高数期末过线，先打通极限与连续",
        "daily_minutes_budget": 45,
        "days_left": 12,
        "tasks": [
            _task(
                1,
                "回看",
                "极限定义与邻域语言",
                20,
                "用自己的话讲清 ε-δ，并写出 2 个反例",
                "low",
                "math.a1.ch02",
                "math",
                status="done",
            ),
            _task(
                2,
                "练习",
                "第一重要极限与夹逼",
                40,
                "完成 4 道基础题，每题标出放缩方向",
                "medium",
                "math.a1.ch02",
                "math",
                error_tag="formula_misuse",
                status="done",
            ),
            _task(
                3,
                "整理",
                "函数连续性证明（综合）",
                60,
                "整理证明卡片并标注每一步依据",
                "high",
                "math.a1.ch04",
                "math",
                status="blocked",
            ),
            _task(
                4,
                "练习",
                "无穷小比较常见型",
                35,
                "完成 3 道填空，错题写回错因本",
                "medium",
                "math.a1.ch02",
                "math",
            ),
            _task(
                5,
                "回看",
                "连续与间断分类小结",
                25,
                "画一张分类表，覆盖可去、跳跃、无穷间断",
                "low",
                "math.a1.ch04",
                "math",
            ),
            _task(
                6,
                "模拟",
                "极限综合小测 20 分钟",
                30,
                "限时完成 5 题，正确率目标 ≥ 70%",
                "high",
                "math.a1.ch02",
                "math",
            ),
            _task(
                7,
                "复盘",
                "错题本极限专题",
                30,
                "把本周错题按公式误用 / 放缩方向归类",
                "medium",
                "math.a1.ch02",
                "math",
            ),
        ],
        "_demo": {
            "plan_status": "conflict",
            "plan_message": "今晚只剩 45 分钟，但「连续性证明」需要约 60 分钟，需要先决定怎么改今晚安排。",
            "user_options": MATH_OPTIONS,
            "selected_option_id": "reduce_depth",
            "show_intervention": False,
            "setup": {
                "mode": "final_review",
                "subject": "math",
                "dailyMinutes": 45,
                "examDate": "2026-11-22",
                "chapter": "高等数学 A1 · 第 2–4 章",
            },
            "persona": {
                "real_name": "张思睿",
                "major": "工科试验班（人工智能类）· 2501",
                "course": "高等数学 A1",
                "semester": "大一上 · 距期末 12 天",
                "focus": "极限计算已基本稳住，连续性证明还卡住",
                "weak_points": [
                    "放缩方向容易写反",
                    "见到复杂分式就想直接上洛必达",
                    "证明题缺少「先写定义再拆步骤」的习惯",
                ],
                "next_action": "先处理今晚超时的安排，再继续极限综合小测",
                "next_path": "/plan",
                "chat_greeting": "思睿你好。距离高数期末还有 12 天，今晚的连续性证明看起来会超出你设定的 45 分钟。要不要先一起看看怎么改今晚的安排？",
                "quick_asks": [
                    "今晚时间不够怎么办",
                    "我夹逼定理哪里容易错",
                    "帮我安排明日复习",
                    "最近正确率怎么样",
                ],
                "recent_days": [
                    {"when": "前天 20:10", "text": "极限定义笔记完成，自测 2/2"},
                    {"when": "昨天 21:05", "text": "夹逼基础题 4 道，错 1 道（放缩方向）"},
                    {"when": "今天 15:40", "text": "做到连续性证明第 2 步后暂停，标记「稍后再看」"},
                ],
                "mastery": [
                    {"label": "极限定义", "value": 82},
                    {"label": "夹逼定理", "value": 58},
                    {"label": "重要极限", "value": 74},
                    {"label": "连续性证明", "value": 41},
                ],
                "question_notes": [
                    {
                        "question_id": "math_a1c01_0001",
                        "title": "求 lim(x→0) (sin 3x − 3x)/x³",
                    },
                    {
                        "question_id": "math_a1c01_0002",
                        "title": "用夹逼证明 lim(x→0) x² sin(1/x) = 0",
                    },
                    {
                        "question_id": "math_a1c02_0001",
                        "title": "讨论 f(x)=|x|/x 在 x=0 的连续性",
                    },
                    {
                        "question_id": "math_a1c02_0002",
                        "title": "无穷小比较：sin x 与 x − x³/6",
                    },
                    {
                        "question_id": "math_a1c03_0001",
                        "title": "分段函数连续条件填空",
                    },
                ],
                "materials_focus": "教材第 2 章极限 + 课件例题 3、5",
            },
        },
    }
    _upsert_plan(db, user_id, plan)
    _upsert_bb(
        db,
        "bb_seed_math_conflict",
        {
            "user_id": user_id,
            "type": "conflict",
            "summary": "今晚「连续性证明」约需 60 分钟，超过你设定的每日 45 分钟",
            "severity": "high",
            "evidence_refs": json.dumps(
                [
                    "传话 · 程计：第 3 天「连续性证明」估时 60 分钟，已经顶破每日 45 分钟预算。",
                    "传话 · 安节：别直接砍整晚任务，给三个选项——压缩证明 / 顺延一天 / 临时加时。",
                    "传话 · 析因：记下这次拍板，下周排期避开同类塞车。",
                    "依据 · 第 3 天「连续性证明」约 60 分钟",
                    "约束 · 每日可用时间 ≤ 45 分钟",
                    "建议动作 · 打开学习计划，选择压缩证明或顺延",
                ],
                ensure_ascii=False,
            ),
            "status": "open",
            "resolution": None,
        },
    )
    _upsert_bb(
        db,
        "bb_seed_math_note",
        {
            "user_id": user_id,
            "type": "stage_conclusion",
            "summary": "极限计算部分可暂视为过线水平，下一周重点应放在证明书写",
            "severity": "low",
            "evidence_refs": json.dumps(
                [
                    "传话 · 析因：近 5 次极限题正确率约 80%，可视为过线。",
                    "传话 · 程计：那下周排期把力气挪到证明书写。",
                    "依据 · 近 5 次极限题正确率约 80%",
                    "依据 · 证明题仍有 2 次中途放弃",
                    "建议动作 · 去学习轨迹确认强弱项",
                ],
                ensure_ascii=False,
            ),
            "status": "resolved",
            "resolution": json.dumps(
                {"action": "keep_focus", "note": "已将证明题排到第 3、5 天"},
                ensure_ascii=False,
            ),
        },
    )
    # 历史协作：已处理的多轮传话，展示「不是只有当前待办」
    _upsert_bb(
        db,
        "bb_seed_math_hist_plan",
        {
            "user_id": user_id,
            "type": "hypothesis",
            "summary": "（历史）上周：先把夹逼题正确率拉到 70%，再碰连续性证明",
            "severity": "low",
            "evidence_refs": json.dumps(
                [
                    "传话 · 析因：夹逼近 3 次正确率只有 45%，证明再堆只会更慌。",
                    "传话 · 程计：那本周任务改成「夹逼热身 ×3 + 证明草稿 ×1」。",
                    "传话 · 温题：我准备两道夹逼变式，做完打卡即可。",
                    "传话 · 安节：每天上限仍 45 分钟，证明草稿只留 15 分钟。",
                    "依据 · 上周夹逼正确率 45%",
                    "建议动作 · 已确认并写入计划",
                ],
                ensure_ascii=False,
            ),
            "status": "resolved",
            "resolution": json.dumps(
                {"action": "ack", "note": "已按假设调整上周计划"},
                ensure_ascii=False,
            ),
        },
    )
    _upsert_bb(
        db,
        "bb_seed_math_hist_verify",
        {
            "user_id": user_id,
            "type": "challenge",
            "summary": "（历史）洛必达连用三次被校验拦下：未核对条件",
            "severity": "medium",
            "evidence_refs": json.dumps(
                [
                    "传话 · 温题：草稿直接洛必达三次，条件写糊了，先别提交。",
                    "传话 · 析因：这是「公式误用」标签第二次出现。",
                    "传话 · 程计：把「洛必达条件检查」加进明日热身清单。",
                    "传话 · 安节：今天只订正这一题就收工，别再开新证明。",
                    "依据 · verify#failed · 洛必达条件缺失",
                    "建议动作 · 已订正并标记了解",
                ],
                ensure_ascii=False,
            ),
            "status": "resolved",
            "resolution": json.dumps(
                {"action": "ack", "note": "已补条件后重交"},
                ensure_ascii=False,
            ),
        },
    )
    _upsert_bb(
        db,
        "bb_seed_math_hist_pace",
        {
            "user_id": user_id,
            "type": "intervention",
            "summary": "（历史）期中后曾连续 3 天未练，助手们缩短了任务颗粒",
            "severity": "medium",
            "evidence_refs": json.dumps(
                [
                    "传话 · 安节：检测到 72 小时空白，先别用原计划硬扛。",
                    "传话 · 程计：今日只保留 15 分钟极限填空。",
                    "传话 · 温题：热身题已就绪，完成即可恢复节奏。",
                    "传话 · 析因：空白后第一天正确率通常偏低，不记入强弱项。",
                    "依据 · demo#time_jump",
                    "建议动作 · 已完成短热身",
                ],
                ensure_ascii=False,
            ),
            "status": "resolved",
            "resolution": json.dumps(
                {"action": "ack", "note": "已用短任务重启"},
                ensure_ascii=False,
            ),
        },
    )
    now = datetime.now(timezone.utc)
    _replace_attempts(
        db,
        user_id,
        [
            {
                "id": "att_math_001",
                "user_id": user_id,
                "question_id": "math_a1c01_0001",
                "answer": "直接洛必达三次，结果写成 -3/2",
                "is_correct": False,
                "error_tag": "公式误用",
                "duration_ms": 42000,
                "created_at": now - timedelta(days=2, hours=3),
            },
            {
                "id": "att_math_002",
                "user_id": user_id,
                "question_id": "math_a1c01_0002",
                "answer": "-x² ≤ x²sin(1/x) ≤ x²，夹逼得 0",
                "is_correct": True,
                "error_tag": None,
                "duration_ms": 28000,
                "created_at": now - timedelta(days=1, hours=5),
            },
            {
                "id": "att_math_003",
                "user_id": user_id,
                "question_id": "math_a1c02_0001",
                "answer": "左右极限不等，先不确定怎么写结论",
                "is_correct": None,
                "error_tag": "假设不清",
                "duration_ms": 15000,
                "created_at": now - timedelta(hours=6),
            },
            {
                "id": "att_math_004",
                "user_id": user_id,
                "question_id": "math_a1c02_0002",
                "answer": "等价替换 sin x ~ x",
                "is_correct": True,
                "error_tag": None,
                "duration_ms": 19000,
                "created_at": now - timedelta(days=1, hours=2),
            },
            {
                "id": "att_math_005",
                "user_id": user_id,
                "question_id": "math_a1c03_0001",
                "answer": "漏写 x→0+ 一侧条件",
                "is_correct": False,
                "error_tag": "边界条件",
                "duration_ms": 31000,
                "created_at": now - timedelta(hours=20),
            },
        ],
    )
    _ensure_ai_log(
        db,
        user_id=user_id,
        intent="create_plan",
        request_id="seed_math_cp",
        status="conflict",
        response={"status": "conflict", "message": "tonight overflow"},
    )



def _seed_physics_ok(db, user_id: str) -> None:
    """汪佳文：大物力学跟课，受力图漏了摩擦。"""
    _reset_user_learning_state(db, user_id)
    plan = {
        "scenario": "catch_up",
        "goal": "两周内跟上力学进度，受力分析不再丢条件",
        "daily_minutes_budget": 60,
        "days_left": 14,
        "tasks": [
            _task(
                1,
                "回看",
                "质点运动：位移、速度、加速度",
                25,
                "完成 1 页对照表，区分平均量与瞬时量",
                "low",
                "physics.mech.ch01",
                "physics",
                status="done",
            ),
            _task(
                2,
                "练习",
                "牛顿定律 · 三力平衡",
                45,
                "独立画 3 个受力图并写出方程",
                "medium",
                "physics.mech.ch02",
                "physics",
                error_tag="遗漏假设",
                status="done",
            ),
            _task(
                3,
                "练习",
                "斜面 + 摩擦力综合",
                50,
                "完成 2 道综合题，每题先列「是否计摩擦」",
                "high",
                "physics.mech.ch02",
                "physics",
                status="in_progress",
            ),
            _task(
                4,
                "回看",
                "课堂例题：木块相对传送带",
                30,
                "对照课件例 4，补齐相对运动分析",
                "medium",
                "physics.mech.ch02",
                "physics",
            ),
            _task(
                5,
                "整理",
                "受力分析检查清单",
                25,
                "整理「重力 / 弹力 / 摩擦 / 拉力」四步检查表",
                "low",
                "physics.mech.ch02",
                "physics",
            ),
            _task(
                6,
                "练习",
                "圆周运动入门衔接",
                40,
                "完成向心力基础题 3 道",
                "medium",
                "physics.mech.ch03",
                "physics",
            ),
        ],
        "_demo": {
            "plan_status": "ok",
            "plan_message": "本周力学计划已排好。上一道斜面题漏写摩擦力，建议先补检查清单再继续综合题。",
            "user_options": [],
            "selected_option_id": "",
            "show_intervention": False,
            "setup": {
                "mode": "catch_up",
                "subject": "physics",
                "dailyMinutes": 60,
                "examDate": "2026-12-18",
                "chapter": "大学物理 · 力学第 2 章",
            },
            "persona": {
                "real_name": "汪佳文",
                "major": "工科试验班（人工智能类）· 2501",
                "course": "大学物理 B",
                "semester": "大一上 · 力学进度落后约 1 周",
                "focus": "牛顿定律跟课补漏，受力图完整性",
                "weak_points": [
                    "斜面问题常默认光滑",
                    "静摩擦与滑动摩擦切换不敏感",
                    "相对地面 / 相对传送带参考系混用",
                ],
                "next_action": "处理「遗漏摩擦力」这条提醒，然后继续斜面综合题",
                "next_path": "/blackboard",
                "chat_greeting": "佳文，力学第 2 章你已经补回三力平衡。昨天那道斜面题漏了摩擦力，要不要先把检查清单过一遍再继续？",
                "quick_asks": [
                    "这道斜面为什么错了",
                    "今天该练哪一类题",
                    "摩擦力和法向怎么判断",
                    "我跟课程进度差多少",
                ],
                "recent_days": [
                    {"when": "大前天", "text": "运动学概念回看完成"},
                    {"when": "前天 19:30", "text": "三力平衡 3 题全对"},
                    {"when": "昨天 20:15", "text": "斜面综合第 1 题漏写摩擦，已标错"},
                    {"when": "今天 10:00", "text": "打开综合题第 2 题后暂缓提交"},
                ],
                "mastery": [
                    {"label": "运动学", "value": 78},
                    {"label": "牛顿定律", "value": 66},
                    {"label": "摩擦力", "value": 44},
                    {"label": "相对运动", "value": 52},
                ],
                "question_notes": [
                    {
                        "question_id": "physics_mech_0001",
                        "title": "匀加速直线运动位移公式选择",
                    },
                    {
                        "question_id": "physics_mech_0002",
                        "title": "悬挂重物三力平衡作图",
                    },
                    {
                        "question_id": "physics_mech_0003",
                        "title": "粗糙斜面上滑块的加速度",
                    },
                    {
                        "question_id": "physics_mech_0004",
                        "title": "传送带上木块相对滑动判定",
                    },
                    {
                        "question_id": "physics_mech_0005",
                        "title": "静摩擦达到最大值的临界角",
                    },
                ],
                "materials_focus": "大物课件第 2 章 + 作业 2.3、2.5",
            },
        },
    }
    _upsert_plan(db, user_id, plan)
    _upsert_bb(
        db,
        "bb_seed_physics_challenge",
        {
            "user_id": user_id,
            "type": "challenge",
            "summary": "斜面题草稿默认「光滑」，但题干写了摩擦系数 μ=0.2",
            "severity": "medium",
            "evidence_refs": json.dumps(
                [
                    "传话 · 温题：题干写了 μ=0.2，草稿却按光滑面算，先拦住提交。",
                    "传话 · 析因：近两次错题都和摩擦假设有关，值得钉在黑板上。",
                    "传话 · 安节：提醒语气放软——指出缺摩擦力，再送回练习页。",
                    "依据 · 题干写明 μ=0.2",
                    "依据 · 草稿按光滑面计算",
                    "建议动作 · 回练习页补全摩擦力后再提交",
                ],
                ensure_ascii=False,
            ),
            "status": "open",
            "resolution": None,
        },
    )
    _upsert_bb(
        db,
        "bb_seed_physics_oknote",
        {
            "user_id": user_id,
            "type": "hypothesis",
            "summary": "若先强制写出「接触面是否光滑」再列方程，漏力概率会下降",
            "severity": "low",
            "evidence_refs": json.dumps(
                [
                    "传话 · 析因：提出可验证假设——先写「光滑？/有摩擦？」再列式。",
                    "传话 · 温题：下次同类题我会按这条先检查再提示。",
                    "依据 · 近 2 次错题都与摩擦假设有关",
                    "建议动作 · 下次先在草稿纸写「光滑？/有摩擦？」再列式",
                ],
                ensure_ascii=False,
            ),
            "status": "open",
            "resolution": None,
        },
    )
    _upsert_bb(
        db,
        "bb_seed_physics_hist_force",
        {
            "user_id": user_id,
            "type": "challenge",
            "summary": "（历史）受力分析漏画支持力，助手拦下并补受力清单",
            "severity": "medium",
            "evidence_refs": json.dumps(
                [
                    "传话 · 温题：草稿只有重力与拉力，缺支持力，先别交。",
                    "传话 · 析因：受力漏项是上周错因第一名。",
                    "传话 · 程计：明日热身改成「先列力再写方程」模板题。",
                    "传话 · 安节：订正这题就够，别连做三道难题。",
                    "依据 · 受力分析缺支持力",
                    "建议动作 · 已补全后提交",
                ],
                ensure_ascii=False,
            ),
            "status": "resolved",
            "resolution": json.dumps(
                {"action": "ack", "note": "已按清单订正"},
                ensure_ascii=False,
            ),
        },
    )
    _upsert_bb(
        db,
        "bb_seed_physics_hist_plan",
        {
            "user_id": user_id,
            "type": "conflict",
            "summary": "（历史）曾把动能定理与摩擦长题排进同一晚，超时后改期",
            "severity": "high",
            "evidence_refs": json.dumps(
                [
                    "传话 · 程计：今晚两道长题合计 70 分钟，超过每日 50 分钟。",
                    "传话 · 安节：建议保留动能定理，摩擦题顺延。",
                    "传话 · 温题：那我把摩擦题移到练习中心「明日待做」。",
                    "传话 · 析因：连续超时会降低完成率，记一笔。",
                    "依据 · plan#overload",
                    "建议动作 · 已选择顺延",
                ],
                ensure_ascii=False,
            ),
            "status": "resolved",
            "resolution": json.dumps(
                {"action": "defer", "note": "摩擦题顺延一天"},
                ensure_ascii=False,
            ),
        },
    )
    now = datetime.now(timezone.utc)
    _replace_attempts(
        db,
        user_id,
        [
            {
                "id": "att_phy_001",
                "user_id": user_id,
                "question_id": "physics_mech_0001",
                "answer": "x = v0t + ½at²",
                "is_correct": True,
                "error_tag": None,
                "duration_ms": 18000,
                "created_at": now - timedelta(days=3),
            },
            {
                "id": "att_phy_002",
                "user_id": user_id,
                "question_id": "physics_mech_0002",
                "answer": "T1、T2、mg 闭合三角形",
                "is_correct": True,
                "error_tag": None,
                "duration_ms": 22000,
                "created_at": now - timedelta(days=2),
            },
            {
                "id": "att_phy_003",
                "user_id": user_id,
                "question_id": "physics_mech_0003",
                "answer": "按光滑斜面算出 a=g sinθ",
                "is_correct": False,
                "error_tag": "遗漏假设",
                "duration_ms": 35000,
                "created_at": now - timedelta(days=1),
            },
            {
                "id": "att_phy_004",
                "user_id": user_id,
                "question_id": "physics_mech_0004",
                "answer": "相对静止条件还没写完",
                "is_correct": None,
                "error_tag": "假设不清",
                "duration_ms": 12000,
                "created_at": now - timedelta(hours=4),
            },
            {
                "id": "att_phy_005",
                "user_id": user_id,
                "question_id": "physics_mech_0005",
                "answer": "tanθ = μs",
                "is_correct": True,
                "error_tag": None,
                "duration_ms": 26000,
                "created_at": now - timedelta(days=2, hours=6),
            },
            {
                "id": "att_phy_006",
                "user_id": user_id,
                "question_id": "physics_mech_0003",
                "answer": "补写 f=μN 后重算，方向仍反了",
                "is_correct": False,
                "error_tag": "方向判断",
                "duration_ms": 41000,
                "created_at": now - timedelta(hours=22),
            },
        ],
    )
    _ensure_ai_log(
        db,
        user_id=user_id,
        intent="verify_answer",
        request_id="seed_phy_vf",
        status="ok",
        response={"status": "ok", "verdict": "doubt"},
    )





CS_OPTIONS = [
    {"id": "extend_time", "label": "每天多挤出一点时间"},
    {"id": "reduce_depth", "label": "先降低今晚任务难度"},
    {"id": "adjust_goal", "label": "把难点挪到周末"},
]


def _seed_cs_hao(db, user_id: str) -> None:
    """郝梓博：计概 Python —— 今晚任务超时 + 沙箱练习。"""
    _reset_user_learning_state(db, user_id)
    plan = {
        "scenario": "catch_up",
        "goal": "两周内打通 Python 基础与算法入门，能独立完成入门题",
        "daily_minutes_budget": 50,
        "days_left": 14,
        "tasks": [
            _task(1, "练习", "变量与字符串沙箱题", 25, "完成沙箱自测", "low", "cs.py.basics", "cs", status="done"),
            _task(2, "练习", "分支与循环沙箱 + 平台连刷", 70, "沙箱通过并提交 2 道题", "high", "cs.py.control", "cs", error_tag="off_by_one", status="blocked"),
            _task(3, "练习", "列表与字典热身", 45, "完成列表求和沙箱", "medium", "cs.py.structures", "cs"),
            _task(4, "整理", "函数封装与边界条件笔记", 30, "写清边界用例各 2 个", "low", "cs.py.functions", "cs"),
        ],
        "_demo": {
            "plan_status": "conflict",
            "plan_message": "今晚只剩 50 分钟，但「分支与循环 + 连刷」约需 70 分钟，需要先决定怎么改今晚安排。",
            "user_options": CS_OPTIONS,
            "selected_option_id": "reduce_depth",
            "show_intervention": False,
            "setup": {
                "mode": "catch_up",
                "subject": "cs",
                "dailyMinutes": 50,
                "examDate": "2026-12-10",
                "chapter": "计概 · Python 基础",
            },
            "persona": {
                "real_name": "郝梓博",
                "major": "工科试验班（人工智能类）· 2501",
                "course": "计算与人工智能概论（Python）",
                "semester": "大一上 · 计概同步练习",
                "focus": "语法能写，但报错读不懂；今晚任务又排超了",
                "weak_points": ["IndentationError 慌", "循环边界 off-by-one", "沙箱到平台输入格式"],
                "next_action": "先确认今晚怎么安排，再去沙箱过分支循环",
                "next_path": "/plan",
                "chat_greeting": "梓博你好。今晚「分支循环 + 连刷」看起来会超出你设定的 50 分钟。要不要先一起看看怎么改？",
                "quick_asks": ["今晚时间不够怎么办", "这段报错什么意思", "给我一个提示"],
                "recent_days": [
                    {"when": "前天 21:10", "text": "变量题自测通过"},
                    {"when": "昨天 20:40", "text": "循环题 IndentationError 卡住"},
                    {"when": "今天 16:05", "text": "准备练分支，计划又叠了两道平台题"},
                ],
                "mastery": [
                    {"label": "变量字符串", "value": 78},
                    {"label": "分支循环", "value": 46},
                    {"label": "列表字典", "value": 38},
                ],
                "materials_focus": "计概课件：列表字典 + 算法思维",
            },
        },
    }
    _upsert_plan(db, user_id, plan)
    _upsert_bb(
        db,
        "bb_seed_cs_conflict",
        {
            "user_id": user_id,
            "type": "conflict",
            "summary": "今晚「分支循环 + 连刷」约需 70 分钟，超过每日 50 分钟",
            "severity": "high",
            "evidence_refs": json.dumps(
                ["依据 · 第 2 天任务约 70 分钟", "约束 · 每日 ≤ 50 分钟", "建议 · 打开学习计划选择压缩或顺延"],
                ensure_ascii=False,
            ),
            "status": "open",
            "resolution": None,
        },
    )
    now = datetime.now(timezone.utc)
    _replace_attempts(
        db,
        user_id,
        [
            {
                "id": "att_cs_hello",
                "user_id": user_id,
                "question_id": "cs_local_two_sum",
                "answer": "双重循环找两数之和",
                "is_correct": True,
                "error_tag": None,
                "duration_ms": 480000,
                "created_at": now - timedelta(days=2),
            },
            {
                "id": "att_cs_loop",
                "user_id": user_id,
                "question_id": "cs_local_jump_game",
                "answer": "穷举跳跃路径",
                "is_correct": False,
                "error_tag": "complexity",
                "duration_ms": 900000,
                "created_at": now - timedelta(days=1),
            },
        ],
    )


def _seed_research_tang(db, user_id: str) -> None:
    """唐铭鑫：科研与竞赛共创样例。"""
    _reset_user_learning_state(db, user_id)
    plan = {
        "scenario": "catch_up",
        "goal": "推进具身智能课题周报，并完成数模组队与竞赛节点对齐",
        "daily_minutes_budget": 90,
        "days_left": 21,
        "tasks": [
            _task(1, "科研", "课题实验记录整理", 40, "补齐本周原始记录并上传共创板", "medium", "research.lab", "cs", status="done"),
            _task(2, "科研", "导师月谈材料", 30, "整理进展 1 页 + 卡点 3 条", "medium", "research.mentor", "cs", status="todo"),
            _task(3, "竞赛", "数模组队意向确认", 25, "确认建模/写作/编程分工", "low", "research.contest", "cs", status="blocked"),
            _task(4, "竞赛", "RoboCup 复盘清单", 35, "输出可复用调试清单草稿", "medium", "research.contest", "cs"),
        ],
        "_demo": {
            "plan_status": "conflict",
            "plan_message": "今晚科研记录与组队讨论叠在一起，建议先保课题周报，组队沟通顺延到明早。",
            "user_options": [
                {"id": "extend_time", "label": "今晚加时 30 分钟"},
                {"id": "reduce_depth", "label": "先交周报，组队改明早"},
                {"id": "adjust_goal", "label": "竞赛讨论挪到周末"},
            ],
            "selected_option_id": "reduce_depth",
            "show_intervention": False,
            "setup": {
                "mode": "catch_up",
                "subject": "cs",
                "dailyMinutes": 90,
                "examDate": "2026-12-20",
                "chapter": "科研与竞赛 · 课题推进",
            },
            "persona": {
                "real_name": "唐铭鑫",
                "major": "工科试验班（人工智能类）· 2501",
                "course": "科研与竞赛共创",
                "semester": "大一 · 全员进组",
                "focus": "课题周报与赛事节点并行，需要显式排期",
                "weak_points": ["实验记录碎片化", "竞赛节点容易临时抱佛脚"],
                "next_action": "打开科研竞赛板，勾选本周清单",
                "next_path": "/research",
                "chat_greeting": "铭鑫你好。今晚课题周报和组队讨论叠在一起了——要不要先保周报，把组队挪到明早？",
                "quick_asks": ["今晚先做什么", "竞赛节点有哪些", "怎么写周报"],
                "recent_days": [
                    {"when": "前天", "text": "完成一次导师沟通"},
                    {"when": "昨天", "text": "整理 RoboCup 复盘要点"},
                    {"when": "今天", "text": "准备上传实验记录"},
                ],
                "mastery": [
                    {"label": "课题推进", "value": 62},
                    {"label": "竞赛准备", "value": 48},
                    {"label": "文档沉淀", "value": 55},
                ],
                "materials_focus": "科研竞赛板 · 组队与周报模板",
            },
        },
    }
    _upsert_plan(db, user_id, plan)
    _upsert_bb(
        db,
        "bb_seed_research_conflict",
        {
            "user_id": user_id,
            "type": "conflict",
            "summary": "今晚课题周报与竞赛组队叠压，建议先保周报",
            "severity": "high",
            "evidence_refs": json.dumps(
                ["依据 · 科研板清单未完成项 2 条", "建议 · 打开 /research 勾选并重排"],
                ensure_ascii=False,
            ),
            "status": "open",
            "resolution": None,
        },
    )
    _upsert_bb(
        db,
        "bb_seed_research_contest",
        {
            "user_id": user_id,
            "type": "hypothesis",
            "summary": "数模组队宜在两周内锁定分工，避免临赛换人",
            "severity": "medium",
            "evidence_refs": json.dumps(
                ["依据 · 往年经验：分工不定会拖写作", "建议 · 在科研板登记组队意向"],
                ensure_ascii=False,
            ),
            "status": "open",
            "resolution": None,
        },
    )


FOCUS_IDS = {UID_ZHANG, UID_WANG, UID_HAO, UID_TANG}


def _cleanup_non_roster_students(db, roster_sids: set[str]) -> int:
    """删除花名册以外的所有学生及其学习数据；保留 admin。"""
    keep_ids = {_uid_for_sid(sid) for sid in roster_sids} | {UID_ADMIN}
    keep_names = set(roster_sids) | {"admin"}
    removed = 0
    rows = list(db.scalars(select(User)).all())
    for user in rows:
        if user.role == "admin" or user.username == "admin" or user.id == UID_ADMIN:
            continue
        if user.id in keep_ids or (user.username and user.username in keep_names):
            continue
        db.execute(delete(Attempt).where(Attempt.user_id == user.id))
        db.execute(delete(BlackboardEntry).where(BlackboardEntry.user_id == user.id))
        db.execute(delete(Plan).where(Plan.user_id == user.id))
        db.execute(delete(AiCallLog).where(AiCallLog.user_id == user.id))
        db.delete(user)
        removed += 1
    for old_id in (
        "u_stats_pad",
        "u_student_math",
        "u_student_physics",
        "u_student_catchup",
        "u_student_cs",
    ):
        pad = db.get(User, old_id)
        if pad is not None and pad.id not in keep_ids:
            db.execute(delete(Attempt).where(Attempt.user_id == old_id))
            db.execute(delete(BlackboardEntry).where(BlackboardEntry.user_id == old_id))
            db.execute(delete(Plan).where(Plan.user_id == old_id))
            db.execute(delete(AiCallLog).where(AiCallLog.user_id == old_id))
            db.delete(pad)
            removed += 1
    return removed


def _seed_roster_users(db, roster: dict) -> int:
    created = 0
    for item in roster["students"]:
        sid = item["student_id"]
        uid = _uid_for_sid(sid)
        before = db.get(User, uid)
        _upsert_user(
            db,
            {
                "id": uid,
                "username": sid,
                "display_name": item["name"],
                "role": "student",
                "password": _password_for_sid(sid),
                "demo_time_jump_days": 0,
            },
        )
        if before is None:
            created += 1
    _upsert_user(
        db,
        {
            "id": UID_ADMIN,
            "username": "admin",
            "display_name": "教学管理",
            "role": "admin",
            "password": ADMIN_PASSWORD,
            "demo_time_jump_days": 0,
        },
    )
    return created


def reseed_focus_user(db, user_id: str) -> bool:
    """恢复四名样例账号的开场数据。"""
    table = {
        UID_ZHANG: _seed_math_conflict,
        SAMPLE_ZHANG: _seed_math_conflict,
        UID_WANG: _seed_physics_ok,
        SAMPLE_WANG: _seed_physics_ok,
        UID_HAO: _seed_cs_hao,
        SAMPLE_HAO: _seed_cs_hao,
        UID_TANG: _seed_research_tang,
        SAMPLE_TANG: _seed_research_tang,
    }
    fn = table.get(user_id)
    target = None
    if fn is _seed_math_conflict:
        target = UID_ZHANG
    elif fn is _seed_physics_ok:
        target = UID_WANG
    elif fn is _seed_cs_hao:
        target = UID_HAO
    elif fn is _seed_research_tang:
        target = UID_TANG
    if fn is None:
        user = db.get(User, user_id)
        if user is None or not user.username:
            return False
        mapped = {
            SAMPLE_ZHANG: (UID_ZHANG, _seed_math_conflict),
            SAMPLE_WANG: (UID_WANG, _seed_physics_ok),
            SAMPLE_HAO: (UID_HAO, _seed_cs_hao),
            SAMPLE_TANG: (UID_TANG, _seed_research_tang),
        }.get(user.username)
        if mapped is None:
            return False
        target, fn = mapped
    fn(db, target)
    return True


def seed_demo_accounts() -> dict:
    init_db()
    roster = _load_roster()
    roster_sids = {item["student_id"] for item in roster["students"]}
    with SessionLocal() as db:
        removed = _cleanup_non_roster_students(db, roster_sids)
        created = _seed_roster_users(db, roster)
        db.flush()
        _seed_math_conflict(db, UID_ZHANG)
        _seed_physics_ok(db, UID_WANG)
        _seed_cs_hao(db, UID_HAO)
        _seed_research_tang(db, UID_TANG)
        db.commit()
        student_total = len(
            list(db.scalars(select(User).where(User.role == "student")).all())
        )
    return {
        "class": roster.get("class_name"),
        "removed": removed,
        "created": created,
        "students_total": student_total,
        "samples": [SAMPLE_ZHANG, SAMPLE_WANG, SAMPLE_HAO, SAMPLE_TANG],
        "admin": "admin",
    }


def main() -> int:
    stats = seed_demo_accounts()
    print("seeded roster accounts:", stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
