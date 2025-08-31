"""GraphQL Data models for the metadata store api."""

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Json
from pydantic import field_serializer
from pydantic import field_validator

from dkist_processing_common.models.input_dataset import InputDatasetBaseModel
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList


class GraphqlBaseModel(BaseModel):
    """Custom BaseModel for input datasets."""

    model_config = ConfigDict(validate_assignment=True)


class RecipeRunMutation(GraphqlBaseModel):
    """Recipe run mutation record."""

    recipeRunId: int
    recipeRunStatusId: int


class RecipeRunStatusQuery(GraphqlBaseModel):
    """Recipe run status query for the recipeRunStatuses endpoint."""

    recipeRunStatusName: str


class RecipeRunStatusMutation(GraphqlBaseModel):
    """Recipe run status mutation record."""

    recipeRunStatusName: str
    isComplete: bool
    recipeRunStatusDescription: str


class RecipeRunStatusResponse(GraphqlBaseModel):
    """Response to a recipe run status query."""

    recipeRunStatusId: int


class InputDatasetPartTypeResponse(GraphqlBaseModel):
    """Response class for the input dataset part type entity."""

    inputDatasetPartTypeName: str


class InputDatasetPartResponse(InputDatasetBaseModel):
    """Response class for the input dataset part entity."""

    inputDatasetPartId: int
    # inputDatasetPartDocument : Json[InputDatasetPartDocumentList] # will work in gqlclient v2
    inputDatasetPartDocument: Json[list]
    inputDatasetPartType: InputDatasetPartTypeResponse

    @field_validator("inputDatasetPartDocument", mode="after")
    @classmethod
    def _use_frame_or_parameter_model(cls, value_list):  # not needed for gqlclient v2
        return InputDatasetPartDocumentList(doc_list=value_list)


class InputDatasetInputDatasetPartResponse(GraphqlBaseModel):
    """Response class for the join entity between input datasets and input dataset parts."""

    inputDatasetPart: InputDatasetPartResponse


class InputDatasetResponse(GraphqlBaseModel):
    """Input dataset query response."""

    inputDatasetId: int
    isActive: bool
    inputDatasetInputDatasetParts: list[InputDatasetInputDatasetPartResponse]


class InputDatasetRecipeInstanceResponse(GraphqlBaseModel):
    """Recipe instance query response."""

    inputDataset: InputDatasetResponse


class InputDatasetRecipeRunResponse(GraphqlBaseModel):
    """Recipe run query response."""

    recipeInstance: InputDatasetRecipeInstanceResponse


class RecipeInstanceResponse(GraphqlBaseModel):
    """Recipe instance query response."""

    recipeId: int
    inputDatasetId: int


class RecipeRunProvenanceResponse(GraphqlBaseModel):
    """Response for the metadata store recipeRunProvenances and mutations endpoints."""

    recipeRunProvenanceId: int
    isTaskManual: bool


class RecipeRunConfiguration(GraphqlBaseModel):
    """Response class for a recipe run configuration dictionary."""

    validate_l1_on_write: bool = True
    destination_bucket: str = "data"
    tile_size: int | None = None
    trial_directory_name: str | None = None
    trial_root_directory_name: str | None = None
    teardown_enabled: bool = True
    trial_exclusive_transfer_tag_lists: list[list[str]] | None = None


class RecipeRunResponse(GraphqlBaseModel):
    """Recipe run query response."""

    recipeInstance: RecipeInstanceResponse
    recipeInstanceId: int
    recipeRunProvenances: list[RecipeRunProvenanceResponse]
    # configuration: Json[RecipeRunConfiguration] | None # will work in gqlclient v2
    configuration: Json[dict] | None

    @field_validator("configuration", mode="after")
    @classmethod
    def _use_recipe_run_configuration_model(cls, value):  # not needed for gqlclient v2
        if value is None:
            return RecipeRunConfiguration()
        return RecipeRunConfiguration.model_validate(value)

    @field_serializer("configuration")
    def _serialize_as_basemodel(self, config: RecipeRunConfiguration):
        return config.model_dump()


class RecipeRunMutationResponse(GraphqlBaseModel):
    """Recipe run mutation response."""

    recipeRunId: int


class RecipeRunQuery(GraphqlBaseModel):
    """Query parameters for the metadata store endpoint recipeRuns."""

    recipeRunId: int


class DatasetCatalogReceiptAccountMutation(GraphqlBaseModel):
    """
    Dataset catalog receipt account mutation record.

    It sets an expected object count for a dataset so that dataset inventory creation
    doesn't happen until all objects are transferred and inventoried.
    """

    datasetId: str
    expectedObjectCount: int


class DatasetCatalogReceiptAccountResponse(GraphqlBaseModel):
    """Dataset catalog receipt account response for query and mutation endpoints."""

    datasetCatalogReceiptAccountId: int


class RecipeRunProvenanceMutation(GraphqlBaseModel):
    """Recipe run provenance mutation record."""

    inputDatasetId: int
    isTaskManual: bool
    recipeRunId: int
    taskName: str
    libraryVersions: str
    workflowVersion: str
    codeVersion: str | None = None


class QualityCreation(GraphqlBaseModel):
    """Quality data creation record."""

    datasetId: str
    metricCode: str
    facet: str | None = None
    name: str | None = None
    description: str | None = None
    statement: str | None = None
    # JSON array
    warnings: str | None = None
    # JSON objects
    plotData: str | None = None
    multiPlotData: str | None = None
    tableData: str | None = None
    histogramData: str | None = None
    modmatData: str | None = None
    raincloudData: str | None = None
    efficiencyData: str | None = None


class QualitiesRequest(GraphqlBaseModel):
    """Query parameters for quality data."""

    datasetId: str


class QualityResponse(GraphqlBaseModel):
    """Query Response for quality data."""

    qualityId: int
