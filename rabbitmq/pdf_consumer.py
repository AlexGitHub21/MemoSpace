import aio_pika
import asyncio
import json
from dotenv import load_dotenv
import os
from apps.core.core_dependency.redis_dependency import RedisDependency
from apps.core.core_dependency.db_dependency import DBDependency
from apps.crud_notes.managers import NoteManager


load_dotenv()
RMUSER = os.getenv("RMUSER")
RMPASSWORD = os.getenv("RMPASSWORD")
RMHOST = os.getenv("RMHOST", "localhost")
RMPORT = os.getenv("RMPORT", "5672")

async def process_message(
        message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    async with message.process(requeue=True):
        data = json.loads(message.body)

        note_manager = NoteManager(
            db=DBDependency(),
            redis=RedisDependency()
        )

        user_id = int(data["user_id"])
        note_id = int(data["note_id"])

        note = await note_manager.get_note(user_id, note_id)
        print(note)
        # if not note:
        #     return pass
        #
        # generate_pdf(note)


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