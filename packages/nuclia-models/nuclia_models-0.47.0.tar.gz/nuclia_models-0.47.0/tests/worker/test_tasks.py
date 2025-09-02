import pytest
from pydantic_core import ValidationError

from nuclia_models.worker.proto import Filter, LLMConfig, Operation
from nuclia_models.worker.tasks import (  # type: ignore
    ApplyTo,
    DataAugmentation,
    SemanticModelMigrationParams,
    TaskName,
    TaskStart,
)


def test_task_validation() -> None:
    # Test case 1: DUMMY task accepts None parameters
    _ = TaskStart(name=TaskName.DUMMY, parameters=None)
    with pytest.raises(ValidationError):
        # Test case 2: ASK task doesn't accept None parameters
        _ = TaskStart(name=TaskName.ASK, parameters=None)
    with pytest.raises(ValidationError):
        # Test case 3: SEMANTIC_MODEL_MIGRATOR task doesn't accept None parameters
        _ = TaskStart(name=TaskName.SEMANTIC_MODEL_MIGRATOR, parameters=None)

    with pytest.raises(ValidationError):
        # Test case 4: DUMMY task doesn't accept not None parameters
        _ = TaskStart(
            name=TaskName.DUMMY, parameters=SemanticModelMigrationParams(semantic_model_id="testid")
        )
    with pytest.raises(ValidationError):
        # Test case 5: At least one operation must be defined for ASK task
        _ = TaskStart(
            name=TaskName.ASK,
            parameters=DataAugmentation(
                name="test", on=ApplyTo.FIELD, filter=Filter(), operations=[], llm=LLMConfig()
            ),
        )
    # Test case 6: ASK task with correct parameters
    _ = TaskStart(
        name=TaskName.ASK,
        parameters=DataAugmentation(
            name="test", on=ApplyTo.FIELD, filter=Filter(), operations=[Operation()], llm=LLMConfig()
        ),
    )
    # Test case 7: SEMANTIC_MODEL_MIGRATOR task with correct parameters
    _ = TaskStart(
        name=TaskName.SEMANTIC_MODEL_MIGRATOR,
        parameters=SemanticModelMigrationParams(semantic_model_id="testid"),
    )
