import asyncio
from shared_kernel.messaging.nats_databus import NATSDataBus

databus = NATSDataBus(
    config={
        "servers": "nats://localhost:4222",
        "user": "dbiz",
        "password": "dbiz",
    },
)


async def worker(payload):
    await asyncio.sleep(2)
    print(f"Worker {payload["id"]} completed")


async def main():
    await databus.make_connection()
    await databus.subscribe_async_event("WORKER_INVOKE", worker)


if __name__ == "__main__":
    asyncio.run(main())
