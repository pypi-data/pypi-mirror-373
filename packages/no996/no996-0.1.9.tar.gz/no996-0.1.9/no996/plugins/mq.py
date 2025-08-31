import json
from typing import Any, Dict, List, Union

import aio_pika
import structlog
from aio_pika.abc import AbstractConnection
from aio_pika.pool import Pool

from no996.base.config import settings

logger = structlog.get_logger(__name__)


class MQ(object):
    _instance = None
    _connection_pool = None
    _channel_pools = {}
    _logger = logger

    def __new__(cls) -> "MQ":
        if cls._instance is None:
            cls._instance = super(MQ, cls).__new__(cls)
            cls._settings = settings
            cls._logger.info("MQ instance created")
        return cls._instance

    @classmethod
    async def get_connection_pool(cls) -> Pool:
        if cls._connection_pool is None:
            cls._connection_pool = Pool(
                cls._get_connection,
                max_size=5,  # Adjust pool size as needed
            )
            cls._logger.info("MQ connection pool established")
        return cls._connection_pool

    @classmethod
    async def _get_connection(cls) -> AbstractConnection:
        return await aio_pika.connect_robust(str(settings.AMQP_URI))

    @classmethod
    async def get_channel_pool(cls, connection: AbstractConnection) -> Pool:
        connection_id = id(connection)
        if connection_id not in cls._channel_pools:
            cls._channel_pools[connection_id] = Pool(
                connection.channel,
                max_size=10,  # Adjust channel pool size as needed
            )
        return cls._channel_pools[connection_id]

    @classmethod
    async def close(cls):
        if cls._channel_pools:
            for pool in cls._channel_pools.values():
                await pool.close()
            cls._channel_pools.clear()
        if cls._connection_pool is not None:
            await cls._connection_pool.close()
            cls._connection_pool = None
            cls._logger.info("MQ pools closed")

    async def publish_message(
        self, exchange_name: str, routing_key: str, message: Dict[str, Any]
    ):
        """Publish message to specified exchange and routing"""
        connection_pool = await self.get_connection_pool()
        async with connection_pool.acquire() as connection:
            channel_pool = await self.get_channel_pool(connection)
            async with channel_pool.acquire() as channel:
                # Declare exchange
                exchange = await channel.declare_exchange(
                    exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
                )

                # Convert message to JSON and send
                message_body = json.dumps(message).encode()
                await exchange.publish(
                    aio_pika.Message(
                        body=message_body,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    ),
                    routing_key=routing_key,
                )

                self._logger.info(
                    f"Published message to {exchange_name} with routing key {routing_key}"
                )

    async def consume_messages(
        self,
        queue_name: str,
        callback,
        routing_keys: Union[List[str], str] = [],
        exchange_name: str = None,
    ):
        """Consume messages from specified queue"""
        connection_pool = await self.get_connection_pool()
        async with connection_pool.acquire() as connection:
            channel_pool = await self.get_channel_pool(connection)
            async with channel_pool.acquire() as channel:
                await channel.set_qos(prefetch_count=1)

                # Handle exchange and routing key binding if specified
                if exchange_name and routing_keys:
                    exchange = await channel.declare_exchange(
                        exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
                    )

                    queue = await channel.declare_queue(queue_name, durable=True)

                    if isinstance(routing_keys, str):
                        routing_keys = [routing_keys]

                    for routing_key in routing_keys:
                        await queue.bind(exchange, routing_key)
                else:
                    queue = await channel.declare_queue(queue_name, durable=True)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        # 当代码块执行完成后，会自动确认(ack)消息
                        # 如果代码块执行过程中抛出异常，消息会被自动拒绝(nack)
                        async with message.process():
                            logger.info(f"Received message: {message.body.decode()}")
                            data = json.loads(message.body.decode())
                            await callback(data)
