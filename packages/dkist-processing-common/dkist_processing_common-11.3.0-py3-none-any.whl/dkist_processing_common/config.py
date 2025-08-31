"""Common configurations."""

from dkist_processing_core.config import DKISTProcessingCoreConfiguration
from dkist_service_configuration.settings import DEFAULT_MESH_SERVICE
from dkist_service_configuration.settings import MeshService
from pydantic import BaseModel
from pydantic import Field
from talus import ConnectionRetryerFactory
from talus import ConsumerConnectionParameterFactory
from talus import ProducerConnectionParameterFactory


class RetryConfig(BaseModel):
    """Retry metadata model."""

    retry_delay: int = 1
    retry_backoff: int = 2
    retry_jitter: tuple[int, int] = (1, 10)
    retry_max_delay: int = 300
    retry_tries: int = -1


class DKISTProcessingCommonConfiguration(DKISTProcessingCoreConfiguration):
    """Common configurations."""

    retry_config: RetryConfig = Field(default_factory=RetryConfig)
    # metadata-store-api
    gql_auth_token: str | None = None
    # object-store-api
    object_store_access_key: str | None = None
    object_store_secret_key: str | None = None
    object_store_use_ssl: bool = False
    multipart_threshold: int | None = None
    s3_client_config: dict | None = None
    s3_upload_config: dict | None = None
    s3_download_config: dict | None = None
    # globus
    globus_transport_params: dict = Field(default_factory=dict)
    globus_client_id: str | None = None
    globus_client_secret: str | None = None
    object_store_endpoint: str | None = None
    scratch_endpoint: str | None = None
    # scratch
    scratch_base_path: str = Field(default="scratch/")
    scratch_inventory_db_count: int = 16
    # docs
    docs_base_url: str = Field(default="my_test_url")

    @property
    def metadata_store_api_base(self) -> str:
        """Metadata store api url."""
        gateway = self.service_mesh_detail(service_name="internal-api-gateway")
        return f"http://{gateway.host}:{gateway.port}/graphql"

    @property
    def object_store_api_mesh_service(self) -> MeshService:
        """Object store host and port."""
        return self.service_mesh_detail(service_name="object-store-api")

    @property
    def scratch_inventory_mesh_service(self) -> MeshService:
        """Scratch inventory host and port."""
        mesh = self.service_mesh_detail(service_name="automated-processing-scratch-inventory")
        if mesh == DEFAULT_MESH_SERVICE:
            return MeshService(mesh_address="localhost", mesh_port=6379)  # testing default
        return mesh

    @property
    def scratch_inventory_max_db_index(self) -> int:
        """Scratch inventory's largest db index."""
        return self.scratch_inventory_db_count - 1

    @property
    def isb_producer_connection_parameters(self) -> ProducerConnectionParameterFactory:
        """Return the connection parameters for the ISB producer."""
        return ProducerConnectionParameterFactory(
            rabbitmq_host=self.isb_mesh_service.host,
            rabbitmq_port=self.isb_mesh_service.port,
            rabbitmq_user=self.isb_username,
            rabbitmq_pass=self.isb_password,
            connection_name="dkist-processing-common-producer",
        )

    @property
    def isb_consumer_connection_parameters(self) -> ConsumerConnectionParameterFactory:
        """Return the connection parameters for the ISB producer."""
        return ConsumerConnectionParameterFactory(
            rabbitmq_host=self.isb_mesh_service.host,
            rabbitmq_port=self.isb_mesh_service.port,
            rabbitmq_user=self.isb_username,
            rabbitmq_pass=self.isb_password,
            connection_name="dkist-processing-common-consumer",
        )

    @property
    def isb_connection_retryer(self) -> ConnectionRetryerFactory:
        """Return the connection retryer for the ISB connection."""
        return ConnectionRetryerFactory(
            delay_min=self.retry_config.retry_delay,
            delay_max=self.retry_config.retry_max_delay,
            backoff=self.retry_config.retry_backoff,
            jitter_min=self.retry_config.retry_jitter[0],
            jitter_max=self.retry_config.retry_jitter[1],
            attempts=self.retry_config.retry_tries,
        )


common_configurations = DKISTProcessingCommonConfiguration()
common_configurations.log_configurations()
