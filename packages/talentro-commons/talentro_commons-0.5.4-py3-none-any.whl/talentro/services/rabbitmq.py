import asyncio
import json
import os

import aio_pika

from ..event import Message, Queue, Event
from ..util.singleton import SingletonMeta


class RabbitMQ:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            host=os.getenv('QUEUE_HOST'),
            port=int(os.getenv('QUEUE_PORT')),
            login=os.getenv('QUEUE_USER'),
            password=os.getenv('QUEUE_PASS'),
        )
        print(f"  RabbitMQ - Connected!")
        self.channel = await self.connection.channel()
        print(f"  RabbitMQ - Channel created!")

    async def consume(self, queue: Queue, callback):
        print(f"  RabbitMQ - Consuming from queue: {queue}")
        queue_object = await self.channel.declare_queue(queue, durable=True)
        async for message in queue_object:
            async with message.process():
                event: Event = Event(**json.loads(message.body))
                print(f"  RabbitMQ ({queue}) - [x] Received event with type: {event.event_type}")
                await callback(queue, event)

    async def send_message(self, message: Message):
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=message.event.encode()),
            routing_key=message.queue
        )
        print(f"  RabbitMQ ({message.queue.name}) - [x] Sent event with type: '{message.event.event_type}'")


class QueueContext(metaclass=SingletonMeta):

    def __init__(self):
        self._rabbit_mq = RabbitMQ()
        self._message_callbacks = []

    async def connect(self):
        await self._rabbit_mq.connect()

    async def start_consuming(self, queue: Queue):
        asyncio.create_task(
            self._rabbit_mq.consume(queue, self._on_new_message)
        )

    async def _on_new_message(self, queue: Queue, event: Event):
        for callback_object in self._message_callbacks:
            if callback_object.get("queue") == queue:
                await callback_object.get("callback")(event)

    def add_on_message_callback(self, queue: Queue, callback):
        self._message_callbacks.append({'queue': queue, 'callback': callback})

    async def send_message(self, message: Message):
        await self._rabbit_mq.send_message(message)