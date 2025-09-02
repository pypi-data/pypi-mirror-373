import enum
from typing import Any

from pydantic import BaseModel


class RefreshedTokenManagerParams(BaseModel):
    session: Any  # requests.Session
    clerk_session: str


class SignInStrategyType(str, enum.Enum):
    PASSWORD = "PASSWORD"
