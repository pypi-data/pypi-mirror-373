from os import getenv as env
from dotenv import load_dotenv

from xync_schema import models

load_dotenv()

TORM = {
    "connections": {"default": env("DB_URL")},
    "apps": {"models": {"models": [models, "aerich.models"]}},
    "use_tz": False,
    "timezone": "UTC",
}


async def main():
    import logging
    from x_model import init_db
    from logging import DEBUG

    logging.basicConfig(level=DEBUG)
    await init_db(TORM, True)


if __name__ == "__main__":
    from asyncio import run

    run(main())
