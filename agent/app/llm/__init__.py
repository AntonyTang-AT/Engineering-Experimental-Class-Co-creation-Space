"""唯一模型客户端（DeepSeek OpenAI 兼容）。"""

from app.llm.client import ChatResult, chat, chat_json_hint, is_configured

__all__ = ["ChatResult", "chat", "chat_json_hint", "is_configured"]
