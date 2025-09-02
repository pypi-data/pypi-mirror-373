from typing import Annotated, Optional

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    limit: Annotated[int, Field(ge=0, le=1000)] = 10
    starting_after: Optional[int] = None
    ending_before: Optional[int] = None
