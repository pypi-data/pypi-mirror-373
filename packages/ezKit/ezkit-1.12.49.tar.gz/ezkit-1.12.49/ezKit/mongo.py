"""MongoDB Library"""

from loguru import logger
from pymongo import MongoClient
from pymongo.collection import Collection

from . import utils


class Mongo:
    """MongoDB"""

    client = MongoClient()

    def __init__(self, target: str | dict | None = None):
        """Initiation"""
        if isinstance(target, str) and utils.isTrue(target, str):
            self.client = MongoClient(target)
        elif isinstance(target, dict) and utils.isTrue(target, dict):
            self.client = MongoClient(**target)
        else:
            pass

    def close(self) -> bool:
        """client close"""
        try:
            self.client.close()
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def connect_test(self) -> bool:
        info = "MongoDB connect test"
        try:
            logger.info(f"{info} ......")
            self.client.server_info()
            logger.success(f"{info} [success]")
            return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False

    def collection(self, database: str, name: str) -> Collection | None:
        try:
            return self.client[database][name]
        except Exception as e:
            logger.exception(e)
            return None

    def collection_insert(self, database, collection, data, drop: bool = False):
        db_collection = self.client[database][collection]
        info = "MongoDB collection insert"
        try:
            logger.info(f"{info} ......")
            # 是否删除 collection
            if utils.isTrue(drop, bool):
                # 删除 collection
                db_collection.drop()
            # 插入数据
            if utils.isTrue(data, dict):
                # 插入一条数据
                result = db_collection.insert_one(data)
            elif utils.isTrue(data, list):
                # 插入多条数据
                result = db_collection.insert_many(data)
            else:
                logger.error(f"{info} [failed]")
                logger.error("Data type error")
                return False
            logger.success(f"{info} [success]")
            return result
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False
