from pydantic import BaseModel

from elluminate.schemas.criterion import Criterion, CriterionIn
from elluminate.schemas.prompt_template import PromptTemplate


class CriterionSet(BaseModel):
    """Criterion set model."""

    id: int
    name: str
    prompt_templates: list[PromptTemplate] | None = None
    criteria: list[Criterion] | None = None


class CreateCriterionSetRequest(BaseModel):
    """Request to create a new criterion set.

    Args:
        name: The name of the criterion set
        criteria: Optional list of criteria to create alongside the criterion set

    """

    name: str
    criteria: list[CriterionIn] | None = None
