"""Mixin to add methods to a Task to support globus transfers."""

import logging
from dataclasses import dataclass
from pathlib import Path

from globus_sdk import ClientCredentialsAuthorizer
from globus_sdk import ConfidentialAppAuthClient
from globus_sdk import GlobusError
from globus_sdk import TransferClient
from globus_sdk import TransferData

from dkist_processing_common.config import common_configurations

logger = logging.getLogger(__name__)


@dataclass
class GlobusTransferItem:
    """Dataclass used to support globus transfers."""

    source_path: str | Path
    destination_path: str | Path
    recursive: bool = False  # file

    def __hash__(self) -> int:
        """Hash so we can do set stuff on these items."""
        return hash((self.source_path, self.destination_path, self.recursive))


class GlobusMixin:
    """Mixin to add methods to a Task to support globus transfers."""

    @property
    def globus_transfer_client(self) -> TransferClient:
        """Get the globus transfer client, creating it if it doesn't exist."""
        if getattr(self, "_globus_transfer_client", False):
            return self._globus_transfer_client
        confidential_client = ConfidentialAppAuthClient(
            client_id=common_configurations.globus_client_id,
            client_secret=common_configurations.globus_client_secret,
            transport_params=common_configurations.globus_transport_params,
        )
        authorizer = ClientCredentialsAuthorizer(
            confidential_client, scopes="urn:globus:auth:scope:transfer.api.globus.org:all"
        )
        self._globus_transfer_client = TransferClient(authorizer=authorizer)
        return self._globus_transfer_client

    def globus_transfer_scratch_to_object_store(
        self,
        transfer_items: list[GlobusTransferItem],
        label: str = None,
        sync_level: str = None,
        verify_checksum: bool = True,
    ) -> None:
        """Transfer data from scratch to the object store."""
        self.globus_transfer(
            source_endpoint=common_configurations.scratch_endpoint,
            destination_endpoint=common_configurations.object_store_endpoint,
            transfer_items=transfer_items,
            label=label,
            sync_level=sync_level,
            verify_checksum=verify_checksum,
        )

    def globus_transfer_object_store_to_scratch(
        self,
        transfer_items: list[GlobusTransferItem],
        label: str = None,
        sync_level: str = None,
        verify_checksum: bool = True,
    ) -> None:
        """Transfer data from the object store to scratch."""
        self.globus_transfer(
            source_endpoint=common_configurations.object_store_endpoint,
            destination_endpoint=common_configurations.scratch_endpoint,
            transfer_items=transfer_items,
            label=label,
            sync_level=sync_level,
            verify_checksum=verify_checksum,
        )

    def _globus_format_transfer_data(
        self,
        source_endpoint: str,
        destination_endpoint: str,
        transfer_items: list[GlobusTransferItem],
        label: str = None,
        sync_level: str = None,
        verify_checksum: bool = True,
    ) -> TransferData:
        """Format a globus TransferData instance."""
        transfer_data = self._globus_transfer_configuration(
            source_endpoint=source_endpoint,
            destination_endpoint=destination_endpoint,
            label=label,
            sync_level=sync_level,
            verify_checksum=verify_checksum,
        )
        for item in transfer_items:
            transfer_data.add_item(
                source_path=str(item.source_path),
                destination_path=str(item.destination_path),
                recursive=item.recursive,
            )
        return transfer_data

    def globus_transfer(
        self,
        source_endpoint: str,
        destination_endpoint: str,
        transfer_items: list[GlobusTransferItem],
        label: str = None,
        sync_level: str = None,
        verify_checksum: bool = True,
    ) -> None:
        """Perform a transfer of data using globus."""
        transfer_data = self._globus_format_transfer_data(
            source_endpoint=source_endpoint,
            destination_endpoint=destination_endpoint,
            transfer_items=transfer_items,
            label=label,
            sync_level=sync_level,
            verify_checksum=verify_checksum,
        )
        self._blocking_globus_transfer(transfer_data=transfer_data)

    def _globus_transfer_configuration(
        self,
        source_endpoint: str,
        destination_endpoint: str,
        label: str = None,
        sync_level: str = None,
        verify_checksum: bool = True,
    ) -> TransferData:
        label = label or "Data Processing Transfer"
        return TransferData(
            transfer_client=self.globus_transfer_client,
            source_endpoint=source_endpoint,
            destination_endpoint=destination_endpoint,
            label=label,
            sync_level=sync_level,
            verify_checksum=verify_checksum,
        )

    def _blocking_globus_transfer(self, transfer_data: TransferData) -> None:
        tc = self.globus_transfer_client
        logger.info(f"Starting globus transfer: label={transfer_data.get('label')}")
        transfer_result = tc.submit_transfer(transfer_data)
        task_id = transfer_result["task_id"]
        polling_interval = 60
        while not tc.task_wait(
            task_id=task_id, timeout=polling_interval, polling_interval=polling_interval
        ):
            events = list(tc.task_event_list(task_id=task_id, limit=1))
            if not events:
                logger.info(
                    f"Transfer task not started: recipe_run_id={self.recipe_run_id}, {task_id=}"
                )
                continue
            last_event = events[0]
            log_message = (
                f"Transfer status: {last_event=}, recipe_run_id={self.recipe_run_id}, {task_id=}"
            )
            if last_event["is_error"]:
                logger.warning(log_message)
            else:
                logger.info(log_message)
        task = tc.get_task(task_id)
        status = task["status"]
        if status != "SUCCEEDED":
            message = f"Transfer unsuccessful: {task=}, recipe_run_id={self.recipe_run_id}"
            logger.error(message)
            raise GlobusError(message)
        logger.info(
            f"Transfer Completed Successfully: recipe_run_id={self.recipe_run_id}, {task_id=}"
        )
