"""
Configuration for Obvyr Agent.

The BaseSettings object will attempt to replace any properties
from environment variables, allowing environmental overrides.
"""

import os
import secrets
from typing import Dict

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_AGENT_URL = "https://api.obvyr.com"


class AgentSettings(BaseModel):
    """Configuration for an Obvyr Agent."""

    API_KEY: str
    API_URL: str = DEFAULT_AGENT_URL
    ATTACHMENT_PATH: str | None = None
    TIMEOUT: float = 10.0
    VERIFY_SSL: bool = True


class Settings(BaseSettings):
    """Configuration and settings for the Obvyr Agent."""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="OBVYR_",
        env_nested_delimiter="__",
        env_ignore_empty=True,
        extra="ignore",
        populate_by_name=True,
    )

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACTIVE_AGENT: str = "DEFAULT"  # Default agent
    AGENTS: Dict[str, AgentSettings] = Field(default_factory=dict)

    @classmethod
    def get_env_prefix(cls) -> str:
        """Retrieve the configured environment variable prefix."""
        return cls.model_config.get("env_prefix", "")

    @classmethod
    def remove_old_env_vars(cls) -> None:
        """Removes all old environment variables that match the `env_prefix`."""
        env_prefix = cls.get_env_prefix()

        for key in list(os.environ.keys()):
            if not key == "OBVYR_ACTIVE_AGENT" and key.startswith(env_prefix):
                del os.environ[key]

    def get_agent(self, agent_name: str | None = None) -> AgentSettings:
        """Return settings for the specified agent or currently active agent."""
        if agent_name:
            active_agent = agent_name.strip().upper()
        else:
            active_agent = self.ACTIVE_AGENT.strip().upper()

        if active_agent not in self.AGENTS:
            raise ValueError(
                f"Agent '{active_agent}' not found in configuration."
            )
        agent = self.AGENTS[active_agent]

        return agent

    def list_agents(self) -> list:
        """Return a list of available agents."""
        return list(self.AGENTS.keys())

    def show_config(self, agent_name: str | None = None) -> dict:
        """Show active agent's settings (excluding API keys)."""
        active_agent = self.get_agent(agent_name)
        return {
            k.upper(): v
            for k, v in active_agent.model_dump().items()
            if "KEY" not in k.upper()
        }


def get_settings() -> Settings:
    """Return the current settings."""
    Settings.remove_old_env_vars()
    load_dotenv(".env", override=True)

    return Settings()
