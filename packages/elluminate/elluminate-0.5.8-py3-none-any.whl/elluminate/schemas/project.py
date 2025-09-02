from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Project(BaseModel):
    """Project model."""

    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
