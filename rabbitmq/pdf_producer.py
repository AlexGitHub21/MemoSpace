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


async def main() -> None:
    connection = await aio_pika.connect_robust(f"amqp://{RMUSER}:{RMPASSWORD}@{RMHOST}:{RMPORT}/")

    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            name="pdf_exchange",
            type=aio_pika.ExchangeType.DIRECT,
            durable=True
        )

        await exchange.publish(
            aio_pika.Message(body=f"Generate pdf".encode()),
                             routing_key="pdf",
        )
        print("Message sent")

if __name__ == "__main__":
    asyncio.run(main())