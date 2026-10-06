"""Configuration settings for Sovereign Engineering Copilot."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    # Nebius Token Factory & NVIDIA model settings
    nebius_base_url: str = os.getenv(
        "NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1"
    )
    nebius_api_key: str = os.getenv("NEBIUS_API_KEY", "")
    model_name: str = os.getenv(
        "SOVEREIGN_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct"
    )

    # Local state and temporal memory path
    workspace_dir: Path = Path(os.getenv("SOVEREIGN_WORKSPACE", ".sovereign"))
    db_path: Path = Path(os.getenv("SOVEREIGN_DB", ".sovereign/memory.db"))

    # Privacy and security governance
    enable_sanitizer: bool = True
    mask_credentials: bool = True
    mask_internal_ips: bool = True
    mask_emails: bool = True

    # Fallback to local deterministic reasoning mock if no API key is set
    mock_mode: bool = False

    def __post_init__(self):
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        if not self.nebius_api_key:
            self.mock_mode = True


def load_config() -> Config:
    return Config()
