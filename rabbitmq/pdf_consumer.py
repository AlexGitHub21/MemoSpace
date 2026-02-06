import aio_pika
import asyncio
from aio_pika import connect, Message
from dotenv import load_dotenv
import os

load_dotenv()
RMUSER = os.getenv("RMUSER")
RMPASSWORD = os.getenv("RMPASSWORD")
RMHOST = os.getenv("RMHOST", "localhost")
RMPORT = os.getenv("RMPORT", "5672")

async def process_message(
        message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    async with message.process(requeue=True):
        print(message.body.decode())
        await asyncio.sleep(1)

async def main() -> None:
    connection = await aio_pika.connect_robust(f"amqp://{RMUSER}:{RMPASSWORD}@{RMHOST}:{RMPORT}/")

    queue_name = "pdf_queue"
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=1)

    exchange = await channel.declare_exchange(
        name="pdf_exchange",
        type=aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    queue = await channel.declare_queue(queue_name, durable=True)

    await queue.bind(exchange, routing_key="pdf")

    await queue.consume(process_message)

    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())