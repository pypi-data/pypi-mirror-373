"""Bottle Extensions"""

from types import FunctionType
from typing import Any

from . import bottle, utils


def enable_cors(fn: FunctionType) -> Any | None:
    """Bottle CORS"""

    # 参考文档:
    # - https://stackoverflow.com/a/17262900
    # - https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Headers
    # - https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Methods
    # - https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin
    def cors(*args, **kwargs):
        bottle.response.headers["Access-Control-Allow-Headers"] = "*"
        bottle.response.headers["Access-Control-Allow-Methods"] = "*"
        bottle.response.headers["Access-Control-Allow-Origin"] = "*"
        if bottle.request.method != "OPTIONS":
            return fn(*args, **kwargs)
        return None

    return cors


def request_json() -> bottle.DictProperty | None:
    """Bottle Request JSON"""
    try:
        data = bottle.request.json
        if utils.isTrue(data, dict):
            return data
        return None
    except Exception as e:
        print(e)
        return None
