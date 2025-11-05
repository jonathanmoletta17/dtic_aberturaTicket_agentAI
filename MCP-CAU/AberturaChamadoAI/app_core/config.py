# -*- coding: utf-8 -*-
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class Settings:
    glpi_url: str | None
    glpi_app_token: str | None
    glpi_user_token: str | None


def load_settings() -> Settings:
    # Resolve paths: agent root (AberturaChamadoAI) and project root (MCP-CAU)
    current_file = Path(__file__).resolve()
    agent_root = current_file.parents[2]  # .../MCP-CAU/AberturaChamadoAI
    project_root = current_file.parents[3]  # .../MCP-CAU

    # Try loading .env from agent folder first, then fallback to project root
    env_candidates = [agent_root / ".env", project_root / ".env"]
    for env_path in env_candidates:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            break
    else:
        # Fallback to default behavior (current working directory)
        load_dotenv()
    return Settings(
        glpi_url=os.getenv("GLPI_URL"),
        glpi_app_token=os.getenv("GLPI_APP_TOKEN"),
        glpi_user_token=os.getenv("GLPI_USER_TOKEN"),
    )


