"""Tests for the interservice bus mixin for a WorkflowDataTaskBase subclass"""

from typing import Type
from uuid import uuid4

import pytest
from pydantic import BaseModel
from pydantic import Field
from talus import Binding
from talus import ConsumeMessageBase
from talus import DurableConsumer
from talus import DurableProducer
from talus import Exchange
from talus import MessageBodyBase
from talus import PublishMessageBase
from talus import Queue


@pytest.fixture
def sample_message_body():
    """Sample message body class"""

    class SampleMessageBody(MessageBodyBase):
        objectName: str = "test_isb_mixin_objectName"
        bucket: str = "test_isb_mixin_bucket"

    return SampleMessageBody


@pytest.fixture
def sample_message(sample_message_body):
    """Instance of a sample message class with attributes for publishing and consuming"""

    class SampleMessage(BaseModel):
        queue: Queue = Queue(name=f"isb_test_queue_{uuid4().hex[:6]}")
        exchange: Exchange = Exchange(name=f"isb_test_exchange_{uuid4().hex[:6]}")
        body_cls: Type = sample_message_body
        body: MessageBodyBase = sample_message_body()

    sample_message = SampleMessage()

    return sample_message


@pytest.fixture
def publish_message(sample_message):
    class PublishMessage(PublishMessageBase):
        message_body_cls = sample_message.body_cls

    return PublishMessage


@pytest.fixture
def consume_message(sample_message):
    class ConsumeMessage(ConsumeMessageBase):
        message_body_cls = sample_message.body_cls

    return ConsumeMessage


@pytest.fixture
def producer(sample_message, publish_message):
    exchange = sample_message.exchange
    binding = Binding(queue=sample_message.queue, message=publish_message)
    with DurableProducer(queue_bindings=binding, publish_exchange=exchange) as p:
        yield p
        p.channel.queue_delete(queue=sample_message.queue.name)
        p.channel.exchange_delete(exchange=sample_message.exchange.name)


@pytest.fixture
def consumer(sample_message):
    queue = sample_message.queue
    with DurableConsumer(consume_queue=queue, prefetch_count=100) as c:
        yield c
        c.channel.queue_delete(queue=sample_message.queue.name)
        c.channel.exchange_delete(exchange=sample_message.exchange.name)


def test_isb(sample_message, producer, publish_message, consumer, consume_message):
    """
    Given: a test message and a test exchange and queue on the ISB
    When: the message is published to the queue
    Then: consume the message, confirm it is the same message, and delete the test exchange and queue
    """
    # Given: sample_message
    # When:
    p = producer
    sent = publish_message(sample_message.body)
    p.publish(sent)
    # Then:
    c = consumer
    for method, properties, body in c.consume_generator(auto_ack=True):
        received = consume_message(method=method, properties=properties, body=body)
        assert received.body == sent.body
        c.cancel_consume_generator()
