from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel

# Generic type variable for the result type
TResult = TypeVar("TResult", bound=BaseModel | Sequence[BaseModel])


class BatchCreateStatus(BaseModel, Generic[TResult]):
    status: str
    error_msg: str | None = None
