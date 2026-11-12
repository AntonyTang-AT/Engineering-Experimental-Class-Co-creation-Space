"""DeepSeek OpenAI 兼容客户端（唯一模型出口）。"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import httpx
from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class ChatResult:
    text: str
    model: str
    used_llm: bool
    error: str | None = None


def is_configured() -> bool:
    key = (get_settings().deepseek_api_key or "").strip()
    return bool(key) and "请替换" not in key and key.lower() not in {"sk-xxx", "your_key"}


@lru_cache
def _client() -> OpenAI | None:
    settings = get_settings()
    if not is_configured():
        return None
    proxy = settings.resolve_llm_proxy()
    http_client: httpx.Client | None = None
    if proxy:
        # trust_env=False：避免系统代理与显式代理叠加导致二次拐弯
        http_client = httpx.Client(proxy=proxy, timeout=45.0, trust_env=False)
        logger.info("DeepSeek client using proxy %s", proxy.split("@")[-1])
    return OpenAI(
        api_key=settings.deepseek_api_key.strip(),
        base_url=(settings.deepseek_base_url or "https://api.deepseek.com").rstrip("/"),
        timeout=45.0,
        http_client=http_client,
    )


def chat(
    *,
    system: str,
    user: str,
    temperature: float = 0.4,
    max_tokens: int = 800,
) -> ChatResult:
    """同步对话；无 Key 或调用失败时 used_llm=False，由调用方走规则兜底。"""
    settings = get_settings()
    client = _client()
    if client is None:
        return ChatResult(text="", model=settings.model_name, used_llm=False, error="llm_not_configured")

    try:
        resp = client.chat.completions.create(
            model=settings.model_name or "deepseek-chat",
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        choice = resp.choices[0].message.content if resp.choices else ""
        text = (choice or "").strip()
        if not text:
            return ChatResult(
                text="",
                model=settings.model_name,
                used_llm=False,
                error="empty_completion",
            )
        return ChatResult(text=text, model=settings.model_name, used_llm=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning("DeepSeek chat failed: %s", exc)
        return ChatResult(
            text="",
            model=settings.model_name,
            used_llm=False,
            error=str(exc),
        )


def chat_json_hint(
    *,
    system: str,
    user: str,
    temperature: float = 0.3,
    max_tokens: int = 900,
) -> dict[str, Any] | None:
    """要求模型返回 JSON 对象；解析失败返回 None。"""
    import json
    import re

    result = chat(
        system=system + "\n只输出一个 JSON 对象，不要 Markdown 代码块。",
        user=user,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if not result.used_llm or not result.text:
        return None
    raw = result.text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if fence:
        raw = fence.group(1).strip()
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            try:
                data = json.loads(raw[start : end + 1])
                return data if isinstance(data, dict) else None
            except json.JSONDecodeError:
                return None
        return None
