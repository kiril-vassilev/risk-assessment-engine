from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    tavily_api_key: str
    azure_endpoint: str
    azure_api_key: str
    azure_api_version: str
    azure_deployment: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        values = {
            "tavily_api_key": os.getenv("TAVILY_API_KEY", ""),
            "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            "azure_api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
            "azure_api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
            "azure_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", ""),
        }
        missing = [name for name, value in values.items() if name != "azure_api_version" and not value]
        if missing:
            raise ValueError("Missing required environment variables: " + ", ".join(missing))
        return cls(**values)