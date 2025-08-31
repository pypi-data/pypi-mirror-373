"""Mixin for a WorkflowDataTaskBase subclass which implements Metadata Store data access functionality."""

import json
import logging
from functools import cached_property
from typing import Literal

from pydantic import validate_call

from dkist_processing_common._util.graphql import GraphQLClient
from dkist_processing_common.codecs.quality import QualityDataEncoder
from dkist_processing_common.config import common_configurations
from dkist_processing_common.models.graphql import DatasetCatalogReceiptAccountMutation
from dkist_processing_common.models.graphql import DatasetCatalogReceiptAccountResponse
from dkist_processing_common.models.graphql import InputDatasetPartResponse
from dkist_processing_common.models.graphql import InputDatasetRecipeRunResponse
from dkist_processing_common.models.graphql import QualitiesRequest
from dkist_processing_common.models.graphql import QualityCreation
from dkist_processing_common.models.graphql import QualityResponse
from dkist_processing_common.models.graphql import RecipeRunMutation
from dkist_processing_common.models.graphql import RecipeRunMutationResponse
from dkist_processing_common.models.graphql import RecipeRunProvenanceMutation
from dkist_processing_common.models.graphql import RecipeRunProvenanceResponse
from dkist_processing_common.models.graphql import RecipeRunQuery
from dkist_processing_common.models.graphql import RecipeRunResponse
from dkist_processing_common.models.graphql import RecipeRunStatusMutation
from dkist_processing_common.models.graphql import RecipeRunStatusQuery
from dkist_processing_common.models.graphql import RecipeRunStatusResponse

logger = logging.getLogger(__name__)


class MetadataStoreMixin:
    """Mixin for a WorkflowDataTaskBase which implements Metadata Store access functionality."""

    @property
    def metadata_store_client(self) -> GraphQLClient:
        """Get the graphql client."""
        return GraphQLClient(common_configurations.metadata_store_api_base)

    # RECIPE RUN STATUS

    def metadata_store_change_recipe_run_to_inprogress(self):
        """Set the recipe run status to "INPROGRESS"."""
        self._metadata_store_change_status(status="INPROGRESS", is_complete=False)

    def metadata_store_change_recipe_run_to_completed_successfully(self):
        """Set the recipe run status to "COMPLETEDSUCCESSFULLY"."""
        self._metadata_store_change_status(status="COMPLETEDSUCCESSFULLY", is_complete=True)

    def metadata_store_change_recipe_run_to_trial_success(self):
        """Set the recipe run status to "TRIALSUCCESS"."""
        self._metadata_store_change_status(status="TRIALSUCCESS", is_complete=False)

    def _metadata_store_recipe_run_status_id(self, status: str) -> None | int:
        """Find the id of a recipe run status."""
        params = RecipeRunStatusQuery(recipeRunStatusName=status)
        response = self.metadata_store_client.execute_gql_query(
            query_base="recipeRunStatuses",
            query_response_cls=RecipeRunStatusResponse,
            query_parameters=params,
        )
        if len(response) > 0:
            return response[0].recipeRunStatusId

    @validate_call
    def _metadata_store_create_recipe_run_status(self, status: str, is_complete: bool) -> int:
        """
        Add a new recipe run status to the db.

        :param status: name of the status to add
        :param is_complete: does the new status correspond to an accepted completion state
        """
        recipe_run_statuses = {
            "INPROGRESS": "Recipe run is currently undergoing processing",
            "COMPLETEDSUCCESSFULLY": "Recipe run processing completed with no errors",
            "TRIALSUCCESS": "Recipe run trial processing completed with no errors. Recipe run not "
            "marked complete.",
        }

        params = RecipeRunStatusMutation(
            recipeRunStatusName=status,
            isComplete=is_complete,
            recipeRunStatusDescription=recipe_run_statuses[status],
        )
        recipe_run_status_response = self.metadata_store_client.execute_gql_mutation(
            mutation_base="createRecipeRunStatus",
            mutation_response_cls=RecipeRunStatusResponse,
            mutation_parameters=params,
        )
        return recipe_run_status_response.recipeRunStatus.recipeRunStatusId

    def _metadata_store_change_status(self, status: str, is_complete: bool):
        """Change the recipe run status of a recipe run to the given status."""
        recipe_run_status_id = self._metadata_store_recipe_run_status_id(status=status)
        if not recipe_run_status_id:
            recipe_run_status_id = self._metadata_store_create_recipe_run_status(
                status=status, is_complete=is_complete
            )
        self._metadata_store_update_status(recipe_run_status_id=recipe_run_status_id)

    def _metadata_store_update_status(
        self,
        recipe_run_status_id: int,
    ):
        """
        Change the status of a given recipe run id.

        :param recipe_run_status_id: the new status to use
        """
        params = RecipeRunMutation(
            recipeRunId=self.recipe_run_id, recipeRunStatusId=recipe_run_status_id
        )
        self.metadata_store_client.execute_gql_mutation(
            mutation_base="updateRecipeRun",
            mutation_parameters=params,
            mutation_response_cls=RecipeRunMutationResponse,
        )

    # RECEIPT

    def metadata_store_add_dataset_receipt_account(
        self, dataset_id: str, expected_object_count: int
    ):
        """Set the number of expected objects."""
        params = DatasetCatalogReceiptAccountMutation(
            datasetId=dataset_id, expectedObjectCount=expected_object_count
        )
        self.metadata_store_client.execute_gql_mutation(
            mutation_base="createDatasetCatalogReceiptAccount",
            mutation_parameters=params,
            mutation_response_cls=DatasetCatalogReceiptAccountResponse,
        )

    # PROVENANCE

    def metadata_store_record_provenance(self, is_task_manual: bool, library_versions: str):
        """Record the provenance record in the metadata store."""
        params = RecipeRunProvenanceMutation(
            inputDatasetId=self.metadata_store_recipe_run.recipeInstance.inputDatasetId,
            isTaskManual=is_task_manual,
            recipeRunId=self.recipe_run_id,
            taskName=self.task_name,
            libraryVersions=library_versions,
            workflowVersion=self.workflow_version,
        )
        self.metadata_store_client.execute_gql_mutation(
            mutation_base="createRecipeRunProvenance",
            mutation_parameters=params,
            mutation_response_cls=RecipeRunProvenanceResponse,
        )

    # QUALITY

    def metadata_store_add_quality_data(self, dataset_id: str, quality_data: list[dict]):
        """Add the quality data to the metadata-store."""
        if self.metadata_store_quality_data_exists(dataset_id):
            raise RuntimeError(f"Quality data already persisted for dataset {dataset_id!r}")
        for metric in quality_data:
            if (metric_code := metric.get("metric_code")) is None:
                name = metric.get("name")
                raise ValueError(f"No metric_code for {name!r} in dataset {dataset_id!r}")
            params = QualityCreation(
                datasetId=dataset_id,
                metricCode=metric_code,
                facet=metric.get("facet"),
                name=metric.get("name"),
                description=metric.get("description"),
                statement=metric.get("statement"),
                # JSON array
                warnings=json.dumps(metric.get("warnings")),
                # JSON objects
                plotData=json.dumps(metric.get("plot_data"), cls=QualityDataEncoder),
                multiPlotData=json.dumps(metric.get("multi_plot_data"), cls=QualityDataEncoder),
                tableData=json.dumps(metric.get("table_data"), cls=QualityDataEncoder),
                histogramData=json.dumps(metric.get("histogram_data"), cls=QualityDataEncoder),
                modmatData=json.dumps(metric.get("modmat_data"), cls=QualityDataEncoder),
                raincloudData=json.dumps(metric.get("raincloud_data"), cls=QualityDataEncoder),
                efficiencyData=json.dumps(metric.get("efficiency_data"), cls=QualityDataEncoder),
            )
            self.metadata_store_client.execute_gql_mutation(
                mutation_base="createQuality",
                mutation_parameters=params,
                mutation_response_cls=QualityResponse,
            )

    def metadata_store_quality_data_exists(self, dataset_id: str) -> bool:
        """Return True if quality data exists in the metadata-store for the given dataset id."""
        params = QualitiesRequest(datasetId=dataset_id)
        response = self.metadata_store_client.execute_gql_query(
            query_base="qualities",
            query_response_cls=QualityResponse,
            query_parameters=params,
        )
        return bool(response)

    # INPUT DATASET RECIPE RUN

    @cached_property
    def metadata_store_input_dataset_recipe_run(self) -> InputDatasetRecipeRunResponse:
        """Get the input dataset recipe run response from the metadata store."""
        params = RecipeRunQuery(recipeRunId=self.recipe_run_id)
        response = self.metadata_store_client.execute_gql_query(
            query_base="recipeRuns",
            query_response_cls=InputDatasetRecipeRunResponse,
            query_parameters=params,
        )
        return response[0]

    def _metadata_store_input_dataset_part(
        self, part_type: Literal["observe_frames", "calibration_frames", "parameters"]
    ) -> InputDatasetPartResponse:
        """Get the input dataset part by input dataset part type name."""
        part_types_found = set()
        input_dataset_part = None
        parts = (
            self.metadata_store_input_dataset_recipe_run.recipeInstance.inputDataset.inputDatasetInputDatasetParts
        )
        for part in parts:
            part_type_name = part.inputDatasetPart.inputDatasetPartType.inputDatasetPartTypeName
            if part_type_name in part_types_found:
                raise ValueError(f"Multiple input dataset parts found for {part_type_name=}.")
            part_types_found.add(part_type_name)
            if part_type_name == part_type:
                input_dataset_part = part.inputDatasetPart
        return input_dataset_part

    @property
    def metadata_store_input_dataset_observe_frames(self) -> InputDatasetPartResponse:
        """Get the input dataset part for the observe frames."""
        return self._metadata_store_input_dataset_part(part_type="observe_frames")

    @property
    def metadata_store_input_dataset_calibration_frames(self) -> InputDatasetPartResponse:
        """Get the input dataset part for the calibration frames."""
        return self._metadata_store_input_dataset_part(part_type="calibration_frames")

    @property
    def metadata_store_input_dataset_parameters(self) -> InputDatasetPartResponse:
        """Get the input dataset part for the parameters."""
        return self._metadata_store_input_dataset_part(part_type="parameters")

    # RECIPE RUN

    @cached_property
    def metadata_store_recipe_run(self) -> RecipeRunResponse:
        """Get the recipe run response from the metadata store."""
        params = RecipeRunQuery(recipeRunId=self.recipe_run_id)
        response = self.metadata_store_client.execute_gql_query(
            query_base="recipeRuns",
            query_response_cls=RecipeRunResponse,
            query_parameters=params,
        )
        return response[0]
