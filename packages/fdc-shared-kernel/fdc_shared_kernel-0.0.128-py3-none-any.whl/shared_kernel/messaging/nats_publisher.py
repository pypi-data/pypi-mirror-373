import asyncio
from shared_kernel.messaging.nats_databus import NATSDataBus

databus = NATSDataBus(
    config={
        "servers": "nats://localhost:4222",
        "user": "dbiz",
        "password": "dbiz",
    },
)


async def main():
    await databus.make_connection()
    await databus.publish_event("WORKER_INVOKE", {"id": 4})
    await databus.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
