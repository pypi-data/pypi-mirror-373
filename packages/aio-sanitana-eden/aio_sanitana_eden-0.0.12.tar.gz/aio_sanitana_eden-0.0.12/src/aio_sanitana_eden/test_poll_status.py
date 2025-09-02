import asyncio
from .sanitana_eden import SanitanaEden
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


async def main():
    eden = SanitanaEden("192.168.2.15", 2000, reconnect_interval=5, poll_interval=1)

    def cb():
        logger.info("Callback triggered")
        logger.info("Available: %s", eden.available)
        logger.info("State: %s", eden._state)

    eden.add_listener(cb)
    await eden.async_setup()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        await eden.async_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
