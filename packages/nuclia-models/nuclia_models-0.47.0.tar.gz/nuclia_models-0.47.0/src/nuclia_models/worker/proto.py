# ruff: noqa: UP006
# ruff: noqa: E501
import typing
from datetime import datetime
from enum import IntEnum

from pydantic import BaseModel, ConfigDict, Field

# The models from this file are generated from private protos
# Here we just duplicate the models


###
#    learning_protos/config_p2p.py
###


class SimilarityFunction(IntEnum):
    """
    Keep this in sync with learning_models.encoder.SemanticConfig
    """

    DOT = 0
    COSINE = 1


class ResponseStatus(IntEnum):
    OK = 0
    ERROR = 1
    VALIDATION_ERROR = 2
    NOT_FOUND = 3


class ModelType(IntEnum):
    """
    ALERT: needs to be synched to learning_config/models/ModelTypes
    """

    GENERATIVE = 0
    NER = 1
    RESOURCE_LABELER = 2
    CLASSIFIER = 3
    ANONYMIZER = 4
    VISUAL_LABELER = 5
    SUMMARY = 6
    DUMMY = 7
    PARAGRAPH_LABELER = 8
    EMBEDDINGS = 9
    RELATIONS = 10


class OpenAIKey(BaseModel):
    key: str = Field(default="")
    org: str = Field(default="")


class AzureOpenAIKey(BaseModel):
    key: str = Field(default="")
    url: str = Field(default="")
    deployment: str = Field(default="")
    model: str = Field(default="")


class HFLLMKey(BaseModel):
    class ModelType(IntEnum):
        LLAMA31 = 0
        QWEN25 = 1

    key: str = Field(default="")
    url: str = Field(default="")
    model: "HFLLMKey.ModelType" = Field(default=ModelType.LLAMA31)


class AzureMistralKey(BaseModel):
    key: str = Field(default="")
    url: str = Field(default="")


class PalmKey(BaseModel):
    credentials: str = Field(default="")
    location: str = Field(default="")


class MistralKey(BaseModel):
    key: str = Field(default="")


class AnthropicKey(BaseModel):
    key: str = Field(default="")


class TextGenerationKey(BaseModel):
    model: str = Field(default="")


class HFEmbeddingKey(BaseModel):
    """
         Some models require a specific template (including prefix) to work correctly in each task
    For example Snowflake's Arctic-embed requires a specific prefix to work correctly.
    In that case, the query prompt will be
    ```
    passage_prompt: ""
    query_prompt: "Represent this sentence for searching relevant passages: {}"
    ````
    where {} will be replaced by the actual sentence.
    `passage_prompt` is empty because the model does not require alterations to the sentence to embed is as a passage.
    """

    url: str = Field(default="")
    key: str = Field(default="")
    matryoshka: typing.List[int] = Field(default_factory=list)
    similarity: str = Field(default="")
    size: int = Field(default=0)
    threshold: float = Field(default=0.0)
    passage_prompt: str = Field(default="")
    query_prompt: str = Field(default="")


class UserLearningKeys(BaseModel):
    openai: typing.Optional[OpenAIKey] = Field(default=None)
    azure_openai: typing.Optional[AzureOpenAIKey] = Field(default=None)
    palm: typing.Optional[PalmKey] = Field(default=None)
    anthropic: typing.Optional[AnthropicKey] = Field(default=None)
    claude3: typing.Optional[AnthropicKey] = Field(default=None)
    text_generation: typing.Optional[TextGenerationKey] = Field(default=None)
    mistral: typing.Optional[MistralKey] = Field(default=None)
    azure_mistral: typing.Optional[AzureMistralKey] = Field(default=None)
    hf_llm: typing.Optional[HFLLMKey] = Field(default=None)
    hf_embedding: typing.Optional[HFEmbeddingKey] = Field(default=None)


class OpenAIUserPrompt(BaseModel):
    system: str = Field(default="")
    prompt: str = Field(default="")


class AzureUserPrompt(BaseModel):
    system: str = Field(default="")
    prompt: str = Field(default="")


class HFUserPrompt(BaseModel):
    system: str = Field(default="")
    prompt: str = Field(default="")


class PalmUserPrompt(BaseModel):
    prompt: str = Field(default="")


class AnthropicUserPrompt(BaseModel):
    prompt: str = Field(default="")


class Claude3UserPrompt(BaseModel):
    system: str = Field(default="")
    prompt: str = Field(default="")


class TextGenerationUserPrompt(BaseModel):
    prompt: str = Field(default="")


class MistralUserPrompt(BaseModel):
    prompt: str = Field(default="")


class AzureMistralUserPrompt(BaseModel):
    prompt: str = Field(default="")


class SummaryPrompt(BaseModel):
    prompt: str = Field(default="")


class UserPrompts(BaseModel):
    openai: typing.Optional[OpenAIUserPrompt] = Field(default=None)
    azure_openai: typing.Optional[AzureUserPrompt] = Field(default=None)
    palm: typing.Optional[PalmUserPrompt] = Field(default=None)
    anthropic: typing.Optional[AnthropicUserPrompt] = Field(default=None)
    text_generation: typing.Optional[TextGenerationUserPrompt] = Field(default=None)
    mistral: typing.Optional[MistralUserPrompt] = Field(default=None)
    azure_mistral: typing.Optional[AzureMistralUserPrompt] = Field(default=None)
    claude3: typing.Optional[Claude3UserPrompt] = Field(default=None)


class SemanticConfig(BaseModel):
    """
    Keep this in sync with learning_models.encoder.SemanticConfig
    """

    # Similarity function to use for semantic similarity
    similarity: SimilarityFunction = Field(default=SimilarityFunction.DOT)
    # Number of dimensions of the embeddings
    size: int = Field(default=0)
    # Similarity threshold to use at search time, results with a similarity below this threshold will be discarded
    threshold: float = Field(default=0.0)
    # Maximum number of tokens in a sentence that the model can handle
    max_tokens: int = Field(default=0)
    # Subdivisions of the matryoshka embeddings that can be used (if the model supports it), in descending order
    matryoshka_dims: typing.List[int] = Field(default_factory=list)
    # Whether the model is external
    external: bool = Field(default=False)


class LearningConfiguration(BaseModel):
    """
    Hey, developer! Keep this in sync with corresponding pydantic model in learning_config.models
    """

    semantic_model: str = Field(default="")
    anonymization_model: str = Field(default="")
    ner_model: str = Field(default="")
    visual_labeling: str = Field(default="")
    relation_model: str = Field(default="")
    summary: str = Field(default="")
    summary_model: str = Field(default="")
    summary_provider: str = Field(default="")
    summary_prompt_id: str = Field(default="")
    summary_prompt: SummaryPrompt = Field()
    user_keys: UserLearningKeys = Field()
    user_prompts: UserPrompts = Field()
    prefer_markdown_generative_response: bool = Field(default=False)
    semantic_models: typing.List[str] = Field(default_factory=list)
    semantic_model_configs: typing.Dict[str, SemanticConfig] = Field(default_factory=dict)
    default_semantic_model: str = Field(default="")
    generative_model: str = Field(default="")
    generative_provider: str = Field(default="")
    generative_prompt_id: str = Field(default="")


class AddKBConfigRequest(BaseModel):
    kbid: str = Field(default="")
    account: str = Field(default="")
    config: LearningConfiguration = Field()


class UpdateKBConfigRequest(BaseModel):
    kbid: str = Field(default="")
    config: LearningConfiguration = Field()


class UpdateKBConfigResponse(BaseModel):
    status: ResponseStatus = Field(default=ResponseStatus.OK)


class DeleteKBConfigRequest(BaseModel):
    kbid: str = Field(default="")


class DeleteKBConfigResponse(BaseModel):
    status: ResponseStatus = Field(default=ResponseStatus.OK)


class GetKBConfigRequest(BaseModel):
    kbid: str = Field(default="")


class GetExternalKBConfigRequest(BaseModel):
    account: str = Field(default="")
    kbid: str = Field(default="")


class GetKBConfigResponse(BaseModel):
    status: ResponseStatus = Field(default=ResponseStatus.OK)
    config: LearningConfiguration = Field()
    semantic_vector_similarity: str = Field(default="")
    semantic_vector_size: int = Field(default=0)
    semantic_threshold: float = Field(default=0.0)
    errors: typing.List[str] = Field(default_factory=list)
    semantic_matryoshka_dimensions: typing.List[int] = Field(default_factory=list)


class AddModelRequest(BaseModel):
    model_type: ModelType = Field(default=ModelType.GENERATIVE)
    trained_date: datetime = Field(default_factory=datetime.now)
    location: str = Field(default="")
    log: str = Field(default="")
    loss: float = Field(default=0.0)
    accuracy: float = Field(default=0.0)
    account: str = Field(default="")
    trained_kbid: str = Field(default="")
    model_uuid: str = Field(default="")
    trained_dataset: str = Field(default="")
    title: str = Field(default="")


class AddModelResponse(BaseModel):
    uuid: str = Field(default="")


class DeleteModelRequest(BaseModel):
    model_id: str = Field(default="")
    account_id: str = Field(default="")


class DeleteModelResponse(BaseModel):
    pass


class GetModelsRequest(BaseModel):
    kbid: str = Field(default="")


class GetExternalModelsRequest(BaseModel):
    kbid: str = Field(default="")
    account: str = Field(default="")


class Model(BaseModel):
    model_type: ModelType = Field(default=ModelType.GENERATIVE)
    trained_date: datetime = Field(default_factory=datetime.now)
    model_id: str = Field(default="")
    account: str = Field(default="")
    trained_kbid: str = Field(default="")
    trained_dataset: str = Field(default="")
    title: str = Field(default="")
    provider: str = Field(default="")
    prompt_id: str = Field(default="")
    kbids: typing.List[str] = Field(default_factory=list)


class GetModelsResponse(BaseModel):
    models: typing.List[Model] = Field(default_factory=list)


class SetAvailableModelsRequest(BaseModel):
    kbid: str = Field(default="")
    models: typing.List[str] = Field(default_factory=list)


class SetAvailableModelsResponse(BaseModel):
    pass


class GetModelRequest(BaseModel):
    model_id: str = Field(default="")


class GetAccountModelsRequest(BaseModel):
    account: str = Field(default="")
    client_id: str = Field(default="")


class GetModelResponse(BaseModel):
    model_type: ModelType = Field(default=ModelType.GENERATIVE)
    trained_date: datetime = Field(default_factory=datetime.now)
    location: str = Field(default="")
    log: str = Field(default="")
    loss: float = Field(default=0.0)
    accuracy: float = Field(default=0.0)
    account: str = Field(default="")
    trained_kbid: str = Field(default="")
    model_id: str = Field(default="")
    kbids: typing.List[str] = Field(default_factory=list)


class DeleteTrainedModelsOfAccountRequest(BaseModel):
    account: str = Field(default="")


class DeleteTrainedModelsOfAccountResponse(BaseModel):
    class Status(IntEnum):
        OK = 0
        ERROR = 1

    status: "DeleteTrainedModelsOfAccountResponse.Status" = Field(default=Status.OK)


###
#    learning_protos/data_augmentation_p2p.py
###


class ApplyTo(IntEnum):
    TEXT_BLOCK = 0
    FIELD = 1


class KBConfiguration(BaseModel):
    account: str = Field(default="")
    kbid: str = Field(default="")
    onprem: bool = Field(default=False)


class Trigger(BaseModel):
    url: str = Field(default="")
    headers: typing.Dict[str, str] = Field(default_factory=dict)
    params: typing.Dict[str, str] = Field(default_factory=dict)


class EntityDefinition(BaseModel):
    label: str = Field(description="Entity type")
    description: typing.Optional[str] = Field(default="", description="Description of the entity type")


class EntityExample(BaseModel):
    name: str = Field(description="Name associated with the entity")
    label: str = Field(description="Type of entity")


class RelationExample(BaseModel):
    source: str = Field(description="Entity name from which the relation starts")
    target: str = Field(description="Entity name to which the relation ends")
    label: str = Field(description="Type of relation")


class GraphExtractionExample(BaseModel):
    entities: typing.List[EntityExample] = Field(
        description="Examples of entities extracted from the example text"
    )
    relations: typing.List[RelationExample] = Field(
        description="Examples of relations extracted from the example text, all entities must be included in the entities list"
    )
    text: str = Field(description="Example text where entities and relations were extracted")


class GraphOperation(BaseModel):
    entity_defs: typing.List[EntityDefinition] = Field(
        default_factory=list,
        description="Types of entities that will be considered for extraction",
    )
    examples: typing.List[GraphExtractionExample] = Field(
        default_factory=list,
        description="Examples to be sent to the model as few-shot learning",
    )
    ident: str = Field(title="ID of Operation, Will be used to tag the extracted entities and relationships")
    triggers: typing.List[Trigger] = Field(
        default_factory=list, title="Triggers to execute when the operation is executed"
    )


class Label(BaseModel):
    label: str = Field(title="Label Name")
    description: str = Field(default="", title="Description of the Label")
    examples: typing.List[str] = Field(default_factory=list)


class LabelOperation(BaseModel):
    labels: typing.List[Label] = Field(default_factory=list)
    ident: str = Field(title="ID of Operation, Will be used to name the generated Label Set")
    description: str = Field(
        default="",
        title="Description of the Operation, will be used to describe to the model the task at hand",
    )
    multiple: bool = Field(default=False)
    triggers: typing.List[Trigger] = Field(
        default_factory=list, title="Triggers to execute when the operation is executed"
    )


class GuardOperation(BaseModel):
    enabled: bool = Field(default=False)
    triggers: typing.List[Trigger] = Field(
        default_factory=list, title="Triggers to execute when the operation is executed"
    )


class AskOperation(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    question: str = Field(title="Question")
    destination: str = Field(title="Destination")
    generate_json: bool = Field(default=False, alias="json")
    triggers: typing.List[Trigger] = Field(
        default_factory=list, title="Triggers to execute when the operation is executed"
    )
    user_prompt: str = Field(
        default="",
        title="Custom User Prompt",
        description="Prompt to use when executing the agent over a field, it must include the {context} placeholder and optionally the {question} placeholder if you wish. If not given, the default prompt will be used. Only supported when `json` is not set",
    )


class QAOperation(BaseModel):
    question_generator_prompt: str = Field(default="")
    system_question_generator_prompt: str = Field(default="")
    summary_prompt: str = Field(default="")
    generate_answers_prompt: str = Field(default="")
    triggers: typing.List[Trigger] = Field(
        default_factory=list, title="Triggers to execute when the operation is executed"
    )


class ExtractOperation(BaseModel):
    class Model(IntEnum):
        TABLES = 0

    model: "ExtractOperation.Model" = Field(default=Model.TABLES)
    triggers: typing.List[Trigger] = Field(
        default_factory=list, title="Triggers to execute when the operation is executed"
    )


class Operation(BaseModel):
    graph: typing.Optional[GraphOperation] = Field(default=None, title="Graph Config")
    label: typing.Optional[LabelOperation] = Field(default=None, title="Label Config")
    ask: typing.Optional[AskOperation] = Field(default=None, title="Ask Config")
    qa: typing.Optional[QAOperation] = Field(default=None, title="QA Config")
    extract: typing.Optional[ExtractOperation] = Field(default=None, title="Extract Config")
    prompt_guard: typing.Optional[GuardOperation] = Field(default=None, title="Prompt Guard Config")
    llama_guard: typing.Optional[GuardOperation] = Field(default=None, title="Llama Guard Config")


class FilterLogicalOperator(IntEnum):
    AND = 0
    OR = 1


class Filter(BaseModel):
    contains: typing.List[str] = Field(
        default_factory=list,
        description="Text that must be contained in the field in order to apply the data augmentation, if multiple values are provided, at least one must be present",
    )
    resource_type: typing.List[str] = Field(
        default_factory=list,
        description="Data Augmentation will only be applied to resources of the specified types",
    )
    field_types: typing.List[str] = Field(
        default_factory=list,
        description="Data Augmentation will only be applied to fields of the specified types",
    )
    not_field_types: typing.List[str] = Field(
        default_factory=list,
        description="Data Augmentation will not be applied to fields of the specified types",
    )
    rids: typing.List[str] = Field(
        default_factory=list,
        description="Data Augmentation will only be applied resources matching the specified resource ids",
    )
    fields: typing.List[str] = Field(
        default_factory=list,
        description="Data Augmentation will only be applied to fields matching the specified field ids",
    )
    splits: typing.List[str] = Field(
        default_factory=list,
        description="Data Augmentation will only be applied to fields matching the specified field splits",
    )
    labels: typing.List[str] = Field(
        default_factory=list,
        description="Data Augmentation will only be applied to fields matching the specified labels",
    )
    apply_to_agent_generated_fields: bool = Field(
        default=False,
        description="If enabled, the data augmentation will also be applied to fields generated by other data augmentation agents. This functionality is only supported for agents that do not generate fields.",
    )
    contains_operator: FilterLogicalOperator = Field(
        default=FilterLogicalOperator.AND, description="Way of combining the values in the contains field"
    )
    labels_operator: FilterLogicalOperator = Field(
        default=FilterLogicalOperator.AND, description="Way of combining the values in the labels field"
    )


class LLMConfig(BaseModel):
    model: str = Field(default="")
    provider: str = Field(default="")
    keys: typing.Optional[UserLearningKeys] = Field(default=None)
    prompts: typing.Optional[UserPrompts] = Field(default=None)


class DataAugmentation(BaseModel):
    # If you modify this proto remember to update nuclia-models repo accordingly
    name: str = Field(default="")
    on: ApplyTo = Field(
        default=ApplyTo.TEXT_BLOCK,
        title="ApplyTo",
        description="Defines if the task should be applied to paragraphs (0) or whole fields (1)",
    )
    filter: typing.Optional[Filter] = Field(default=None, description="Filter to apply the data augmentation")
    operations: typing.List[Operation] = Field(default_factory=list)
    llm: LLMConfig = Field()


class DataAugmentations(BaseModel):
    class Status(IntEnum):
        FOUND = 0
        NOT_FOUND = 1

    data_augmentations: typing.List[DataAugmentation] = Field(default_factory=list)
    status: "DataAugmentations.Status" = Field(default=Status.FOUND)
