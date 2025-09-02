"""Database Library"""

# Column, Table, MetaData API
#     https://docs.sqlalchemy.org/en/14/core/metadata.html#column-table-metadata-api
# CursorResult
#     https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.CursorResult
# PostgreSQL 14 Data Types
#     https://www.postgresql.org/docs/14/datatype.html

import csv
import json
import re
from copy import deepcopy
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple, Type

import pandas as pd
from loguru import logger
from sqlalchemy import CursorResult, Engine, Index, bindparam, create_engine, insert, text
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session

from . import utils
from .errors import database_error, sqlalchemy_error

# --------------------------------------------------------------------------------------------------


class Base(DeclarativeBase):
    """所有 ORM 模型的基类"""

    pass  # pylint: disable=unnecessary-pass


# --------------------------------------------------------------------------------------------------


def get_limit_offset(page_index: int, page_size: int) -> tuple[int, int]:
    """
    根据 page_index (页码) 和 page_size (每页数量) 计算 SQL 的 LIMIT 和 OFFSET

    参数:

        page_index (int): 当前页码, 从 1 开始
        page_size (int): 每页数量, 必须 > 0

    返回:

        (limit, offset): limit 表示取多少条，offset 表示跳过多少条
    """
    try:

        # 默认第 1 页
        # if page_index < 1:
        #     page_index = 1
        page_index = max(page_index, 1)

        # 默认每页 10 条
        if page_size < 1:
            page_size = 10

        offset = (page_index - 1) * page_size

        # LIMIT, OFFSET
        return page_size, offset

    except Exception as e:
        logger.exception(e)
        return 10, 0


# --------------------------------------------------------------------------------------------------


def orm_object_to_dict(obj, include: list | None = None) -> dict | None:
    """
    将 ORM 对象转为 dict, 可选择只包含部分字段.
    :param obj: SQLAlchemy ORM 实例
    :param include: 要保留的字段列表(白名单)
    """
    if obj is None:
        return None

    data = {}

    for column in obj.__table__.columns:

        key = column.name

        if include and key not in include:
            continue

        value = getattr(obj, key)

        if isinstance(value, str):
            # 移除字符串前后的空白字符, 包括空格、\n、\t 等
            data[key] = str(value).strip()
        elif isinstance(value, (datetime, date)):
            # 日期时间转换为可读的字符串
            # data[key] = value.isoformat()
            data[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data[key] = value

    return data


def orm_list_to_dict(obj_list, include: list | None = None) -> list:
    return [orm_object_to_dict(obj, include) for obj in obj_list]


def orm_to_dict(obj, include: list | None = None) -> dict | list | None:
    """
    ORM 对象 (单个或列表) 转 JSON 字符串.
    :param include: 仅导出指定字段（白名单）
    """
    try:
        if isinstance(obj, list):
            data = orm_list_to_dict(obj, include)
        else:
            data = orm_object_to_dict(obj, include)
        return data
    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


def replace_datetime(source: str, to_pgsql: bool = True) -> str:
    """
    替换 datetime_date <-> datetime::date
    to_pgsql=True  : datetime_date -> datetime::date
    to_pgsql=False : datetime::date -> datetime_date
    """

    if to_pgsql:
        pattern = re.compile(r"(^|\.)(datetime_date)(__|$)")
        return pattern.sub(r"\1datetime::date\3", source, count=1)

    pattern = re.compile(r"(^|\.)(datetime::date)$")
    return pattern.sub(r"\1datetime_date\3", source, count=1)


def build_sqlalchemy_where_clause(data: dict) -> Optional[Tuple[str, Dict[str, Any], list]]:
    """
    构建 SQLAlchemy 原生 SQL 查询的 WHERE 子句与绑定参数 (text + :param_name)
    - 支持操作符: __like, __ge, __gt, __lt, __ne, __in, __between
    - 支持 PostgreSQL 对 date 字段的特殊处理
    - 返回: (SQL 子句字符串, 参数 dict, bindparams 列表)
    """

    # try:

    #     _data = deepcopy(data)

    #     sql_parts = []
    #     param_dict = {}
    #     bind_params = []

    #     for field, value in _data.items():

    #         # 特殊处理日期字段
    #         if field == "date" or field.startswith("date__"):
    #             field = field.replace("date", "datetime::date", 1)

    #         if "__" in field:

    #             base, op = field.split("__", 1)

    #             # 避免字段名冲突
    #             param_key = f"{base}_{op}"

    #             # 特殊处理日期字段
    #             if param_key.startswith("datetime::date"):
    #                 param_key = param_key.replace("datetime::date", "datetime_date", 1)

    #             if op == "like":
    #                 sql_parts.append(f"{base} LIKE :{param_key}")
    #                 param_dict[param_key] = f"%{value}%"
    #             elif op == "ge":
    #                 sql_parts.append(f"{base} >= :{param_key}")
    #                 param_dict[param_key] = value
    #             elif op == "gt":
    #                 sql_parts.append(f"{base} > :{param_key}")
    #                 param_dict[param_key] = value
    #             elif op == "le":
    #                 sql_parts.append(f"{base} <= :{param_key}")
    #                 param_dict[param_key] = value
    #             elif op == "lt":
    #                 sql_parts.append(f"{base} < :{param_key}")
    #                 param_dict[param_key] = value
    #             elif op == "ne":
    #                 sql_parts.append(f"{base} != :{param_key}")
    #                 param_dict[param_key] = value
    #             elif op == "in" and isinstance(value, list):
    #                 sql_parts.append(f"{base} IN :{param_key}")
    #                 param_dict[param_key] = value
    #                 bind_params.append(bindparam(param_key, expanding=True))
    #             elif op == "between" and isinstance(value, list) and len(value) == 2:
    #                 sql_parts.append(f"{base} BETWEEN :{param_key}_start AND :{param_key}_end")
    #                 param_dict[f"{param_key}_start"] = value[0]
    #                 param_dict[f"{param_key}_end"] = value[1]

    #         else:

    #             param_key = field

    #             # 特殊处理日期字段
    #             if param_key.startswith("datetime::date"):
    #                 param_key = param_key.replace("datetime::date", "datetime_date", 1)

    #             sql_parts.append(f"{field} = :{param_key}")

    #             param_dict[param_key] = value

    #     where_clause = " AND ".join(sql_parts)

    #     return where_clause, param_dict, bind_params

    # except Exception as e:
    #     logger.exception(e)
    #     return None

    try:

        _data = deepcopy(data)

        sql_parts = []
        param_dict = {}
        bind_params = []

        for field, value in _data.items():

            # 特殊处理日期字段
            # 如果匹配到 datetime_date 或者 .datetime_date 或者 datetime_date__ 或者 .datetime_date__ 就替换
            # is_date_field = field == "datetime_date" or field.startswith("datetime_date__")
            # base_field = field.replace("datetime_date", "datetime::date", 1) if is_date_field else field
            pattern_date_field = re.compile(r"(^|\.)(datetime_date)(__|$)")
            if pattern_date_field.search(field):
                # base_field = pattern_date.sub(r"\1datetime::date\3", field, count=1)
                base_field = replace_datetime(field, to_pgsql=True)
            else:
                base_field = field

            if "__" in base_field:

                base, op = base_field.split("__", 1)

                # 避免字段名冲突
                param_key = f"{base.replace('.', '_')}_{op}"

                # 特殊处理日期字段
                # if param_key.startswith("datetime::date"):
                #     param_key = param_key.replace("datetime::date", "datetime_date", 1)
                pattern_param_key = re.compile(r"(^|\.)(datetime::date)$")
                if pattern_param_key.search(param_key):
                    param_key = replace_datetime(param_key, to_pgsql=False)

                if op == "like":
                    sql_parts.append(f"{base} LIKE :{param_key}")
                    param_dict[param_key] = f"%{value}%"
                elif op in ("ge", "gt", "le", "lt", "ne"):
                    operator = {"ge": ">=", "gt": ">", "le": "<=", "lt": "<", "ne": "!="}[op]
                    sql_parts.append(f"{base} {operator} :{param_key}")
                    param_dict[param_key] = value
                elif op == "in" and isinstance(value, list):
                    sql_parts.append(f"{base} IN :{param_key}")
                    param_dict[param_key] = value
                    bind_params.append(bindparam(param_key, expanding=True))
                elif op == "between" and isinstance(value, list) and len(value) == 2:
                    sql_parts.append(f"{base} BETWEEN :{param_key}_start AND :{param_key}_end")
                    param_dict[f"{param_key}_start"] = value[0]
                    param_dict[f"{param_key}_end"] = value[1]

            else:

                param_key = base_field.replace(".", "_")
                # 特殊处理日期字段
                # 如果匹配到 datetime_date 或者 .datetime_date 或者 datetime_date__ 或者 .datetime_date__ 就替换
                # if param_key.startswith("datetime::date"):
                #     param_key = param_key.replace("datetime::date", "datetime_date", 1)
                pattern_param_key = re.compile(r"(^|\.)(datetime::date)$")
                if pattern_param_key.search(param_key):
                    param_key = replace_datetime(param_key, to_pgsql=False)
                sql_parts.append(f"{base_field} = :{param_key}")
                param_dict[param_key] = value

        where_clause = " AND ".join(sql_parts)
        return where_clause, param_dict, bind_params

    except Exception as e:
        logger.exception(e)
        return None


def build_sqlalchemy_select_where(data: dict) -> tuple | None:
    """Build SQLAlchemy select WHERE"""

    try:

        _data = deepcopy(data)

        # 获取分页参数 (从 data 中取出 pageIndex 和 pageSize, 剩余的为查询参数)

        pageIndex = _data.pop("pageIndex", 1)
        pageSize = _data.pop("pageSize", 10)

        limit, offset = get_limit_offset(pageIndex, pageSize)

        # 构建 WHERE

        build_result = build_sqlalchemy_where_clause(_data)

        if build_result is None:
            logger.error("Build SQLAlchemy WHERE clause error")
            return None

        where_clause, statement_params, bind_params = build_result

        # 添加 WHERE 前缀
        if isinstance(where_clause, str) and where_clause.strip():
            where_clause = f"WHERE {where_clause.strip()}"

        # 分页参数
        statement_params["limit"] = limit
        statement_params["offset"] = offset

        return where_clause, statement_params, bind_params

    except Exception as e:
        logger.exception(e)
        return None


def build_sqlalchemy_update(tablename: str, where_data: dict, update_data: dict) -> tuple | None:
    """Build SQLAlchemy update"""

    # 构建 WHERE

    build_result = build_sqlalchemy_where_clause(where_data)

    if build_result is None:
        logger.error("Build SQLAlchemy WHERE clause error")
        return None

    where_clause, statement_params, bind_params = build_result

    # 构建 UPDATE SQL 语句 (SET 中 key 的 value 的 key 添加后缀 _value, 避免与 where 冲突)
    sql: str = f"UPDATE {tablename} SET " + ", ".join([f"{k} = :{k}_value" for k in update_data.keys()]) + f" WHERE {where_clause}"

    # 合并数据 (key 添加后缀 _value, 与 SQL 保持一致)
    for k in update_data.keys():
        statement_params[f"{k}_value"] = update_data[k]

    # 返回 statement 和 params
    return text(sql).bindparams(*bind_params), statement_params


# --------------------------------------------------------------------------------------------------


class Database:
    """Database"""

    engine = create_engine("sqlite://")

    def __init__(self, engine: Engine | None = None, target: str | None = None, **options):
        """Initiation"""
        if engine is not None:
            self.engine = engine
        elif isinstance(target, str) and utils.isTrue(target, str):
            if utils.isTrue(options, dict):
                self.engine = create_engine(target, **options)
            else:
                self.engine = create_engine(target)
        else:
            pass

    # ----------------------------------------------------------------------------------------------

    def initializer(self):
        """ensure the parent proc's database connections are not touched in the new connection pool"""
        self.engine.dispose(close=False)

    # ----------------------------------------------------------------------------------------------

    def connect_test(self) -> bool:
        info = "Database connect test"
        try:
            logger.info(f"{info} ......")
            with self.engine.connect() as _:
                logger.success(f"{info} [success]")
                return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False

    # ----------------------------------------------------------------------------------------------

    def metadata_init(self, base: type[Base], **kwargs) -> bool:
        # https://stackoverflow.com/questions/19175311/how-to-create-only-one-table-with-sqlalchemy
        info = "Database init table"
        try:
            logger.info(f"{info} ......")
            base.metadata.drop_all(self.engine, **kwargs)
            base.metadata.create_all(self.engine, **kwargs)
            logger.success(f"{info} [success]")
            return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False

    # ----------------------------------------------------------------------------------------------

    def initialization_table(self, table: str):
        """初始化表"""

        # 初始化所有表
        #   db.metadata_init(Base)
        # 初始化指定表
        #   database.metadata_init(Base, tables=[Base.metadata.tables['ashare']])
        self.metadata_init(Base, tables=[Base.metadata.tables[table]])

    # ----------------------------------------------------------------------------------------------

    def create_index(self, index_name, table_field) -> bool:
        # 创建索引
        #   https://stackoverflow.com/a/41254430
        # 示例:
        #   index_name: a_share_list_code_idx1
        #   table_field: Table_a_share_list.code
        info = "Database create index"
        try:
            logger.info(f"{info} ......")
            idx = Index(index_name, table_field)
            try:
                idx.drop(bind=self.engine)
            except Exception as e:
                logger.exception(e)
            idx.create(bind=self.engine)
            logger.success(f"{info} [success]")
            return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False

    # ----------------------------------------------------------------------------------------------

    # 私有函数, 保存 execute 的结果到 CSV 文件
    def _result_save(self, file, data) -> bool:
        try:
            outcsv = csv.writer(file)
            outcsv.writerow(data.keys())
            outcsv.writerows(data)
            logger.success("save to csv success")
            return True
        except Exception as e:
            logger.error("save to csv failed")
            logger.exception(e)
            return False

    # ----------------------------------------------------------------------------------------------

    # def execute(
    #     self,
    #     sql: str | None = None,
    #     sql_file: str | None = None,
    #     sql_file_kwargs: dict | None = None,
    #     csv_file: str | None = None,
    #     csv_file_kwargs: dict | None = None
    # ) -> CursorResult[Any] | bool:
    #     """"运行"""

    #     # ------------------------------------------------------------

    #     # 提取 SQL
    #     # 如果 sql 和 sql_file 同时存在, 优先执行 sql

    #     sql_object = None

    #     info: str = f"""Extract SQL: {sql}"""

    #     try:

    #         logger.info(f"{info} ......")

    #         if utils.isTrue(sql, str):

    #             sql_object = sql

    #         elif sql_file is not None and utils.isTrue(sql_file, str):

    #             # 判断文件是否存在
    #             if isinstance(sql_file, str) and utils.check_file_type(sql_file, "file") is False:

    #                 logger.error(f"No such file: {sql_file}")
    #                 return False

    #             if isinstance(sql_file, str) and utils.isTrue(sql_file, str):

    #                 # 读取文件内容
    #                 if sql_file_kwargs is not None and utils.isTrue(sql_file_kwargs, dict):
    #                     with open(sql_file, "r", encoding="utf-8", **sql_file_kwargs) as _file:
    #                         sql_object = _file.read()
    #                 else:
    #                     with open(sql_file, "r", encoding="utf-8") as _file:
    #                         sql_object = _file.read()

    #         else:

    #             logger.error("SQL or SQL file error")
    #             logger.error(f"{info} [failed]")
    #             return False

    #         logger.success(f'{info} [success]')

    #     except Exception as e:

    #         logger.error(f"{info} [failed]")
    #         logger.exception(e)
    #         return False

    #     # ------------------------------------------------------------

    #     # 执行 SQL

    #     info = f"""Execute SQL: {sql_object}"""

    #     try:

    #         logger.info(f"{info} ......")

    #         with self.engine.connect() as connect:

    #             # 执行SQL
    #             if sql_object is None:
    #                 return False

    #             result = connect.execute(text(sql_object))

    #             connect.commit()

    #             if csv_file is None:
    #                 # 如果 csv_file 没有定义, 则直接返回结果
    #                 logger.success(f'{info} [success]')
    #                 return result

    #             # 如果 csv_file 有定义, 则保存结果到 csv_file
    #             info_of_save = f"Save result to file: {csv_file}"
    #             logger.info(f"{info_of_save} .......")

    #             # 保存结果
    #             if isinstance(csv_file_kwargs, dict) and utils.isTrue(csv_file_kwargs, dict):
    #                 with open(csv_file, "w", encoding="utf-8", **csv_file_kwargs) as _file:
    #                     result_of_save = self._result_save(_file, result)
    #             else:
    #                 with open(csv_file, "w", encoding="utf-8") as _file:
    #                     result_of_save = self._result_save(_file, result)

    #             # 检查保存结果
    #             if result_of_save is True:
    #                 logger.success(f'{info_of_save} [success]')
    #                 logger.success(f'{info} [success]')
    #                 return True

    #             logger.error(f"{info_of_save} [failed]")
    #             logger.error(f"{info} [failed]")
    #             return False

    #     except Exception as e:

    #         logger.error(f'{info} [failed]')
    #         logger.exception(e)
    #         return False

    # ----------------------------------------------------------------------------------------------

    def connect_execute(
        self,
        sql: str | None = None,
        read_sql_file: dict | None = None,
        save_to_csv: dict | None = None,
    ) -> CursorResult[Any] | bool | None:

        info: str = "Database connect execute"

        logger.info(f"{info} ......")

        sql_statement: str = ""

        # ------------------------------------------------------------------------------------------

        try:
            # SQL文件优先
            if isinstance(read_sql_file, dict) and utils.isTrue(read_sql_file, dict):
                read_sql_file.pop("encoding")
                read_sql_file_kwargs: dict = {
                    "mode": "r",
                    "encoding": "utf-8",
                    **read_sql_file,
                }
                with open(encoding="utf-8", **read_sql_file_kwargs) as _file:
                    sql_statement = _file.read()
            else:
                if not isinstance(sql, str):
                    return None
                sql_statement = sql
        except Exception as e:
            logger.exception(e)
            return None

        # ------------------------------------------------------------------------------------------

        # 创建一个连接
        with self.engine.connect() as connection:

            # 开始一个事务
            with connection.begin():  # 事务会自动提交或回滚

                try:

                    # 执行 SQL 查询
                    result = connection.execute(text(sql_statement))

                    # 执行成功
                    logger.success(f"{info} [success]")

                    # 返回查询结果
                    if isinstance(save_to_csv, dict) and utils.isTrue(save_to_csv, dict):
                        save_to_csv_kwargs: dict = {
                            "mode": "w",
                            "encoding": "utf-8",
                            **save_to_csv,
                        }
                        with open(encoding="utf-8", **save_to_csv_kwargs) as _file:
                            return self._result_save(_file, result)

                    return result

                except Exception as e:
                    # 发生异常时回滚事务
                    logger.info(f"{info} [failed]")
                    logger.exception(e)
                    return None

    # ----------------------------------------------------------------------------------------------

    def drop_table(self, table_name: str) -> bool:
        """删除表"""

        info: str = f"drop table: {table_name}"

        try:
            logger.info(f"{info} ......")
            self.connect_execute(sql=f"DROP TABLE IF EXISTS {table_name}")
            logger.success(f"{info} [success]")
            return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False

    # ----------------------------------------------------------------------------------------------

    def read_with_pandas(self, method: str = "read_sql", result_type: str = "df", **kwargs) -> pd.DataFrame | list | dict:
        """读取数据"""

        # 使用SQL查询数据: 使用 pd.read_sql 的参数
        # read_data_with_pandas(by="sql", result_type="df", sql="SELECT * FROM table ORDER BY date DESC LIMIT 1")

        # 读取表中的数据: 使用 pd.read_sql_table 的参数
        # read_data_with_pandas(by="table", result_type="df", table_name="ashare")

        data: pd.DataFrame = pd.DataFrame()

        info: str = "read data"

        try:

            logger.info(f"{info} ......")

            # 从 kwargs 中删除 con 键
            kwargs.pop("con", None)

            match method:
                case "read_sql":
                    data = pd.read_sql(con=self.engine, **kwargs)
                case "read_sql_query":
                    data = pd.read_sql_query(con=self.engine, **kwargs)
                case "read_sql_table":
                    data = pd.read_sql_table(con=self.engine, **kwargs)
                case _:
                    logger.error(f"{info} [incorrect method: {method}]")
                    return data

            if data.empty:
                logger.error(f"{info} [failed]")
                return data

            logger.success(f"{info} [success]")

            match result_type:
                case "json":
                    return json.loads(data.to_json(orient="records"))
                case "dict":
                    return data.to_dict()
                case "list":
                    # https://stackoverflow.com/a/26716774
                    return data.to_dict("list")
                case _:
                    return data

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return data

    # ----------------------------------------------------------------------------------------------

    def create_data(self, TS: Type, data: list) -> bool:
        """创建数据. TS: Table Schema"""

        info: str = "create data"

        if not utils.isTrue(data, list):
            logger.error(f"{info} [data type is not a list]")

        logger.info(f"{info} ......")

        with Session(self.engine) as session:

            try:

                for item in data:

                    if not utils.isTrue(item, dict):
                        logger.error(f"{info} [data type error]")
                        session.rollback()
                        return False

                    session.add(TS(**item))

                session.commit()

                logger.success(f"{info} [success]")

                return True

            except Exception as e:
                session.rollback()
                logger.error(f"{info} [failed]")
                logger.exception(e)
                return False


# ----------------------------------------------------------------------------------------------


class DatabaseAsyncSession:
    """Database Async Session"""

    AsyncSessionLocal: async_sessionmaker[AsyncSession]

    def __init__(self, session: async_sessionmaker[AsyncSession]):
        """Initiation"""
        self.AsyncSessionLocal = session

    # 执行器 (CRUD都可以执行. 即可以执行原生SQL, 也可以执行ORM)
    #   statement: SQL 或者 insert(schema)等
    #   params: List[dict] (非必要)
    async def operater(self, statement, params: Any | None = None, **kwargs) -> Result | None:

        async with self.AsyncSessionLocal() as session:

            try:
                result = await session.execute(statement, params, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error(e)
                return None

    # 精确返回一个标量结果 (适用于只返回一行数据的select, 比如 count 查询)
    async def operate_return_scalar_one(self, statement, params: Any | None = None, **kwargs) -> Any | None:
        result = await self.operater(statement, params, **kwargs)
        if result is None:
            return None
        try:
            return result.scalar_one()
        except Exception as e:
            logger.error(e)
            return None

    # 返回所有结果 (适用于所有select)
    async def operate_return_mappings_all(self, statement, params: Any | None = None, **kwargs) -> List[Any]:
        result = await self.operater(statement, params, **kwargs)
        if result is None:
            return []
        try:
            rows = result.mappings().all()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(e)
            return []


# --------------------------------------------------------------------------------------------------


async def async_create_and_count(db: DatabaseAsyncSession, schema: Type[DeclarativeBase], data: list) -> dict:

    # 插入数据
    result = await db.operater(insert(schema), data)

    # 返回结果
    if result is None:
        return {"code": 1001, "data": 0, "message": database_error["create"]["message"]}

    return {"code": 200, "data": len(data), "message": "create data success"}


# --------------------------------------------------------------------------------------------------


async def async_read_and_count(db: DatabaseAsyncSession, data: dict, statement_select: str, statement_from: str, statement_end: str = "") -> dict:

    # 初始返回结果 (适用于 count 等于 0)
    result = {"count": 0, "list": [], "pageIndex": data["pageIndex"], "pageSize": 0}

    # Statement Prefix
    statement_prefix = f"{statement_select} {statement_from}"

    # ----------------------------------------------------------------------------------------------

    # 构建 WHERE

    where_collections = build_sqlalchemy_select_where(data)

    if where_collections is None:
        return {"code": 1001, "data": None, "message": sqlalchemy_error["build_where"]["message"]}

    where_clause, statement_params, bind_params = where_collections

    # ----------------------------------------------------------------------------------------------

    # 统计 WHERE

    # table_name: str
    # count_statement = text(f"SELECT COUNT(*) FROM {table_name} {where_clause}").bindparams(*bind_params)
    count_statement = text(f"SELECT COUNT(*) {statement_from} {where_clause}").bindparams(*bind_params)

    count_result = await db.operate_return_scalar_one(count_statement, statement_params)

    if count_result is None:
        return {"code": 1002, "data": None, "message": sqlalchemy_error["statement_params"]["message"]}

    if count_result == 0:
        return {"code": 200, "data": result, "message": "read data success"}

    # ----------------------------------------------------------------------------------------------

    # 读取数据

    read_statement = text(f"{statement_prefix} {where_clause} {statement_end}").bindparams(*bind_params)

    read_result = await db.operate_return_mappings_all(read_statement, statement_params)

    # ----------------------------------------------------------------------------------------------

    # 数据整合
    result["count"] = count_result
    result["list"] = read_result
    result["pageSize"] = len(read_result)

    # ----------------------------------------------------------------------------------------------

    # 返回结果
    return {"code": 200, "data": result, "message": "read data success"}


# --------------------------------------------------------------------------------------------------


async def async_update_and_count(db: DatabaseAsyncSession, table_name: str, data: dict) -> dict:

    # 构建 WHERE

    where_collections = build_sqlalchemy_select_where(data["where"])

    if where_collections is None:
        return {"code": 1001, "data": 0, "message": sqlalchemy_error["build_where"]["message"]}

    where_clause, statement_params, bind_params = where_collections

    # ----------------------------------------------------------------------------------------------

    # 统计 WHERE

    count_statement = text(f"SELECT COUNT(*) FROM {table_name} {where_clause}").bindparams(*bind_params)

    count_result = await db.operate_return_scalar_one(count_statement, statement_params)

    if count_result is None:
        return {"code": 1002, "data": None, "message": sqlalchemy_error["statement_params"]["message"]}

    if count_result == 0:
        return {"code": 1003, "data": 0, "message": database_error["no_data"]["message"]}

    # ----------------------------------------------------------------------------------------------

    # 更新数据

    update_collections = build_sqlalchemy_update(table_name, data["where"], data["values"])

    if update_collections is None:
        return {"code": 1004, "data": None, "message": sqlalchemy_error["build_statement"]["message"]}

    update_statement, update_params = update_collections

    update_result = await db.operater(update_statement, update_params)

    if update_result is None:
        return {"code": 1005, "data": None, "message": database_error["update"]["message"]}

    # ----------------------------------------------------------------------------------------------

    # 返回结果
    return {"code": 200, "data": count_result, "message": "update data success"}


# --------------------------------------------------------------------------------------------------


async def async_delete_and_count(db: DatabaseAsyncSession, table_name: str, data: dict) -> dict:

    # 构建 WHERE

    where_collections = build_sqlalchemy_select_where(data)

    if where_collections is None:
        return {"code": 1001, "data": 0, "message": sqlalchemy_error["build_where"]["message"]}

    where_clause, statement_params, bind_params = where_collections

    # ----------------------------------------------------------------------------------------------

    # 统计 WHERE

    count_statement = text(f"SELECT COUNT(*) FROM {table_name} {where_clause}").bindparams(*bind_params)

    count_result = await db.operate_return_scalar_one(count_statement, statement_params)

    if count_result is None:
        return {"code": 1002, "data": None, "message": sqlalchemy_error["statement_params"]["message"]}

    if count_result == 0:
        return {"code": 1003, "data": 0, "message": database_error["no_data"]["message"]}

    # ----------------------------------------------------------------------------------------------

    # 删除数据

    delete_statement = text(f"DELETE FROM {table_name} {where_clause}").bindparams(*bind_params)

    delete_result = await db.operater(delete_statement, statement_params)

    if delete_result is None:
        return {"code": 1004, "data": 0, "message": database_error["delete"]["message"]}

    # ----------------------------------------------------------------------------------------------

    # 返回结果
    return {"code": 200, "data": count_result, "message": "delete data success"}
