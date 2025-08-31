"""Mixin for a WorkflowDataTaskBase subclass which implements interservice bus access functionality."""

from talus import DurableProducer
from talus import PublishMessageBase

from dkist_processing_common.config import common_configurations
from dkist_processing_common.models.message_queue_binding import common_message_queue_bindings


class InterserviceBusMixin:
    """Mixin for a WorkflowDataTaskBase subclass which implements interservice bus access functionality."""

    @staticmethod
    def interservice_bus_publish(messages: list[PublishMessageBase] | PublishMessageBase) -> None:
        """Publish messages on the interservice bus."""
        with DurableProducer(
            queue_bindings=common_message_queue_bindings,
            publish_exchange=common_configurations.isb_publish_exchange,
            connection_parameters=common_configurations.isb_producer_connection_parameters,
            connection_retryer=common_configurations.isb_connection_retryer,
        ) as producer:
            for message in messages:
                producer.publish(message)
