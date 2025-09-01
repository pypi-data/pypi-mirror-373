import json
import os
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from aiofiles import open


@dataclass
class AuthSessions:
    enabled: bool = False


@dataclass
class IntunedSettings:
    auth_sessions: AuthSessions = field(default_factory=AuthSessions)


default_settings = IntunedSettings()


def validate_settings(settings_dict: dict[Any, Any]) -> IntunedSettings:
    auth_sessions = AuthSessions(enabled=settings_dict.get("authSessions", {}).get("enabled", False))
    return IntunedSettings(auth_sessions=auth_sessions)


async def load_intuned_settings() -> IntunedSettings:
    settings_path = os.path.join(os.getcwd(), "Intuned.json")
    if not os.path.exists(settings_path):
        return default_settings
    try:
        async with open(settings_path) as settings_file:
            content = await settings_file.read()
            settings_dict = json.loads(content)
        return validate_settings(settings_dict)
    except json.JSONDecodeError as e:
        raise Exception("Invalid Intuned.json file") from e
