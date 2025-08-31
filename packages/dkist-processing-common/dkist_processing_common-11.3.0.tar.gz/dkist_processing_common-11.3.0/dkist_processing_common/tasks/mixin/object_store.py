"""Mixin for a WorkflowDataTaskBase subclass which implements Object Store data access functionality."""

from pathlib import Path

from object_clerk import ObjectClerk

from dkist_processing_common.config import common_configurations


class ObjectStoreMixin:
    """Mixin for a WorkflowDataTaskBase subclass which implements Object Store data access functionality."""

    @property
    def object_store_client(self) -> ObjectClerk:
        """
        Object store client.

        The object store client is additionally configured by the following environment variables:
            * MULTIPART_THRESHOLD - Threshold in bytes at which uploads are broken into multiple parts for upload. Impacts the checksum stored in the eTag
            * S3_CLIENT_CONFIG - https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html
            * S3_UPLOAD_CONFIG - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig

        """
        return ObjectClerk(
            host=common_configurations.object_store_api_mesh_service.host,
            port=common_configurations.object_store_api_mesh_service.port,
            access_key=common_configurations.object_store_access_key,
            secret_key=common_configurations.object_store_secret_key,
            retry_delay=common_configurations.retry_config.retry_delay,
            retry_backoff=common_configurations.retry_config.retry_backoff,
            retry_jitter=common_configurations.retry_config.retry_jitter,
            retry_max_delay=common_configurations.retry_config.retry_max_delay,
            retry_tries=common_configurations.retry_config.retry_tries,
            use_ssl=common_configurations.object_store_use_ssl,
        )

    def object_store_upload_movie(
        self,
        movie: Path | bytes,
        bucket: str,
        object_key: str,
        content_type: str = "video/mp4",
    ):
        """Upload a movie file to the object store."""
        self.object_store_client.upload_object(
            object_data=movie,
            bucket=bucket,
            object_key=object_key,
            verify_checksum=True,
            content_type=content_type,
            metadata={
                "groupname": "DATASET",
                "groupid": self.constants.dataset_id,
                "objecttype": "MOVIE",
            },
        )

    def object_store_remove_folder_objects(self, bucket: str, path: Path | str) -> list[str]:
        """
        Remove folder objects (end with /) in the specified bucket and path.

        Parameters
        ----------
        bucket
            S3 bucket to retrieve the object metadata from
        path
            Limits the scope of folders to removed to those of the path and below.

        Returns
        -------
        List of removed object keys
        """
        result = []
        for object_meta in self.object_store_client.list_objects(bucket=bucket, prefix=str(path)):
            object_key = object_meta["Key"]
            if object_key.endswith("/"):
                self.object_store_client.delete_object(bucket=bucket, object_key=object_key)
                result.append(object_key)
        return result
