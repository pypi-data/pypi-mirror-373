"""Data structures for messages placed on the interservice bus."""

from typing import Type

from pydantic import Field
from talus import MessageBodyBase
from talus import PublishMessageBase

########################
# Message Body Schemas #
########################


class CatalogFrameMessageBody(MessageBodyBase):
    """Schema for the catalog frame message body."""

    objectName: str
    bucket: str
    incrementDatasetCatalogReceiptCount: bool = True


class CatalogObjectMessageBody(MessageBodyBase):
    """Schema for the catalog object message body."""

    objectType: str
    objectName: str
    bucket: str
    groupId: str
    groupName: str = Field(default="DATASET")
    incrementDatasetCatalogReceiptCount: bool = True


class CreateQualityReportMessageBody(MessageBodyBase):
    """Schema for the create quality report message body."""

    datasetId: str
    bucket: str
    objectName: str
    incrementDatasetCatalogReceiptCount: bool = True


###################
# Message Classes #
###################


class CatalogFrameMessage(PublishMessageBase):
    """Catalog frame message."""

    message_body_cls: Type[CatalogFrameMessageBody] = CatalogFrameMessageBody
    default_routing_key = "catalog.frame.m"


class CatalogObjectMessage(PublishMessageBase):
    """Catalog object message."""

    message_body_cls: Type[CatalogObjectMessageBody] = CatalogObjectMessageBody
    default_routing_key = "catalog.object.m"


class CreateQualityReportMessage(PublishMessageBase):
    """Create quality report message."""

    message_body_cls: Type[CreateQualityReportMessageBody] = CreateQualityReportMessageBody
    default_routing_key = "create.quality.report.m"
