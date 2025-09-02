from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel

from nuclia_models.common.pagination import Pagination


class ContextRelevanceQuery(BaseModel):
    value: int
    operation: Literal["gt", "lt", "eq"]
    aggregation: Literal["average", "max", "min"]


class Status(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    NO_CONTEXT = "NO_CONTEXT"

    def get_value(self) -> int:
        mapping = {
            Status.SUCCESS: 0,
            Status.ERROR: -1,
            Status.NO_CONTEXT: -2,
        }
        return mapping[self]


class RemiQuery(BaseModel):
    context_relevance: Optional[ContextRelevanceQuery] = None
    month: str
    feedback_good: Optional[bool] = None
    status: Optional[Status] = None
    pagination: Pagination = Pagination()


class RetrievedContext(BaseModel):
    text: str
    text_block_id: Optional[str] = None


class RemiAnswerRelevance(BaseModel):
    score: int
    reason: str


class RemiScores(BaseModel):
    answer_relevance: RemiAnswerRelevance
    context_relevance: list[int]
    groundedness: list[int]


class RemiQueryResult(BaseModel):
    id: int
    question: str
    answer: Optional[str]
    remi: Optional[RemiScores]


class RemiQueryResultWithContext(RemiQueryResult):
    context: list[RetrievedContext]


class RemiQueryResults(BaseModel):
    data: list[RemiQueryResult]
    has_more: bool


class AggregatedRemiScoreValues(BaseModel):
    name: str
    min: float
    max: float
    average: float


class AggregatedRemiScoreMetric(BaseModel):
    timestamp: datetime
    metrics: list[AggregatedRemiScoreValues]
