"""Agent 服务配置。优先读 agent/.env，其次仓库根目录 .env。"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

AGENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = AGENT_ROOT.parent
# worktree 场景：密钥常放在上级 private 仓库根 .env
PRIVATE_ROOT = REPO_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(PRIVATE_ROOT / ".env"),
            str(REPO_ROOT / ".env"),
            str(AGENT_ROOT / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    deepseek_api_key: str = ""
    model_name: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"
    # 可选：本机 Clash 等代理，解决直连 api.deepseek.com SSL 失败
    deepseek_proxy: str = ""
    https_proxy: str = ""
    http_proxy: str = ""
    agent_host: str = "0.0.0.0"
    agent_port: int = 8001
    agent_version: str = "0.1.0"
    log_sensitive: bool = False

    def resolve_llm_proxy(self) -> str:
        for value in (self.deepseek_proxy, self.https_proxy, self.http_proxy):
            if (value or "").strip():
                return value.strip()
        return ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
