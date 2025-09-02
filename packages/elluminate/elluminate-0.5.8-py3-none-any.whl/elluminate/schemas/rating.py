from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel

from elluminate.schemas.base import BatchCreateStatus
from elluminate.schemas.criterion import Criterion
from elluminate.schemas.generation_metadata import GenerationMetadata


class RatingValue(str, Enum):
    YES = "YES"
    NO = "NO"


class Rating(BaseModel):
    """Rating model."""

    id: int
    criterion: Criterion
    rating: RatingValue
    reasoning: str | None = None
    generation_metadata: GenerationMetadata | None = None
    created_at: datetime


class RatingMode(str, Enum):
    """Enum for rating mode. In current implementation, only two modes are supported: fast mode is without reasoning and detailed mode is with reasoning."""

    FAST = "fast"
    DETAILED = "detailed"


class CreateRatingRequest(BaseModel):
    prompt_response_id: int
    rating_mode: RatingMode = RatingMode.FAST


class BatchCreateRatingRequest(BaseModel):
    prompt_response_ids: list[int]
    rating_mode: RatingMode = RatingMode.FAST


class BatchCreateRatingResponseStatus(BatchCreateStatus[List[Rating]]):
    pass
