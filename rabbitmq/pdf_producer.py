import json
import aio_pika
from dotenv import load_dotenv
import os

load_dotenv()
RMUSER = os.getenv("RMUSER")
RMPASSWORD = os.getenv("RMPASSWORD")
RMHOST = os.getenv("RMHOST", "localhost")
RMPORT = os.getenv("RMPORT", "5672")


async def publish_pdf_task(user_id: int, note_id: int):
    connection = await aio_pika.connect_robust(f"amqp://{RMUSER}:{RMPASSWORD}@{RMHOST}:{RMPORT}/")

    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            name="pdf_exchange",
            type=aio_pika.ExchangeType.DIRECT,
            durable=True
        )
        message = {
            "user_id": user_id,
            "note_id": note_id
        }

        await exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode(),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                        routing_key="pdf"
        )
        print("Message sent")

# if __name__ == "__main__":
#     asyncio.run(publish_pdf_task())