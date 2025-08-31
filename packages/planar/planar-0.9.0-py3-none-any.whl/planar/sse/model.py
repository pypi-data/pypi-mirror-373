from typing import Any

from pydantic import BaseModel


class Event(BaseModel):
    name: str
    payload: dict[str, Any]
