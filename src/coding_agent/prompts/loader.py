from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class PromptTemplate(BaseModel):
    system: str
    user: str


PROMPTS_DIR = Path(__file__).parent


def load_prompt(agent: str, version: str = "1.0.0") -> PromptTemplate:
    base = PROMPTS_DIR / agent / version
    system_path = base / "system.txt"
    user_path = base / "user.txt"
    if not system_path.exists():
        raise FileNotFoundError(f"System prompt not found: {system_path}")
    if not user_path.exists():
        raise FileNotFoundError(f"User prompt not found: {user_path}")
    return PromptTemplate(
        system=system_path.read_text(encoding="utf-8"),
        user=user_path.read_text(encoding="utf-8"),
    )


def render_prompt(template: str, **kwargs) -> str:
    for key, value in kwargs.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template
