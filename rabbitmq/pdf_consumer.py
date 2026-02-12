import aio_pika
import asyncio
import json
from apps.core.core_dependency.redis_dependency import RedisDependency
from apps.core.core_dependency.db_dependency import DBDependency
from apps.crud_notes.managers import NoteManager
from apps.auth.managers import UserManager
from apps.core.settings import rabbit_settings
from apps.pdf_process.generate_pdf import generate_html


async def process_message(
        message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    async with message.process(requeue=True):
        data = json.loads(message.body)

        note_manager = NoteManager(
            db=DBDependency(),
            redis=RedisDependency()
        )
        user_manager = UserManager(
            db=DBDependency(),
            redis=RedisDependency()
        )

        user_id = int(data["user_id"])
        note_id = int(data["note_id"])

        note = await note_manager.get_note(user_id, note_id)
        author_login = await user_manager.get_user_by_id(user_id)
        author_login = author_login.email

        await generate_html(note, author_login)


async def main() -> None:
    connection = await aio_pika.connect_robust(f"amqp://{rabbit_settings.RMUSER}:{rabbit_settings.RMPASSWORD}@{rabbit_settings.RMHOST}:{rabbit_settings.RMPORT}/")

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