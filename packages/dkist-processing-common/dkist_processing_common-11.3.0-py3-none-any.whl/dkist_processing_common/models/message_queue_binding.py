"""Binding between a queue and a message to be published."""

from talus import Binding
from talus import Queue

from dkist_processing_common.config import common_configurations
from dkist_processing_common.models.message import CatalogFrameMessage
from dkist_processing_common.models.message import CatalogObjectMessage
from dkist_processing_common.models.message import CreateQualityReportMessage

catalog_frame_queue = Queue(
    name="catalog.frame.q", arguments=common_configurations.isb_queue_arguments
)
catalog_object_queue = Queue(
    name="catalog.object.q", arguments=common_configurations.isb_queue_arguments
)
create_quality_report_queue = Queue(
    name="create.quality.report.q", arguments=common_configurations.isb_queue_arguments
)

common_message_queue_bindings = [
    Binding(queue=catalog_frame_queue, message=CatalogFrameMessage),
    Binding(queue=catalog_object_queue, message=CatalogObjectMessage),
    Binding(queue=create_quality_report_queue, message=CreateQualityReportMessage),
]
