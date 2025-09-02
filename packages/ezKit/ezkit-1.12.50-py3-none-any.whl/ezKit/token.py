"""Token Library"""

import json
from typing import Any

from loguru import logger

from . import cipher, utils


def generate_token(
    key: str = "Fc0zXCmGKd7tPu6W", timeout: int = 3600, data: Any = None
) -> str | None:
    try:
        now = utils.datetime_now()

        if now is None:
            return None

        offset = utils.datetime_offset(now, seconds=+timeout)

        if offset is None:
            return None

        source = json.dumps(
            obj={"datetime": utils.datetime_to_string(offset), "data": data},
            default=str,
        )

        aes_cipher = cipher.AESCipher(key=key, algorithm="sha256")

        return aes_cipher.encrypt(source)

    except Exception as e:
        logger.exception(e)
        return None


def parsing_token(token_string: str, key: str = "Fc0zXCmGKd7tPu6W") -> dict | None:
    try:
        if not utils.isTrue(token_string, str):
            return None

        aes_cipher = cipher.AESCipher(key=key, algorithm="sha256")

        target = aes_cipher.decrypt(token_string)

        if target is None:
            return None

        source: dict = json.loads(target)

        source["datetime"] = utils.datetime_string_to_datetime(source["datetime"])

        return source

    except Exception as e:
        logger.exception(e)
        return None


def certify_token(token_string: str, key: str = "Fc0zXCmGKd7tPu6W") -> bool:
    try:

        result = parsing_token(token_string, key)

        if result is None:
            return False

        if result.get("datetime") < utils.datetime_now():  # type: ignore
            return False

        return True

    except Exception as e:
        logger.exception(e)
        return False
