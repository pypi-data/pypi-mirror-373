from enum import IntEnum
from typing import Annotated, Any, Optional, Union

from pydantic import BaseModel, BeforeValidator, Field, SerializerFunctionWrapHandler, WrapSerializer


class OperationType(IntEnum):
    """
    XXX: Hey developer! This enum has to match the fields of `message Operation` below
    """

    graph = 0
    label = 1
    ask = 2
    qa = 3
    extract = 4
    prompt_guard = 5
    llama_guard = 6


# Custom serialization so clients get the string representation of the OperationType enum instead of the int
# This has to be done because the IntEnum is forced by protobuf definition
def serialize_operation_type(value: OperationType, nxt: SerializerFunctionWrapHandler) -> str:
    return value.name


# To accept both string and int values for OperationType
def validate_operation_type(value: Union[str, int]) -> Union[OperationType, int]:
    if isinstance(value, str):
        try:
            return OperationType[value]
        except KeyError as e:
            msg = f"Invalid OperationType {value}, must be one of {OperationType._member_names_}"
            raise ValueError(msg) from e
    return value


OperationTypeString = Annotated[
    OperationType,
    WrapSerializer(serialize_operation_type),
    BeforeValidator(validate_operation_type),
]


class NameOperationFilter(BaseModel):
    """
    Filtering Data Augmentation Agents by operation type and task names.
    """

    operation_type: OperationTypeString = Field(..., description="Type of the operation")
    task_names: list[str] = Field(
        default_factory=list,
        description="List of task names. If None or empty, all tasks for that operation are applied.",
    )


class Ask(BaseModel):
    text: Optional[str] = None
    json_output: Optional[dict[str, Any]] = None
    empty: bool = False


class Position(BaseModel):
    start: int
    end: int


class Entities(BaseModel):
    labels: dict[str, str]
    positions: dict[str, list[Position]]


class RelationNode(BaseModel):
    """
    Represents a relation between two entities.

    """

    entity: str
    label: str
    position: Position


# XXX: We have this model here instead of using existing Relation models
# because this one is sent with triggers
class Relation(BaseModel):
    """
    Represents a relation between two entities.

    """

    head: RelationNode
    tail: RelationNode
    label: str
    paragraph_id: str


class Relations(BaseModel):
    relations: list[Relation]


class Labels(BaseModel):
    labels: dict[str, Union[str, list[str]]]


class Question(BaseModel):
    question: str
    answer: str
    block: int
    reasoning: str
    paragraph_id: str


class Payload(BaseModel):
    type: OperationTypeString = Field(
        ...,
        description=f"The type of operation performed, can be any of {OperationType._member_names_}",
    )
    task_name: str = Field(..., description="The name of the task that generated this payload")
    errors: list[str] = Field(
        default_factory=list,
        description="List of errors (if any) that occurred while processing this payload",
    )
    asks: Optional[list[Ask]] = Field(default=None, description="Results of the ask operation")
    relations: Optional[list[Relations]] = Field(
        default=None, description="Relation results for the graph operation"
    )
    entities: Optional[list[Entities]] = Field(
        default=None, description="Entity results for the graph operation"
    )
    labels: Optional[list[Labels]] = Field(
        default=None, description="Label results for the labeler operation"
    )
    guard_labels: Optional[list[str]] = Field(
        default=None, description="Guard labels for the llama_guard operation"
    )
    prompt_guard: Optional[list[str]] = Field(
        default=None, description="Prompt guard labels for the prompt_guard operation"
    )
    qas: Optional[list[Question]] = Field(
        default=None,
        description="Question and answer results for the synthetic_questions operation",
    )
    kbid: str
    field: str
    rid: Optional[str] = None
