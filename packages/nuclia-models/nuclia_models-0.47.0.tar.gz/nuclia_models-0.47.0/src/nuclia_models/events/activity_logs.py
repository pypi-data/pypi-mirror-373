import re
import warnings
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Generic, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from pydantic.main import create_model

from nuclia_models.common.client import ClientType
from nuclia_models.common.pagination import Pagination
from nuclia_models.common.user import UserType
from nuclia_models.common.utils import CaseInsensitiveEnum

T = TypeVar("T")


class EventType(CaseInsensitiveEnum):
    # Nucliadb
    VISITED = "visited"
    MODIFIED = "modified"
    DELETED = "deleted"
    NEW = "new"
    SEARCH = "search"
    SUGGEST = "suggest"
    INDEXED = "indexed"
    CHAT = "chat"
    ASK = "ask"
    # Tasks
    STARTED = "started"
    STOPPED = "stopped"
    # Processor
    PROCESSED = "processed"


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ShowOnly(BaseConfigModel):
    """
    Marker class to indicate that a field is for display purposes only.

    Fields wrapped in this class are excluded from OpenAPI documentation to prevent confusion,
    as they are not intended for filtering. Instead, they are only used in the "show" parameter.

    This behavior is enforced in the FastAPI application through introspection,
    ensuring these fields are removed from the generated API documentation.
    """


class GenericFilter(BaseConfigModel, Generic[T]):
    eq: Optional[T] = None
    gt: Optional[T] = None
    ge: Optional[T] = None
    lt: Optional[T] = None
    le: Optional[T] = None
    ne: Optional[T] = None
    isnull: Optional[bool] = None


class StringFilter(GenericFilter[str]):
    like: Optional[str] = None
    ilike: Optional[str] = None


class AuditMetadata(StringFilter):
    key: str


class QueryFiltersCommon(BaseConfigModel):
    id: Optional[GenericFilter[int]] = None
    date: Optional[ShowOnly] = Field(None, serialization_alias="event_date")
    user_id: Optional[GenericFilter[str]] = None
    user_type: Optional[GenericFilter[UserType]] = None
    client_type: Optional[GenericFilter[ClientType]] = None
    total_duration: Optional[GenericFilter[int]] = None
    audit_metadata: Optional[list[AuditMetadata]] = Field(
        None, serialization_alias="data.user_request.audit_metadata"
    )
    resource_id: Optional[ShowOnly] = None
    nuclia_tokens: Optional[GenericFilter[float]] = Field(
        None, serialization_alias="nuclia_tokens.billable_nuclia_tokens"
    )
    token_details: Optional[ShowOnly] = Field(None, serialization_alias="nuclia_tokens.token_details")


class QueryFiltersSearch(QueryFiltersCommon):
    question: Optional[StringFilter] = Field(None, serialization_alias="data.user_request.query")
    resources_count: Optional[GenericFilter[int]] = Field(
        None,
        serialization_alias="data.resources_count",
        # cast_to is only needed for JSONB columns, it allows values: str, bool, int, float
        json_schema_extra={"cast_to": "int"},
    )
    filter: Optional[ShowOnly] = Field(None, serialization_alias="data.request.filter")
    learning_id: Optional[ShowOnly] = Field(None, serialization_alias="data.request.learning_id")
    retrieval_rephrased_question: Optional[ShowOnly] = Field(
        None, serialization_alias="data.request.retrieval_rephrased_question"
    )
    vectorset: Optional[StringFilter] = Field(None, serialization_alias="data.request.vectorset")
    security: Optional[ShowOnly] = Field(None, serialization_alias="data.request.security")
    min_score_bm25: Optional[GenericFilter[float]] = Field(
        None, serialization_alias="data.request.min_score_bm25", json_schema_extra={"cast_to": "float"}
    )
    min_score_semantic: Optional[GenericFilter[float]] = Field(
        None, serialization_alias="data.request.min_score_semantic", json_schema_extra={"cast_to": "float"}
    )
    result_per_page: Optional[GenericFilter[int]] = Field(
        None, serialization_alias="data.request.result_per_page", json_schema_extra={"cast_to": "int"}
    )
    retrieval_time: Optional[GenericFilter[int]] = Field(
        None,
        serialization_alias="data.retrieval_time",
        json_schema_extra={"cast_to": "int"},
        description=(
            "Time in milliseconds spent on the NucliaDB side for retrieval, including retrieval rephrase,"
            " calculation of query embedding, index search and results hydration"
        ),
    )


class QueryFiltersChat(QueryFiltersSearch):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "QueryFiltersChat is deprecated and will be removed in a future version. "
            "Please use QueryFiltersAsk instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)

    rephrased_question: Optional[StringFilter] = Field(
        None, serialization_alias="data.request.rephrased_question"
    )
    answer: Optional[StringFilter] = Field(None, serialization_alias="data.request.answer")
    retrieved_context: Optional[ShowOnly] = Field(None, serialization_alias="data.request.context")
    chat_history: Optional[ShowOnly] = Field(None, serialization_alias="data.request.chat_context")
    feedback_good: Optional[GenericFilter[bool]] = Field(
        None,
        serialization_alias="data.feedback.good",
        json_schema_extra={"cast_to": "bool"},
        description="True if the feedback provided for the main question is positive.",
    )
    feedback_comment: Optional[StringFilter] = Field(
        None,
        serialization_alias="data.feedback.feedback",
        description="User-provided comment on the feedback for the question.",
    )
    feedback_good_all: Optional[GenericFilter[bool]] = Field(
        None,
        serialization_alias="data.feedback.all",
        json_schema_extra={"cast_to": "bool"},
        description=(
            "True if all feedback, including that on the main question"
            " and each related text block, is positive."
        ),
    )
    feedback_good_any: Optional[GenericFilter[bool]] = Field(
        None,
        serialization_alias="data.feedback.any",
        json_schema_extra={"cast_to": "bool"},
        description=(
            "True if there is any positive feedback" " on the question itself or any related text block."
        ),
    )
    feedback: Optional[ShowOnly] = Field(
        None,
        serialization_alias="data.feedback",
        description=(
            "Raw feedback data associated with the question or generative answer,"
            " including feedback on related text blocks."
        ),
    )
    model: Optional[StringFilter] = Field(None, serialization_alias="data.request.model")
    rag_strategies_names: Optional[ShowOnly] = Field(None, serialization_alias="data.rag_strategies")
    rag_strategies: Optional[ShowOnly] = Field(None, serialization_alias="data.user_request.rag_strategies")
    status: Optional[GenericFilter[int]] = Field(
        None,
        serialization_alias="data.request.status_code",
        json_schema_extra={"cast_to": "int"},
    )
    generative_answer_first_chunk_time: Optional[GenericFilter[int]] = Field(
        None,
        serialization_alias="data.generative_answer_first_chunk_time",
        json_schema_extra={"cast_to": "int"},
        description=(
            "Time in milliseconds from when the user made the request to when the first chunk"
            " of data was returned by the generative model."
        ),
    )
    generative_answer_time: Optional[GenericFilter[int]] = Field(
        None,
        serialization_alias="data.generative_answer_time",
        json_schema_extra={"cast_to": "int"},
        description=(
            "Time in milliseconds elapsed between the answer streaming request is done"
            " to the generative model until the last chunk of the answer is returned."
        ),
    )
    remi_scores: Optional[ShowOnly] = Field(None, serialization_alias="data_eval")
    user_request: Optional[ShowOnly] = Field(None, serialization_alias="data.user_request")


class QueryFiltersAsk(QueryFiltersChat):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Call the grandparent class directly to skip the deprecation warning
        super(QueryFiltersSearch, self).__init__(*args, **kwargs)


def create_dynamic_model(name: str, base_model: type[QueryFiltersAsk]) -> type[BaseModel]:
    field_definitions = {}
    # Any field that is not str should be added here, this is used for the API activity log schema response
    field_type_map = {
        "id": int,
        "user_type": Optional[UserType],
        "client_type": Optional[ClientType],
        "total_duration": Optional[float],
        "generative_answer_first_chunk_time": Optional[int],
        "generative_answer_time": Optional[int],
        "resources_count": Optional[int],
        "feedback_good": Optional[bool],
        "feedback_good_all": Optional[bool],
        "feedback_good_any": Optional[bool],
        "feedback": Optional[dict],
        "status": Optional[int],
        "rag_strategies": Optional[list],
        "rag_strategies_names": Optional[list],
        "chat_history": Optional[list],
        "retrieved_context": Optional[list],
        "nuclia_tokens": Optional[float],
        "remi_scores": Optional[dict],
        "token_details": Optional[dict],
        "user_request": Optional[dict],
        "min_score_bm25": Optional[float],
        "min_score_semantic": Optional[float],
        "result_per_page": Optional[int],
        "retrieval_time": Optional[int],
    }
    for field_name in base_model.model_fields:
        field_type = field_type_map.get(field_name, Optional[str])

        field_definitions[field_name] = (field_type, Field(default=None))

    return create_model(name, **field_definitions)  # type: ignore


ActivityLogsQueryResponse = create_dynamic_model(name="ActivityLogsQueryResponse", base_model=QueryFiltersAsk)


class ActivityLogsQueryCommon(BaseConfigModel):
    year_month: str

    @field_validator("year_month")
    @classmethod
    def validate_year_month(cls, value: str) -> str:
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", value):
            msg = "year_month must be in the format YYYY-MM"
            raise ValueError(msg)
        return value

    @staticmethod
    def _validate_show(
        show: Union[set[str], Literal["all"]], model: type[QueryFiltersCommon]
    ) -> Union[set[str], Literal["all"]]:
        if show == "all":
            return show

        allowed_fields = list(model.model_fields.keys())
        for field in show:
            if field.startswith("audit_metadata."):
                continue
            if field not in allowed_fields:
                msg = f"{field} is not a field. List of fields: {allowed_fields}"
                raise ValueError(msg)
        return show


SHOW_LITERAL = Literal[tuple(QueryFiltersCommon.model_fields.keys())]  # type: ignore
SHOW_SEARCH_LITERAL = Literal[tuple(QueryFiltersSearch.model_fields.keys())]  # type: ignore
SHOW_ASK_LITERAL = Literal[tuple(QueryFiltersAsk.model_fields.keys())]  # type: ignore
DEFAULT_SHOW_VALUES = {"id", "date"}
DEFAULT_SHOW_SEARCH_VALUES = DEFAULT_SHOW_VALUES | {"question", "resources_count"}
DEFAULT_SHOW_ASK_VALUES = DEFAULT_SHOW_SEARCH_VALUES | {
    "rephrased_question",
    "answer",
    "rag_strategies_names",
}


class ActivityLogs(ActivityLogsQueryCommon):
    show: Union[set[SHOW_LITERAL], Literal["all"]] = DEFAULT_SHOW_VALUES  # type: ignore
    filters: QueryFiltersCommon

    @field_validator("show")
    @classmethod
    def validate_show(cls, show: Union[set[str], Literal["all"]]) -> Union[set[str], Literal["all"]]:
        return cls._validate_show(show=show, model=QueryFiltersCommon)


class ActivityLogsSearch(ActivityLogsQueryCommon):
    show: Union[set[SHOW_SEARCH_LITERAL], Literal["all"]] = DEFAULT_SHOW_SEARCH_VALUES  # type: ignore
    filters: QueryFiltersSearch

    @field_validator("show")
    @classmethod
    def validate_show(cls, show: Union[set[str], Literal["all"]]) -> Union[set[str], Literal["all"]]:
        return cls._validate_show(show=show, model=QueryFiltersSearch)


class ActivityLogsChat(ActivityLogsQueryCommon):
    show: Union[set[SHOW_ASK_LITERAL], Literal["all"]] = DEFAULT_SHOW_ASK_VALUES  # type: ignore
    filters: Union[QueryFiltersAsk, QueryFiltersChat]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "ActivityLogsChat is deprecated and will be removed in a future version. "
            "Please use ActivityLogsAsk instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)

    @field_validator("show")
    @classmethod
    def validate_show(cls, show: Union[set[str], Literal["all"]]) -> Union[set[str], Literal["all"]]:
        return cls._validate_show(show=show, model=QueryFiltersAsk)


class ActivityLogsAsk(ActivityLogsChat):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Call the grandparent class directly to skip the deprecation warning
        super(ActivityLogsQueryCommon, self).__init__(*args, **kwargs)


class PaginationMixin(BaseModel):
    pagination: Pagination = Pagination()

    @model_validator(mode="after")
    @classmethod
    def validate_pagination_and_filters(cls, values):  # type: ignore
        if values.pagination and values.filters and values.filters.id is not None:
            raise ValueError("Payload cannot have both 'pagination' and an 'id' in 'filters'.")  # noqa: TRY003, EM101
        return values


class ActivityLogsSearchQuery(ActivityLogsSearch, PaginationMixin):
    pass


class ActivityLogsChatQuery(ActivityLogsChat, PaginationMixin):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "ActivityLogsChatQuery is deprecated and will be removed in a future version. "
            "Please use ActivityLogsAskQuery instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class ActivityLogsAskQuery(ActivityLogsAsk, PaginationMixin):
    pass


class ActivityLogsQuery(ActivityLogs, PaginationMixin):
    pass


class DownloadRequestType(str, Enum):
    QUERY = "query"


class DownloadFormat(str, Enum):
    NDJSON = "ndjson"
    CSV = "csv"


class DownloadRequest(BaseModel):
    id: Annotated[int, Field(exclude=True)]
    request_id: str
    download_type: DownloadRequestType
    download_format: DownloadFormat
    event_type: EventType
    requested_at: datetime
    user_id: Annotated[str, Field(exclude=True)]
    kb_id: str
    query: Annotated[dict[Any, Any], Field(exclude=True)]
    download_url: Optional[str]

    # Configuration for Pydantic v2 to handle ORM mapping
    class Config:
        from_attributes = True


class DownloadActivityLogsQueryMixin(BaseModel):
    email_address: Optional[EmailStr] = Field(default=None)
    notify_via_email: bool = Field(default=False)


class DownloadActivityLogsSearchQuery(DownloadActivityLogsQueryMixin, ActivityLogsSearch):
    pass


class DownloadActivityLogsChatQuery(DownloadActivityLogsQueryMixin, ActivityLogsChat):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "DownloadActivityLogsChatQuery is deprecated and will be removed in a future version. "
            "Please use DownloadActivityLogsAskQuery instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class DownloadActivityLogsAskQuery(DownloadActivityLogsQueryMixin, ActivityLogsAsk):
    pass


class DownloadActivityLogsQuery(DownloadActivityLogsQueryMixin, ActivityLogs):
    pass
