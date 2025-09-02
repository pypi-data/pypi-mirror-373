from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, model_validator

from nuclia_models.common.utils import BaseConfigModel
from nuclia_models.worker.proto import ApplyTo, DataAugmentation


class ApplyOptions(str, Enum):
    """
    Defines how the tasks should be applied to the existing data.
    - EXSITING: Only apply to existing data (starts a worker that executes the task)
    - NEW: Only apply to new data (enables the task at processing time)
    - ALL: Apply to all data (both of the above)
    """

    EXISTING = "EXISTING"
    NEW = "NEW"
    ALL = "ALL"


class TaskName(str, Enum):
    DUMMY = "dummy"
    ENV = "env"
    DEMO_DATASET = "demo-dataset"
    LABELER = "labeler"
    LLM_GRAPH = "llm-graph"
    SYNTHETIC_QUESTIONS = "synthetic-questions"
    ASK = "ask"
    LLM_ALIGN = "llm-align"
    SEMANTIC_MODEL_MIGRATOR = "semantic-model-migrator"
    LLAMA_GUARD = "llama-guard"
    PROMPT_GUARD = "prompt-guard"


class JobStatus(str, Enum):
    NOT_RUNNING = "not_running"
    FINISHED = "finished"
    RUNNING = "running"
    STARTED = "started"
    STOPPED = "stopped"
    FAILED = "failed"


class SemanticModelMigrationParams(BaseModel):
    semantic_model_id: str = Field(
        description=(
            "The id of the semantic model to migrate to."
            " This must be a valid semantic model id available for the account"
        )
    )


PARAMETERS_MODELS = Union[DataAugmentation, SemanticModelMigrationParams]
PARAMETERS_TYPING = Optional[PARAMETERS_MODELS]


class TaskValidation(BaseModel):
    validation: Optional[type[PARAMETERS_MODELS]] = None
    available_on: list[ApplyTo] = []

    def custom_validation(self, name: TaskName, parameters: PARAMETERS_TYPING) -> "TaskValidation":
        validation_class = self.validation if self.validation is not None else type(None)
        if not isinstance(parameters, validation_class):
            if self.validation is None:
                msg = f"Task {name.value} parameters must be null"
                raise ValueError(msg)
            msg = f"Task {name.value} parameters must match the {self.validation.__name__} model."
            raise ValueError(msg)  # noqa: TRY004
        if isinstance(parameters, DataAugmentation):
            if parameters.on not in self.available_on:
                msg = f"Can not run task on {parameters.on} can only run on {self.available_on}"
                raise ValueError(msg)
            if len(parameters.operations) == 0:
                msg = "At least one operation must be defined"
                raise ValueError(msg)

        return self


TASKS: dict[TaskName, TaskValidation] = {
    TaskName.DUMMY: TaskValidation(),
    TaskName.ENV: TaskValidation(),
    TaskName.DEMO_DATASET: TaskValidation(),
    TaskName.LABELER: TaskValidation(
        validation=DataAugmentation,
        available_on=[ApplyTo.TEXT_BLOCK, ApplyTo.FIELD],
    ),
    TaskName.PROMPT_GUARD: TaskValidation(
        validation=DataAugmentation,
        available_on=[ApplyTo.TEXT_BLOCK, ApplyTo.FIELD],
    ),
    TaskName.LLAMA_GUARD: TaskValidation(
        validation=DataAugmentation,
        available_on=[ApplyTo.FIELD, ApplyTo.TEXT_BLOCK],
    ),
    TaskName.LLM_GRAPH: TaskValidation(
        validation=DataAugmentation,
        available_on=[ApplyTo.FIELD],
    ),
    TaskName.SYNTHETIC_QUESTIONS: TaskValidation(
        validation=DataAugmentation,
        available_on=[ApplyTo.FIELD],
    ),
    TaskName.ASK: TaskValidation(
        validation=DataAugmentation,
        available_on=[ApplyTo.FIELD],
    ),
    TaskName.LLM_ALIGN: TaskValidation(
        validation=DataAugmentation,
    ),
    TaskName.SEMANTIC_MODEL_MIGRATOR: TaskValidation(
        validation=SemanticModelMigrationParams,
        available_on=[ApplyTo.FIELD],
    ),
}


class TaskStart(BaseConfigModel):
    name: TaskName
    parameters: PARAMETERS_TYPING = Field(
        description=(
            "Parameters to be passed to the task."
            " These must match the `validation` field for the Task definition class"
        ),
    )

    @model_validator(mode="after")
    def validate_parameters(self) -> "TaskStart":
        task: Optional[TaskValidation] = TASKS.get(self.name)
        if task is None:
            msg = f"There is no task defined for {self.name.value}"
            raise ValueError(msg)

        task.custom_validation(name=self.name, parameters=self.parameters)
        return self


class TaskStartKB(TaskStart):
    apply: ApplyOptions = Field(
        default=ApplyOptions.ALL,
        description=ApplyOptions.__doc__,
    )


class TaskResponse(BaseModel):
    name: TaskName
    status: JobStatus
    id: str


class TrainingTaskDatasetSource(str, Enum):
    # A knowledge box stored in NucliaDB
    NUCLIADB = "nucliadb"

    # A dataset located in a storage
    DATASET = "dataset"


class PublicTask(BaseModel):
    name: str
    data_augmentation: bool = False
    description: Optional[str] = None


class PublicTaskRequest(BaseModel):
    task: PublicTask
    source: TrainingTaskDatasetSource
    kbid: Optional[str] = None
    dataset_id: Optional[str] = None
    account_id: str
    nua_client_id: Optional[str] = None
    user_id: str
    id: str
    timestamp: datetime
    scheduled: bool = False
    completed: bool = False
    stopped: bool = False
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    failed: bool = False
    retries: int = 0
    parameters: PARAMETERS_TYPING = None
    log: Optional[str] = None


class TaskDefinition(BaseModel):
    name: TaskName
    description: Optional[str] = None
    validation: Optional[dict[str, Any]] = None


class PublicTaskConfig(BaseModel):
    task: PublicTask
    kbid: Optional[str] = None
    account_id: str
    account_type: str
    nua_client_id: Optional[str] = None
    user_id: str
    parameters: PARAMETERS_TYPING = None
    id: str
    timestamp: datetime
    defined_at: Optional[datetime] = None


class TaskList(BaseModel):
    tasks: list[TaskDefinition]
    running: list[PublicTaskRequest]
    configs: list[PublicTaskConfig]
    done: list[PublicTaskRequest]


class PublicTaskSet(BaseModel):
    request: Optional[PublicTaskRequest] = None
    config: Optional[PublicTaskConfig] = None
