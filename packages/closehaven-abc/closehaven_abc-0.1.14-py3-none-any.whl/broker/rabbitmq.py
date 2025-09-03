import asyncio
from functools import wraps
from uuid import uuid4

from aio_pika import ExchangeType, Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage

APP, suffix, url, connection = ("", "", "", None)
registerd_consumers = []
futures = {}


def set_future_result(correlation_id: str, value):
    global futures
    if correlation_id in futures:
        future: asyncio.Future = futures.pop(correlation_id)
        future.set_result(value)


async def message_consumer(
    func,
    exchange_name: str | None = None,
    exchange_type: ExchangeType = ExchangeType.DIRECT,
    queue_name: str | None = None,
    routing_key: str | None = None,
    no_ack: bool = False,
    durable: bool = False,
    exclusive: bool = False,
):
    try:
        global connection
        if connection is None:
            raise Exception("RabbitMQ connection not initialized")

        async with connection.channel() as channel:
            await channel.set_qos(prefetch_count=1)

            if queue_name is not None:
                queue = await channel.declare_queue(
                    name=queue_name, durable=durable, exclusive=exclusive
                )
            else:
                queue = await channel.declare_queue(
                    durable=durable, exclusive=exclusive
                )

            if exchange_name is not None:
                exchange = await channel.declare_exchange(exchange_name, exchange_type)

            if routing_key is not None:
                await queue.bind(exchange, routing_key=routing_key)
            else:
                await queue.bind(exchange)

            async with queue.iterator(no_ack=no_ack) as qiterator:
                message: AbstractIncomingMessage
                async for message in qiterator:
                    await func(message)

    except Exception as e:
        raise e


async def publish(
    payload: bytes,
    exchange_name: str | None = None,
    exchange_type: ExchangeType = ExchangeType.DIRECT,
    callback_queue_name: str | None = None,
    routing_key: str = None,
    rpc: bool = False,
    correlation_id: str | None = None,
):
    try:
        global connection

        if connection is None:
            raise Exception("RabbitMQ connection not initialized")

        new_routing_key = routing_key if routing_key is None else routing_key + suffix

        async with connection.channel() as channel:
            await channel.set_qos(prefetch_count=1)

            if exchange_name is not None:
                exchange = await channel.declare_exchange(exchange_name, exchange_type)
            else:
                exchange = channel.default_exchange

            if not rpc:
                await exchange.publish(
                    Message(payload, correlation_id=correlation_id, app_id=APP),
                    routing_key=new_routing_key,
                )
            else:
                global futures

                if correlation_id is None:
                    correlation_id = str(uuid4())

                future = asyncio.get_running_loop().create_future()

                futures[correlation_id] = future

                await exchange.publish(
                    Message(
                        payload,
                        correlation_id=correlation_id,
                        reply_to=callback_queue_name,
                        content_type="text/plain",
                        app_id=APP,
                    ),
                    routing_key=new_routing_key,
                )

                return await future
    except Exception as e:
        raise e


def consumer(
    exchange_name: str | None = None,
    exchange_type: ExchangeType = ExchangeType.DIRECT,
    queue_name: str | None = None,
    routing_key: str | None = None,
    no_ack: bool = False,
    durable: bool = False,
    exclusive: bool = False,
):
    def decorator(func):
        global registerd_consumers

        new_queue_name = queue_name if queue_name is None else queue_name + suffix
        new_routing_key = routing_key if routing_key is None else routing_key + suffix

        registerd_consumers.append(
            {
                "exchange_name": exchange_name,
                "exchange_type": exchange_type,
                "queue_name": new_queue_name,
                "routing_key": new_routing_key,
                "func": func,
                "no_ack": no_ack,
                "durable": durable,
                "exclusive": exclusive,
            }
        )

        @wraps(func)
        async def wrapper():
            await message_consumer(
                func,
                exchange_name,
                exchange_type,
                new_queue_name,
                new_routing_key,
                no_ack,
                durable,
                exclusive,
            )

        return wrapper

    return decorator


async def init():
    global connection

    if url is None:
        raise Exception("RABBITMQ_URL not set")

    connection = await connect_robust(url, loop=asyncio.get_running_loop())
    for c in registerd_consumers:
        asyncio.ensure_future(message_consumer(**c))


async def close():
    global connection
    if connection is not None:
        await connection.close()


def update_config(rabbitmq_setup_data: dict):
    global APP, suffix, url

    APP, suffix, url = (
        rabbitmq_setup_data.get("app"),
        rabbitmq_setup_data.get("suffix"),
        rabbitmq_setup_data.get("url"),
    )
    if APP is None:
        raise Exception("APP not set")
