"""Tests for the interservice bus mixin for a WorkflowDataTaskBase subclass"""

import logging
from typing import Dict
from typing import Type

import pytest
from pydantic import BaseModel
from talus import ConsumeMessageBase
from talus import DurableConsumer
from talus import Exchange
from talus import MessageBodyBase
from talus import Queue

from dkist_processing_common.config import common_configurations
from dkist_processing_common.models.message_queue_binding import common_message_queue_bindings
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.interservice_bus import InterserviceBusMixin

logger = logging.getLogger(__name__)


@pytest.fixture
def isb_task(recipe_run_id):
    class IsbTask(WorkflowTaskBase, InterserviceBusMixin):
        def run(self):
            pass

    with IsbTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        yield task
        task._purge()


@pytest.fixture
def sample_message_body():
    """Sample message body class that will pass validation of all the possible Task message body types"""

    class SampleMessageBody(MessageBodyBase):
        objectType: str = "test_isb_mixin_objectType"
        objectName: str = "test_isb_mixin_objectName"
        bucket: str = "test_isb_mixin_bucket"
        groupId: str = "test_isb_mixin_groupId"
        datasetId: str = "test_isb_mixin_datasetId"

    return SampleMessageBody


@pytest.fixture(
    params=common_message_queue_bindings,
    ids=[binding.queue.name for binding in common_message_queue_bindings],
)
def task_message(request, sample_message_body):
    """Instance of a class with specific attributes for publishing and consuming Task messages"""

    class TaskMessage(BaseModel):
        queue: Queue = request.param.queue
        exchange: Exchange = common_configurations.isb_publish_exchange
        message_cls: Type = request.param.message
        body_cls: Type = request.param.message.message_body_cls
        body_dict: Dict[str, str] = sample_message_body().model_dump()

    task_message = TaskMessage()

    return task_message


@pytest.fixture
def consume_message(task_message):
    class ConsumeMessage(ConsumeMessageBase):
        message_body_cls = task_message.body_cls

    return ConsumeMessage


@pytest.fixture
def consumer(task_message):
    queue = task_message.queue
    with DurableConsumer(consume_queue=queue, prefetch_count=100) as c:
        yield c
        # Clean up all the queues, skipping queues that are not empty:
        for binding in common_message_queue_bindings:
            q = c.channel.queue_declare(queue=binding.queue.name, durable=True)
            count = q.method.message_count
            if count == 0:
                c.channel.queue_delete(queue=binding.queue.name)
                logger.info(f"Queue {binding.queue.name} is deleted")
            if count != 0:
                logger.info(
                    f"Queue {binding.queue.name} is not deleted because there are {count} messages on the queue"
                )


def test_isb_mixin(isb_task, task_message, consumer, consume_message):
    """
    Given: a task from a class with the ISB mixin
    When: publishing one of the message types with that task
    Then: find the message, ack the message, and leave the queue intact in case a parallel test is using it
    """
    # Given:
    task = isb_task
    # When:
    body = task_message.body_cls(**task_message.body_dict)
    sent = task_message.message_cls(body)
    task.interservice_bus_publish([sent])
    # Then:
    message_found = False
    c = consumer
    for method, properties, body in c.consume_generator(auto_ack=False):
        received = consume_message(method=method, properties=properties, body=body)
        if received.body == sent.body:
            message_found = True
            c.acknowledge_message(received.delivery_tag)
            c.cancel_consume_generator()
        if received.body != sent.body:
            c.requeue_message(received.delivery_tag)
    assert message_found is True
