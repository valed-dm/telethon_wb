import asyncio

from hypercorn.asyncio import serve
from hypercorn.config import Config

from app import app
from bot import start_bot


@app.before_serving
async def startup():
    asyncio.create_task(start_bot())


async def main():
    config = Config()
    config.bind = ["0.0.0.0:5000"]
    await serve(app, config)


if __name__ == "__main__":
    asyncio.run(main())
