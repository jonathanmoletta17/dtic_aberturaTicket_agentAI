# -*- coding: utf-8 -*-
import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Settings:
    glpi_url: str | None
    glpi_app_token: str | None
    glpi_user_token: str | None


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        glpi_url=os.getenv("GLPI_URL"),
        glpi_app_token=os.getenv("GLPI_APP_TOKEN"),
        glpi_user_token=os.getenv("GLPI_USER_TOKEN"),
    )


