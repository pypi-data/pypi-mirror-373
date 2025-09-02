import asyncio

from kelvin.application import KelvinApp
from kelvin.logs import logger


async def main() -> None:
    app = KelvinApp()

    await app.connect()

    while True:
        # Custom Loop
        logger.debug("My APP is running!")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
