"""Utils Library"""

import csv
import hashlib
import importlib
import importlib.util
import json
import os
import re
import subprocess
import time
import tomllib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from itertools import islice
from pathlib import Path
from shutil import rmtree
from typing import Any, Callable
from urllib.parse import ParseResult, urlparse
from uuid import uuid4

from loguru import logger

if importlib.util.find_spec("markdown"):
    import markdown  # type: ignore

# --------------------------------------------------------------------------------------------------


# None Type
# from types import NoneType


# --------------------------------------------------------------------------------------------------


def isTrue(target: object, typeClass: Any) -> bool:
    """检查对象是否为真"""

    # 常见布尔类型:
    #
    #     Boolean     bool            False
    #     Numbers     int/float       0/0.0
    #     String      str             ""
    #     List        list/tuple/set  []/()/{}
    #     Dictionary  dict            {}
    #
    # 查看变量类型: type(x)
    #
    # 判断变量类型: isinstance(x, str)
    #
    # 函数使用 callable(func) 判断
    #
    # 判断多个类型:
    #
    #   isTrue("abc", (str, int))
    #   isTrue("abc", (str | int))
    #
    # all() 用于检查一个可迭代对象(如列表、元组、集合等)中的 所有 元素是否为 真值 (truthy), 所有元素为真, 返回 True
    # any() 用于检查一个可迭代对象(如列表、元组、集合等)中的 某个 元素是否为 真值 (truthy), 某个元素为真, 返回 True
    # 与 all() 作用相反的 not any(), 可以用来检查所有元素是否为 假值 (falsy), any() 中所有元素为假, not any() 返回 True
    #
    # return target not in [False, None, 0, 0.0, '', (), [], {}, {*()}, {*[]}, {*{}}]

    try:
        return isinstance(target, typeClass) and bool(target)
    except Exception as e:
        logger.exception(e)
        return False


# --------------------------------------------------------------------------------------------------


# def check_arguments(data: list) -> bool:
#     """检查函数参数"""

#     # data 示例: [(name, str, "name"), (age, int, "age")]

#     try:
#         if not isTrue(data, list):
#             logger.error(f"argument error: data {type(data)}")
#             return False
#         for arg, arg_type, info in data:
#             if not isTrue(arg, arg_type):
#                 logger.error(f"argument error: {info} {type(arg)}")
#                 return False
#         return True
#     except Exception as e:
#         logger.exception(e)
#         return False


# --------------------------------------------------------------------------------------------------


def os_environ(name: str, value: Any = None) -> Any:
    """系统变量"""

    # 伪全局变量
    # Python 没有全局变量, 多个文件无法调用同一个变量.
    # 为了解决这个问题, 将变量设置为系统变量, 从而实现多个文件调用同一个变量.

    try:

        # 变量名添加一个前缀, 防止和系统中其它变量名冲突
        _variable_name = f"PYTHON_VARIABLE_{name}"

        # 如果 value 的值是 None, 则从系统环境获取变量数据
        if value is None:

            _data = os.environ.get(_variable_name)

            # 判断是否有数据
            if _data is None or not isTrue(_data, str):
                return None

            # 使用 json.loads() 解析数据
            parsed_data = json.loads(_data)
            return parsed_data

        # 如果 value 的值不是 None, 则保存数据到系统环境变量
        _data = json.dumps(value)
        os.environ[_variable_name] = _data

        return value

    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def mam_of_numbers(numbers: list | tuple, dest_type: str | None = None) -> tuple | None:
    """返回一组数字中的 最大值(maximum), 平均值(average), 最小值(minimum)"""

    # numbers 数字列表 (仅支持 list 和 tuple, 不支 set)
    # dest_type 目标类型 (将数字列表中的数字转换成统一的类型)

    if not any([isTrue(dest_type, str), dest_type is None]):
        logger.error("argument error: dest_type")
        return None

    try:

        _numbers = deepcopy(numbers)

        # 转换数据类型
        if dest_type == "float":
            _numbers = [float(i) for i in numbers]

        if dest_type == "int":
            _numbers = [int(i) for i in numbers]

        # 提取数据
        _num_max = max(_numbers)
        _num_avg = f"{sum(_numbers) / len(_numbers):.2f}"
        _num_min = min(_numbers)

        if dest_type == int:
            _num_avg = int(_num_avg)
        else:
            _num_avg = float(_num_avg)

            # 返回数据
        return _num_max, _num_avg, _num_min

    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def step_number_for_split_equally(integer: int, split_equally_number: int) -> int | None:
    """
    step number for split equally

    平分数字的步长

      integer 数字
      split_equally_number 平分 integer 的数字

    示例:

        [1, 2, 3, 4, 5, 6, 7, 8, 9]

        分成 2 份 -> [[1, 2, 3, 4, 5], [6, 7, 8, 9]] -> 返回 5
        分成 3 份 -> [[1, 2, 3], [4, 5, 6], [7, 8, 9]] -> 返回 3
        分成 4 份 -> [[1, 2, 3], [4, 5], [6, 7], [8, 9]] -> 返回 3
        分成 5 份 -> [[1, 2], [3, 4], [5, 6], [7, 8], [9]] -> 返回 2
    """
    try:
        if integer % split_equally_number == 0:
            return int(integer / split_equally_number)
        return int(integer / split_equally_number) + 1
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def division(dividend: int | float, divisor: int | float) -> float | None:
    """Division"""
    try:
        return dividend / divisor
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def format_float(number: float | int, index: int = 2, limit: int = 3) -> float | None:
    """格式化浮点数"""

    # 以两位和三位为例, 如果结果为假, 即: 0, 0.0, 0.00 等，保留小数点后的三位, 否则保留小数点后的两位.

    try:
        rounded_float = round(number, index)
        return rounded_float if bool(rounded_float) else round(number, limit)
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def check_file_type(file_object: str, file_type: str) -> bool:
    """检查文件类型"""

    # file_object 文件对象
    # file_type 文件类型

    try:

        _file_path = Path(file_object)

        match True:
            case True if _file_path.exists() is False:
                result = False
            case True if file_type == "absolute" and _file_path.is_absolute() is True:
                result = True
            case True if file_type == "block_device" and _file_path.is_block_device() is True:
                result = True
            case True if file_type == "dir" and _file_path.is_dir() is True:
                result = True
            case True if file_type == "fifo" and _file_path.is_fifo() is True:
                result = True
            case True if file_type == "file" and _file_path.is_file() is True:
                result = True
            case True if file_type == "mount" and _file_path.is_mount() is True:
                result = True
            # case True if (
            #     file_type == "relative_to" and _file_path.is_relative_to() is True
            # ):
            #     result = True
            case True if file_type == "reserved" and _file_path.is_reserved() is True:
                result = True
            case True if file_type == "socket" and _file_path.is_socket() is True:
                result = True
            case True if file_type == "symlink" and _file_path.is_symlink() is True:
                result = True
            case _:
                result = False

        return result

    except Exception as e:
        logger.exception(e)
        return False


# --------------------------------------------------------------------------------------------------


def list_sort(data: list, deduplication: bool = False, **kwargs) -> list | None:
    """list sort"""
    # 列表排序, 示例: list_sort(['1.2.3.4', '2.3.4.5'], key=inet_aton)
    # 参考文档:
    #     https://stackoverflow.com/a/4183538
    #     https://blog.csdn.net/u013541325/article/details/117530957
    try:

        # from ipaddress import ip_address
        # _ips = [str(i) for i in sorted(ip_address(ip.strip()) for ip in ips)]
        # 注意: list.sort() 是直接改变 list, 不会返回 list

        # 拷贝数据, 去重, 排序, 返回
        _data = deepcopy(data)
        if deduplication is True:
            _data = list(set(_data))
        _data.sort(**kwargs)
        return _data

    except Exception as e:
        logger.exception(e)
        return None


def list_dict_sorted_by_key(data: list | tuple, key: str, **kwargs) -> list | None:
    """list dict sorted by key"""
    # 列表字典排序
    # 参考文档: https://stackoverflow.com/a/73050
    try:
        _data = deepcopy(data)
        return sorted(_data, key=lambda x: x[key], **kwargs)
    except Exception as e:
        logger.exception(e)
        return None


def list_split(data: list, number: int, equally: bool = False) -> list | None:
    """列表分割"""

    # 列表分割
    #
    # 默认: 将 list 以 number 个元素为一个子 list 分割
    #
    #   data = [1, 2, 3, 4, 5, 6, 7]                                奇数个元素
    #   list_split(data, 2) -> [[1, 2], [3, 4], [5, 6], [7]]        将 data 以 2个元素 为一个 list 分割
    #   list_split(data, 3) -> [[1, 2, 3], [4, 5, 6], [7]]          将 data 以 3个元素 为一个 list 分割
    #
    #   data = [1, 2, 3, 4, 5, 6, 7, 8]                             偶数个元素
    #   list_split(data, 2) -> [[1, 2], [3, 4], [5, 6], [7, 8]]     将 data 以 2个元素 为一个 list 分割
    #   list_split(data, 3) -> [[1, 2, 3], [4, 5, 6], [7, 8]]       将 data 以 3个元素 为一个 list 分割
    #
    # equally 为 True 时, 将 list 平均分成 number 个元素的子 list
    #
    #   data = [1, 2, 3, 4, 5, 6, 7]                                奇数个元素
    #   list_split(data, 2, True) -> [[1, 2, 3, 4], [5, 6, 7]]      将 data 平均分成 2个子list
    #   list_split(data, 3, True) -> [[1, 2, 3], [4, 5, 6], [7]]    将 data 平均分成 3个子list
    #
    #   data = [1, 2, 3, 4, 5, 6, 7, 8]                             偶数个元素
    #   list_split(data, 2, True) -> [[1, 2, 3, 4], [5, 6, 7, 8]]   将 data 平均分成 2个子list
    #   list_split(data, 3, True) -> [[1, 2, 3], [4, 5, 6], [7, 8]] 将 data 平均分成 3个子list

    try:

        # 要将列表平均分成 n 个子列表
        if isTrue(equally, bool):
            it = iter(data)
            chunk_size = (len(data) + number - 1) // number  # 每组至少多少个元素
            return [list(islice(it, chunk_size)) for _ in range(number)]

        # 将列表按每 n 个元素为一个列表进行分割
        it = iter(data)
        return [list(islice(it, number)) for _ in range((len(data) + number - 1) // number)]

    except Exception as e:
        logger.exception(e)
        return None


def list_print_by_step(data: list, step: int, separator: str = " ") -> bool:
    """根据 步长 和 分隔符 有规律的打印列表中的数据"""

    try:

        # 打印
        for i, v in enumerate(data):

            if i > 0 and i % step == 0:
                print()

            # print(v, end=separator)

            # 每行最后一个 或者 所有数据最后一个, 不打印分隔符
            if ((i % step) == (step - 1)) or ((i + 1) == len(data)):
                print(v, end="")
            else:
                print(v, end=separator)

        print()

        return True

    except Exception as e:
        logger.exception(e)
        return False


def list_remove_list(original: list, remove: list) -> list | None:
    """List remove List"""
    try:
        _original = deepcopy(original)
        _remove = deepcopy(remove)
        return [i for i in _original if i not in _remove]
    except Exception as e:
        logger.exception(e)
        return None


def list_merge(data: list) -> list | None:
    """list merge"""
    # 合并 List 中的 List 为一个 List
    try:
        _results = []
        for i in deepcopy(data):
            _results += i
        return _results
    except Exception as e:
        logger.exception(e)
        return None


def list_to_file(data: list, file: str, encoding: str = "utf-8-sig") -> bool:
    """list to file"""
    try:
        with open(file, "w", encoding=encoding) as _file:
            for line in data:
                _file.write(f"{line}\n")
        return True
    except Exception as e:
        logger.exception(e)
        return False


def list_to_csvfile(
    data: list,
    file: str,
    fields: list | None = None,
    encoding: str = "utf-8-sig",
    **kwargs,
) -> bool:
    """list to csvfile"""
    try:
        with open(file, "w", encoding=encoding) as _file:
            # CRLF replaced by LF
            # https://stackoverflow.com/a/29976091
            outcsv = csv.writer(_file, lineterminator=os.linesep, **kwargs)
            if fields is not None and isTrue(fields, list):
                outcsv.writerow(fields)
            outcsv.writerows(data)
        return True
    except Exception as e:
        logger.exception(e)
        return False


def range_zfill(start: int, stop: int, step: int, width: int) -> list | None:
    """range zfill"""
    # 生成长度相同的字符串的列表
    # 示例: range_zfill(8, 13, 1, 2) => ['08', '09', '10', '11', '12']
    # 生成 小时 列表: range_zfill(0, 24, 1, 2)
    # 生成 分钟和秒 列表: range_zfill(0, 60, 1, 2)
    # https://stackoverflow.com/a/733478
    # the zfill() method to pad a string with zeros
    try:
        return [str(i).zfill(width) for i in range(start, stop, step)]
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def dict_remove_key(data: dict, key: str) -> dict | None:
    """dict remove key"""
    try:
        data_copy: dict = deepcopy(data)
        data_copy.pop(key)
        return data_copy
    except Exception as e:
        logger.exception(e)
        return None


def dict_to_file(data: dict, file: str, encoding: str = "utf-8-sig", **kwargs) -> bool:
    """dict to file"""
    try:
        with open(file, "w", encoding=encoding) as _file:
            json.dump(obj=data, fp=_file, indent=4, sort_keys=True, **kwargs)
        return True
    except Exception as e:
        logger.exception(e)
        return False


def dict_nested_update(data: dict, key: str, value: Any) -> bool:
    """dict nested update"""
    # dictionary nested update
    # https://stackoverflow.com/a/58885744
    try:

        if not isTrue(data, dict):
            return False

        for _k, _v in data.items():
            # callable() 判断是非为 function
            if (key is not None and key == _k) or (callable(key) is True and key == _k):
                if callable(value) is True:
                    data[_k] = value()
                else:
                    data[_k] = value
            elif isTrue(_v, dict):
                dict_nested_update(_v, key, value)
            elif isTrue(_v, list):
                for _o in _v:
                    if isTrue(_o, dict):
                        dict_nested_update(_o, key, value)
            else:
                pass

        return True

    except Exception as e:
        logger.exception(e)
        return False


# --------------------------------------------------------------------------------------------------


def filename(file: str, split: str = ".") -> str | None:
    """filename"""
    # 获取文件名称
    # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python
    # https://stackoverflow.com/questions/4152963/get-name-of-current-script-in-python
    try:
        _basename = str(os.path.basename(file))
        _index_of_split = _basename.index(split)
        return _basename[:_index_of_split]
    except Exception as e:
        logger.exception(e)
        return None


def filehash(file: str, sha: str = "md5") -> str | None:
    """filehash"""
    # 获取文件Hash
    # 参考文档:
    #     https://stackoverflow.com/a/59056837
    #     https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    try:
        with open(file, "rb") as _file:
            match True:
                case True if sha == "sha1":
                    file_hash = hashlib.sha1()
                case True if sha == "sha224":
                    file_hash = hashlib.sha224()
                case True if sha == "sha256":
                    file_hash = hashlib.sha256()
                case True if sha == "sha384":
                    file_hash = hashlib.sha384()
                case True if sha == "sha512":
                    file_hash = hashlib.sha512()
                case True if sha == "sha3_224":
                    file_hash = hashlib.sha3_224()
                case True if sha == "sha3_256":
                    file_hash = hashlib.sha3_256()
                case True if sha == "sha3_384":
                    file_hash = hashlib.sha3_384()
                case True if sha == "sha3_512":
                    file_hash = hashlib.sha3_512()
                # case True if sha == 'shake_128':
                #     file_hash = hashlib.shake_128()
                # case True if sha == 'shake_256':
                #     file_hash = hashlib.shake_256()
                case _:
                    file_hash = hashlib.md5()
            # 建议设置为和 block size 相同的值, 多数系统默认为 4096, 可使用 stat 命令查看
            # stat / (IO Block)
            # stat -f / (Block size)
            while chunk := _file.read(4096):
                file_hash.update(chunk)
            return file_hash.hexdigest()
    except Exception as e:
        logger.exception(e)
        return None


def filesize(file: str) -> int | None:
    """filesize"""
    # 获取文件大小
    try:
        return os.path.getsize(file)
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


# def resolve_path() -> str | None:
#     """resolve path"""
#     # 获取当前目录名称
#     return str(Path().resolve())


# def parent_path(
#     path: str,
#     debug: bool = False,
#     **kwargs
# ) -> str | None:
#     """获取父目录名称"""
#     try:
#         return str(Path(path, **kwargs).parent.resolve()) if isTrue(path, str, debug=debug) else None
#     except Exception as e:
#         if isTrue(debug, bool):
#             logger.exception(e)
#         return None


def realpath(path: str, **kwargs) -> str | None:
    """获取对象真实路径"""
    try:
        if not isTrue(path, str):
            return None
        return str(Path(path, **kwargs).resolve())
    except Exception as e:
        logger.exception(e)
        return None


def current_dir(path: str, **kwargs) -> str | None:
    """获取对象所在目录"""
    try:
        if not isTrue(path, str):
            return None
        return str(Path(path, **kwargs).parent.resolve())
    except Exception as e:
        logger.exception(e)
        return None


def parent_dir(path: str, **kwargs) -> str | None:
    """获取对象所在目录的父目录"""
    try:
        if not isTrue(path, str):
            return None
        return str(Path(path, **kwargs).parent.parent.resolve())
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def retry(func: Callable, times: int = 3, **kwargs) -> Any:
    """重试"""

    # 函数传递参数: https://stackoverflow.com/a/803632
    # callable() 判断类型是非为函数: https://stackoverflow.com/a/624939

    for attempt in range(times):
        try:
            # 执行函数并结果
            return func(**kwargs)
        except Exception as e:
            logger.exception(e)
            if attempt < (times - 1):
                logger.info("retrying ...")
            else:
                logger.error("all retries failed")
                return False


# --------------------------------------------------------------------------------------------------

# 日期时间有两种: UTC datetime (UTC时区日期时间) 和 Local datetime (当前时区日期时间)
#
# Unix Timestamp 仅为 UTC datetime 的值
#
# 但是, Local datetime 可以直接转换为 Unix Timestamp, UTC datetime 需要先转换到 UTC TimeZone 再转换为 Unix Timestamp
#
# 相反, Unix Timestamp 可以直接转换为 UTC datetime, 要获得 Local datetime, 需要再将 UTC datetime 转换为 Local datetime
#
#     https://stackoverflow.com/a/13287083
#     https://stackoverflow.com/a/466376
#     https://stackoverflow.com/a/7999977
#     https://stackoverflow.com/a/3682808
#     https://stackoverflow.com/a/63920772
#     https://www.geeksforgeeks.org/how-to-remove-timezone-information-from-datetime-object-in-python/
#
# pytz all timezones
#
#     https://stackoverflow.com/a/13867319
#     https://stackoverflow.com/a/15692958
#
#     import pytz
#     pytz.all_timezones
#     pytz.common_timezones
#     pytz.timezone('US/Eastern')
#
# timezone
#
#     https://stackoverflow.com/a/39079819
#     https://stackoverflow.com/a/1681600
#     https://stackoverflow.com/a/4771733
#     https://stackoverflow.com/a/63920772
#     https://toutiao.io/posts/sin4x0/preview
#
# 其它:
#
#     dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
#
#     (dt.replace(tzinfo=timezone.utc).astimezone(tz=None)).strftime(format)
#     datetime.fromisoformat((dt.replace(tzinfo=timezone.utc).astimezone(tz=None)).strftime(format))
#     string_to_datetime((dt.replace(tzinfo=timezone.utc).astimezone(tz=None)).strftime(format), format)
#
#     datetime.fromisoformat(time.strftime(format, time.gmtime(dt)))


def date_to_datetime(date_object: datetime) -> datetime | None:
    """'日期'转换为'日期时间'"""
    # https://stackoverflow.com/a/1937636
    try:
        return datetime.combine(date_object, datetime.min.time())
    except Exception as e:
        logger.exception(e)
        return None


def datetime_to_date(datetime_instance: datetime) -> date | None:
    """'日期时间'转换为'日期'"""
    # https://stackoverflow.com/a/3743240
    try:
        return datetime_instance.date()
    except Exception as e:
        logger.exception(e)
        return None


def local_timezone():
    """获取当前时区"""
    return datetime.now(timezone.utc).astimezone().tzinfo


def datetime_now(**kwargs) -> datetime | None:
    """获取当前日期和时间"""
    utc = kwargs.pop("utc", False)
    try:
        if isTrue(utc, bool):
            return datetime.now(timezone.utc)
        return datetime.now(**kwargs)
    except Exception as e:
        logger.exception(e)
        return None


def datetime_offset(datetime_instance: datetime | None = None, **kwargs) -> datetime | None:
    """
    获取 '向前或向后特定日期时间' 的日期和时间

    类型: weeks, days, hours, minutes, seconds, microseconds, milliseconds
    """
    _utc = kwargs.pop("utc", False)
    try:
        if isinstance(datetime_instance, datetime):
            return datetime_instance + timedelta(**kwargs)

        if _utc is True:
            return datetime.now(timezone.utc) + timedelta(**kwargs)

        return datetime.now() + timedelta(**kwargs)

    except Exception as e:
        logger.exception(e)
        return None


def datetime_to_string(datetime_instance: datetime, string_format: str = "%Y-%m-%d %H:%M:%S") -> str | None:
    """'日期时间'转换为'字符串'"""
    try:
        if not isTrue(datetime_instance, datetime):
            return None
        return datetime.strftime(datetime_instance, string_format)
    except Exception as e:
        logger.exception(e)
        return None


def datetime_to_timestamp(datetime_instance: datetime, utc: bool = False) -> int | None:
    """
    Datatime 转换为 Unix Timestamp
    Local datetime 可以直接转换为 Unix Timestamp
    UTC datetime 需要先替换 timezone 再转换为 Unix Timestamp
    """
    try:
        if not isTrue(datetime_instance, datetime):
            return None
        return int(datetime_instance.replace(tzinfo=timezone.utc).timestamp()) if utc is True else int(datetime_instance.timestamp())
    except Exception as e:
        logger.exception(e)
        return None


def datetime_local_to_timezone(datetime_instance: datetime, tz: timezone = timezone.utc) -> datetime | None:
    """
    Local datetime to TimeZone datetime(默认转换为 UTC datetime)
    replace(tzinfo=None) 移除结尾的时区信息
    """
    try:
        if not isTrue(datetime_instance, datetime):
            return None
        return (datetime.fromtimestamp(datetime_instance.timestamp(), tz=tz)).replace(tzinfo=None)
    except Exception as e:
        logger.exception(e)
        return None


def datetime_utc_to_timezone(
    datetime_instance: datetime,
    tz: Any = datetime.now(timezone.utc).astimezone().tzinfo,
) -> datetime | None:
    """
    UTC datetime to TimeZone datetime(默认转换为 Local datetime)
    replace(tzinfo=None) 移除结尾的时区信息
    """
    try:
        if not isTrue(datetime_instance, datetime):
            return None
        return datetime_instance.replace(tzinfo=timezone.utc).astimezone(tz).replace(tzinfo=None)

    except Exception as e:
        logger.exception(e)
        return None


def timestamp_to_datetime(timestamp: int, tz: timezone = timezone.utc) -> datetime | None:
    """Unix Timestamp 转换为 Datatime"""
    try:
        if not isTrue(timestamp, int):
            return None
        return (datetime.fromtimestamp(timestamp, tz=tz)).replace(tzinfo=None)
    except Exception as e:
        logger.exception(e)
        return None


def datetime_string_to_datetime(datetime_string: str, datetime_format: str = "%Y-%m-%d %H:%M:%S") -> datetime | None:
    """datetime string to datetime"""
    try:
        if not isTrue(datetime_string, str):
            return None
        return datetime.strptime(datetime_string, datetime_format)
    except Exception as e:
        logger.exception(e)
        return None


def datetime_string_to_timestamp(datetime_string: str, datetime_format: str = "%Y-%m-%d %H:%M:%S") -> int | None:
    """datetime string to timestamp"""
    try:
        if not isTrue(datetime_string, str):
            return None
        return int(time.mktime(time.strptime(datetime_string, datetime_format)))
    except Exception as e:
        logger.exception(e)
        return None


def datetime_object(date_time: datetime) -> dict | None:
    """datetime object"""
    try:
        return {
            "date": date_time.strftime("%Y-%m-%d"),
            "time": date_time.strftime("%H:%M:%S"),
            "datetime_now": date_time.strftime("%Y-%m-%d %H:%M:%S"),
            "datetime_minute": date_time.strftime("%Y-%m-%d %H:%M:00"),
            "datetime_hour": date_time.strftime("%Y-%m-%d %H:00:00"),
            "datetime_zero": date_time.strftime("%Y-%m-%d 00:00:00"),
        }
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def shell(
    command: str,
    isfile: bool = False,
    sh_shell: str = "/bin/bash",
    sh_option: str | None = None,
    **kwargs,
) -> subprocess.CompletedProcess | None:
    """执行 Shell 命令 或 脚本"""

    # :param command: 需要执行的命令
    # :param isfile: 是否将命令视为文件路径
    # :param sh_shell: 使用的 Shell 程序路径
    # :param sh_option: Shell 执行选项，例如 '-c'
    # :param kwargs: 其他传递给 subprocess.run 的参数
    # :return: 返回 subprocess.CompletedProcess 对象，失败时返回 None

    try:

        # 校验 Shell 程序路径
        if not check_file_type(sh_shell, "file"):
            logger.error(f"Invalid shell path: {sh_shell}")
            return None

        # 校验 command 和 sh_shell 的类型
        if not (isTrue(sh_shell, str) and isTrue(command, str)):
            logger.error("Invalid shell or command input.")
            return None

        # 构造命令
        if isfile:
            args = [sh_shell, command] if sh_option is None else [sh_shell, sh_option, command]
        else:
            sh_option = sh_option or "-c"
            args = [sh_shell, sh_option, command]

        logger.info(f"Executing command: {args}")

        return subprocess.run(args, **kwargs, check=False)

    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def json_file_parser(file: str) -> dict | None:
    """JSON File Parser"""
    try:
        if not check_file_type(file, "file"):
            logger.error(f"no such file: {file}")
            return None
        with open(file, encoding="utf-8") as json_raw:
            json_dict = json.load(json_raw)
        return json_dict
    except Exception as e:
        logger.exception(e)
        return None


# json_raw = '''
# {
#     "markdown.preview.fontSize": 14,
#     "editor.minimap.enabled": false,
#     "workbench.iconTheme": "vscode-icons",
#     "http.proxy": "http://127.0.0.1:1087"
# }
# '''
#
# print(json_sort(json_raw))
#
# {
#     "editor.minimap.enabled": false,
#     "http.proxy": "http://127.0.0.1:1087",
#     "markdown.preview.fontSize": 14,
#     "workbench.iconTheme": "vscode-icons"
# }


def json_sort(string: str, **kwargs) -> str | None:
    """JSON Sort"""
    try:
        if not isTrue(string, str):
            return None
        return json.dumps(json.loads(string), indent=4, sort_keys=True, **kwargs)
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def delete_files(files: str | list) -> bool:
    """删除文件"""
    try:

        if isinstance(files, str) and check_file_type(files, "file"):
            os.remove(files)
            logger.success(f"deleted file: {files}")
            return True

        if not isTrue(files, list):
            return False

        for _file in files:

            if isinstance(_file, str) and check_file_type(_file, "file"):
                try:
                    os.remove(_file)
                    logger.success(f"deleted file: {_file}")
                except Exception as e:
                    logger.error(f"error file: {_file} {e}")
            else:
                logger.error(f"error file: {_file}")

        return True

    except Exception as e:
        logger.exception(e)
        return False


def delete_directory(
    directory: str | list,
) -> bool:
    """
    delete directory

    https: // docs.python.org / 3 / library / os.html  # os.rmdir

        os.rmdir(path, *, dir_fd=None)

    Remove(delete) the directory path.

    If the directory does not exist or is not empty, an FileNotFoundError or an OSError is raised respectively.

    In order to remove whole directory trees, shutil.rmtree() can be used.

    https: // docs.python.org / 3 / library / shutil.html  # shutil.rmtree

        shutil.rmtree(path, ignore_errors=False, onerror=None)

    Delete an entire directory tree; path must point to a directory(but not a symbolic link to a directory).

    If ignore_errors is true, errors resulting from failed removals will be ignored;

    if false or omitted, such errors are handled by calling a handler specified by onerror or , if that is omitted, they raise an exception.
    """
    try:

        if isinstance(directory, str) and check_file_type(directory, "dir"):
            rmtree(directory)
            logger.success(f"deleted directory: {directory}")
            return True

        if not isTrue(directory, list):
            logger.error(f"error directory: {directory}")
            return False

        for _dir in directory:

            if isTrue(_dir, str) and check_file_type(_dir, "dir"):
                try:
                    rmtree(_dir)
                    logger.success(f"deleted directory: {_dir}")
                except Exception as e:
                    logger.error(f"error directory: {_dir} {e}")
            else:
                logger.error(f"error directory: {_dir}")

        return True

    except Exception as e:
        logger.exception(e)
        return False


# --------------------------------------------------------------------------------------------------


def processor(
    process_func: Callable,
    process_data: list,
    process_num: int = 2,
    thread: bool = False,
    **kwargs,
) -> Any:
    """使用多线程或多进程对数据进行并行处理"""

    # :param process_func: 处理函数
    # :param process_data: 待处理数据列表
    # :param process_num: 并行数量
    # :param thread: 是否使用多线程
    # :param kwargs: 其他可选参数传递给线程池或进程池
    # :return: 处理后的结果列表或 False（异常情况）
    #
    # MultiThread   多线程
    # MultiProcess  多进程
    #
    # ThreadPool    线程池
    # Pool          进程池
    #
    # ThreadPool 共享内存, Pool 不共享内存
    # ThreadPool 可以解决 Pool 在某些情况下产生的 Can't pickle local object 的错误
    #   https://stackoverflow.com/a/58897266
    #
    # 如果要启动一个新的进程或者线程, 将 process_num 设置为 1 即可

    try:

        # 确保并行数不超过数据量
        process_num = min(len(process_data), process_num)
        data_chunks = list_split(process_data, process_num, equally=True) if process_num > 1 else [process_data]

        if not data_chunks:
            logger.error("data chunks error")
            return False

        logger.info(f"Starting {'multi-threading' if thread else 'multi-processing'} with {process_num} workers...")

        # 执行多线程或多进程任务
        pool = ThreadPoolExecutor if thread else ProcessPoolExecutor
        with pool(process_num, **kwargs) as executor:
            return executor.map(process_func, data_chunks)

    except Exception as e:
        logger.exception(e)
        return False


# --------------------------------------------------------------------------------------------------


def create_empty_file(file: str | None = None) -> str | None:
    """create empty file"""
    try:
        if file is None:
            # 当前时间戳(纳秒)
            timestamp = time.time_ns()
            # 空文件路径
            file = f"/tmp/none_{timestamp}.txt"
        # 创建一个空文件
        # pylint: disable=R1732
        open(file, "w", encoding="utf-8").close()
        # 返回文件路径
        return file
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def uuid4_hex() -> str:
    """UUID"""
    return uuid4().hex


def increment_version(version: str) -> str | None:
    """版本号递增"""
    try:
        version_numbers = version.split(".")
        version_numbers[-1] = str(int(version_numbers[-1]) + 1)
        return ".".join(version_numbers)
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def make_directory(directory: str) -> bool:
    """创建目录"""
    try:
        os.makedirs(directory)
        return True
    except Exception as e:
        logger.exception(e)
        return False


def change_directory(directory: str) -> bool:
    """改变目录"""
    try:

        if not isTrue(directory, str):
            return False

        if not check_file_type(directory, "dir"):
            logger.error(f"no such directory: {directory}")
            return False

        os.chdir(directory)

        return True

    except Exception as e:
        logger.exception(e)
        return False


# --------------------------------------------------------------------------------------------------


def load_toml_file(file: str) -> dict | None:
    """Load TOML file"""
    info = "解析配置文件"
    try:
        logger.info(f"{info}[执行]")
        with open(file, "rb") as _file:
            config = tomllib.load(_file)
        logger.success(f"{info}[成功]")
        return config
    except Exception as e:
        logger.error(f"{info}[失败]")
        logger.exception(e)
        return None


def git_clone(
    git_repository: str,
    local_repository: str,
    timeout: int = 30,
    delete: bool = False,
    log_prefix: str = "",
) -> bool:
    """GIT Clone"""

    # 日志前缀
    log_prefix = f"{log_prefix} [GitClone]"

    try:

        # 获取应用程序Git仓库
        # logger.info(f'{log_prefix}process the request')
        # logger.info(f'{log_prefix}git repository: {git_repository}')
        # logger.info(f'{log_prefix}local repository: {local_repository}')

        # 删除本地仓库
        if isTrue(delete, bool):
            delete_directory(local_repository)
            time.sleep(1)

        # from shutil import which
        # logger.info(which('timeout')) if isTrue(debug, bool) else next
        # if which('timeout') != None:
        #     command = f'timeout -s 9 {timeout} git clone {git_repository} {local_repository}'

        # 克隆仓库
        result = shell(
            command=f"timeout -s 9 {timeout} git clone {git_repository} {local_repository}",
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        if result is None:
            return False

        result_code: int = result.returncode
        result_info = result.stdout.splitlines()

        if result_code != 0:
            for i in result_info:
                logger.error(f"{log_prefix}{i}")
            return False

        return True

    except Exception as e:
        logger.error(f"{log_prefix} [failed]")
        logger.exception(e)
        return False


def url_parse(
    url: str,
    # scheme: str = "http"
) -> ParseResult | None:
    """URL Parse"""
    # none_result = ParseResult(scheme='', netloc='', path='', params='', query='', fragment='')
    try:
        # 如果没有 scheme 的话, 字符串是不解析的. 所以, 如果没有 scheme, 就添加一个 scheme, 默认添加 http
        # if isTrue(url, str) and (url.find('://') == -1) and isTrue(scheme, str):
        #     url = f'{scheme}://{url}'
        # if isTrue(url, str):
        #     return urlparse(url)
        # return None
        return urlparse(url)
    except Exception as e:
        logger.exception(e)
        return None


# def debug_log(
#     log: None | str = None,
#     exception: None | Exception = None,
#     debug: bool = False,
#     error: bool = False
# ):
#     """debug log"""
#     if isTrue(log, str) and isTrue(debug, bool):
#         if isTrue(error, bool):
#             logger.error(log)
#         else:
#             logger.info(log)
#         return

#     if isTrue(exception, Exception):
#         if isTrue(debug, bool):
#             logger.exception(exception)
#         else:
#             logger.error(exception)


# --------------------------------------------------------------------------------------------------


def markdown_to_html(markdown_file: str, html_file: str, title: str) -> bool:

    info: str = "将 Markdown 转换为 HTML"

    try:

        logger.info(f"{info} [开始]")

        # 读取 HTML模版 文件
        logger.info(f"{info} [读取 HTML模版 文件]")
        html_template_file = f"{current_dir(__file__)}/markdown_to_html.template"
        with open(html_template_file, "r", encoding="utf-8") as _:
            html_template = _.read()

        # 读取 Markdown 文件
        logger.info(f"{info} [读取 Markdown 文件: {markdown_file}]")
        with open(markdown_file, "r", encoding="utf-8") as _:
            markdown_content = _.read()

        # 将 Markdown 转换为 HTML
        logger.info(f"{info} [将 Markdown 转换为 HTML]")
        # pylint: disable=E0606
        html_body = markdown.markdown(markdown_content, extensions=["tables"])  # type: ignore
        # pylint: enable=E0606

        # 构造完整的 HTML
        logger.info(f"{info} [构造完整的 HTML]")
        html_content = re.sub(r"\{title\}", title, html_template)
        html_content = re.sub(r"\{body\}", html_body, html_content)

        # 保存为 HTML 文件
        logger.info(f"{info} [保存为 HTML 文件: {html_file}]")
        with open(html_file, "w", encoding="utf-8") as _:
            _.write(html_content)

        logger.success(f"{info} [成功]")
        return True

    except Exception as e:
        logger.error(f"{info} [错误]")
        logger.error(e)
        return False


# --------------------------------------------------------------------------------------------------


def convert_field_to_datetime(data: list[dict], field: str, fmt: str = "%Y-%m-%d %H:%M:%S"):
    """
    将列表中每个 dict 的指定字段转换为 datetime 对象

    参数:
        data (list[dict]): 列表数据
        field (str): 要转换的字段名
        fmt (str): 字符串的时间格式, 默认 "%Y-%m-%d %H:%M:%S"
    """
    _data = deepcopy(data)
    for item in _data:
        value = item.get(field)
        if isinstance(value, str):
            try:
                item[field] = datetime.strptime(value, fmt)
            except ValueError:
                pass
    return _data
