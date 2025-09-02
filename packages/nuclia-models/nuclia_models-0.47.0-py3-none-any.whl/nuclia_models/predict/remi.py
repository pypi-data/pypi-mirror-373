from typing import Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from nuclia_models.common.consumption import Consumption


class RemiRequest(BaseModel):
    """
    Model to represent a request for the REMi model

    Metrics will be computed accordingly to the inputs given

    - Answer relevance will be computed if `answer` and `question` are provided
    - Context relevance will be computed if `question` and `contexts` are provided
    - Groundedness will be computed if `answer` and `contexts` are provided
    """

    user_id: str = Field(..., title="The user ID of the user making the request")
    question: Optional[str] = Field(default=None, title="The question or query that the user asked")
    answer: Optional[str] = Field(default=None, title="The answer that the model provided")
    contexts: Optional[list[str]] = Field(
        default=None, title="The contexts that the model used to generate the answer"
    )

    @model_validator(mode="after")
    def check_metrics(self) -> Self:
        if not any([self.question, self.answer, self.contexts]):
            message = "At least one of question, answer or contexts must be provided"
            raise ValueError(message)
        return self


class AnswerRelevance(BaseModel):
    score: int = Field(..., title="The score of the answer relevance")
    reason: str = Field(..., title="The reasoning for the score")


class RemiResponse(BaseModel):
    time: float = Field(..., title="The time taken to compute the response")
    answer_relevance: Optional[AnswerRelevance] = Field(
        default=None,
        title="The relevance score of the answer to the question.",
        description="""Answer Relevance measures the relevance of the generated answer to the user query, \
            in a scale of 0 to 5.""",
    )
    context_relevance: Optional[list[Optional[int]]] = Field(
        default=None,
        title="The relevance score of each context to the question.",
        description="""Context Relevance measures the relevance of the retrieved context to the user query, \
        in a scale of 0 to 5. The score will be None if there was an error computing the score for a specific\
         context.""",
    )
    groundedness: Optional[list[Optional[int]]] = Field(
        default=None,
        title="The groundedness score of the answer on each context.",
        description="""Groundedness measures the degree to which the generated answer is grounded in the \
        retrieved context, in a scale of 0 to 5. \
        The score will be None if there was an error computing the score for a specific context.""",
    )
    consumption: Optional[Consumption] = Field(
        default=None,
        title="The consumption details for the REMi model run",
    )
