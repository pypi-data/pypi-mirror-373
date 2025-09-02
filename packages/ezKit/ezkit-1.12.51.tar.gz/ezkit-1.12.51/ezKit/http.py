"""HTTP Library"""

import json
from typing import Any

import requests
from loguru import logger

from . import utils


def download(
    request: dict,
    file: dict,
    chunks: bool = False,
    iter_content: dict | None = None,
    info: str | None = None,
) -> bool:
    """下载文件"""

    if utils.isTrue(request, dict):
        request_arguments = {"method": "GET", "stream": True, **request}
    else:
        return False

    if utils.isTrue(file, dict):
        file_arguments = {"mode": "wb", **file}
    else:
        return False

    if iter_content is not None and utils.isTrue(iter_content, dict):
        iter_content_arguments = {"chunk_size": 1024, **iter_content}
    else:
        iter_content_arguments = {"chunk_size": 1024}

    info_prefix: str = "Download"
    if utils.isTrue(info, str):
        info_prefix = f"Download {info}"

    try:

        logger.info(f"{info_prefix} ......")

        response = requests.request(**request_arguments)

        # # pylint: disable=W1514
        with open(**file_arguments) as _file:  # type: ignore

            if utils.isTrue(chunks, bool):
                for _chunk in response.iter_content(**iter_content_arguments):  # type: ignore
                    _file.write(_chunk)
            else:
                _file.write(response.content)

        logger.success(f"{info_prefix} [success]")

        return True

    except Exception as e:

        logger.error(f"{info_prefix} [failed]")
        logger.exception(e)
        return False


def response_json(data: Any = None, **kwargs) -> str | None:
    """解决字符编码问题: ensure_ascii=False"""
    try:
        return json.dumps(
            data, default=str, ensure_ascii=False, sort_keys=True, **kwargs
        )
    except Exception as e:
        logger.exception(e)
        return None
