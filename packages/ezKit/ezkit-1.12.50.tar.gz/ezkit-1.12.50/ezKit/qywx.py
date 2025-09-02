"""腾讯企业微信"""

#
# 企业微信开发者中心
#     https://developer.work.weixin.qq.com/
#     https://developer.work.weixin.qq.com/document/path/90313 (全局错误码)
# 参考文档:
#     https://www.gaoyuanqi.cn/python-yingyong-qiyewx/
#     https://www.jianshu.com/p/020709b130d3
#
# 应用管理
#   https://work.weixin.qq.com/wework_admin/frame#apps
# 自建 -> 创建应用
#   https://work.weixin.qq.com/wework_admin/frame#apps/createApiApp
# 上传 Logo -> 应用名称 -> 选择部门 / 成员 -> 创建应用
#
# 服务端API
#   https://developer.work.weixin.qq.com/document/path/90664
# 基本概念
#   https://developer.work.weixin.qq.com/document/path/90665
# 企业ID:
#   https://work.weixin.qq.com/wework_admin/frame#profile
# AgentId 和 Secret:
#   进入已创建的应用, 即可获取
#
# 应用管理 -> 应用 -> 开发者接口 -> 网页授权及JS-SDK
#
#   可作为应用OAuth2.0网页授权功能的回调域名
#   下载 配置可信域名需完成域名归属认证 的文件
#   保存到域名下
#   配置可信域名需完成域名归属认证 已验证
#
# 应用管理 -> 应用 -> 开发者接口 -> 企业可信IP
#
#   添加IP
#
import json
import time

import requests
from loguru import logger

from . import utils


class QYWX:
    """企业微信"""

    # API前缀
    api_prefix = "https://qyapi.weixin.qq.com"

    # 企业ID: https://developer.work.weixin.qq.com/document/path/90665#corpid
    work_id: str = ""

    # 应用ID: https://developer.work.weixin.qq.com/document/path/90665#agentid
    agent_id: str = ""

    # 应用Secret: https://developer.work.weixin.qq.com/document/path/90665#secret
    agent_secret: str = ""

    # Token: https://developer.work.weixin.qq.com/document/path/90665#access-token
    access_token: str = ""

    def __init__(
        self,
        work_id: str,
        agent_id: str,
        agent_secret: str,
        api_prefix: str = "https://qyapi.weixin.qq.com",
    ):
        """Initiation"""
        self.api_prefix = api_prefix
        self.work_id = work_id
        self.agent_id = agent_id
        self.agent_secret = agent_secret

        """获取 Token"""
        self.get_access_token()

    def get_access_token(self) -> bool:
        """获取Token"""

        info: str = "获取 Token"

        try:

            logger.info(f"{info} ......")

            response = requests.get(
                f"{self.api_prefix}/cgi-bin/gettoken?corpid={self.work_id}&corpsecret={self.agent_secret}",
                timeout=10,
            )

            if response.status_code != 200:
                logger.error(f"{info} [状态码错误]")
                return False

            result: dict = response.json()

            self.access_token = result.get("access_token", "")

            if not utils.isTrue(self.access_token, str):
                logger.error(f"{info} [失败]")
                return False

            logger.success(f"{info} [成功]")
            return True

        except Exception as e:
            logger.success(f"{info} [失败]")
            logger.exception(e)
            return False

    # def get_agent_list(self) -> dict | str | None:
    #     try:
    #         if not utils.isTrue(self.access_token, str):
    #             self.get_access_token()
    #         response = requests.get(f"{self.api_prefix}/cgi-bin/agent/list?access_token={self.access_token}", timeout=10)
    #         if response.status_code == 200:
    #             response_data: dict = response.json()
    #             if response_data.get('errcode') == 42001:
    #                 self.get_access_token()
    #                 time.sleep(1)
    #                 self.get_agent_list()
    #             return response_data
    #         return response.text
    #     except Exception as e:
    #         logger.exception(e)
    #         return None

    # def get_department_list(self, eid: str | None = None) -> dict | str | None:
    #     """eid: Enterprise ID"""
    #     try:
    #         if self.access_token is None:
    #             self.get_access_token()
    #         response = requests.get(f"{self.api_prefix}/cgi-bin/department/list?access_token={self.access_token}&id={eid}", timeout=10)
    #         if response.status_code == 200:
    #             response_data: dict = response.json()
    #             if response_data.get('errcode') == 42001:
    #                 self.get_access_token()
    #                 time.sleep(1)
    #                 self.get_department_list(eid)
    #             return response_data
    #         return response.text
    #     except Exception as e:
    #         logger.exception(e)
    #         return None

    # def get_user_list(self, eid: str | None = None) -> dict | str | None:
    #     """eid: Enterprise ID"""
    #     try:
    #         if self.access_token is None:
    #             self.get_access_token()
    #         response = requests.get(f"{self.api_prefix}/cgi-bin/user/list?access_token={self.access_token}&department_id={eid}", timeout=10)
    #         if response.status_code == 200:
    #             response_data: dict = response.json()
    #             if response_data.get('errcode') == 42001:
    #                 self.get_access_token()
    #                 time.sleep(1)
    #                 self.get_user_list(eid)
    #             return response_data
    #         return response.text
    #     except Exception as e:
    #         logger.exception(e)
    #         return None

    def get_user_id_by_mobile(self, mobile: str) -> dict | None:
        """根据电话号码获取用户ID"""

        info: str = f"根据电话号码获取用户ID: {mobile}"

        try:

            logger.info(f"{info} ......")

            if not utils.isTrue(self.access_token, str):
                self.get_access_token()

            json_string = json.dumps({"mobile": mobile})

            response = requests.post(
                f"{self.api_prefix}/cgi-bin/user/getuserid?access_token={self.access_token}",
                data=json_string,
                timeout=10,
            )

            if response.status_code != 200:
                logger.error(f"{info} [接口请求错误]")
                return None

            response_data: dict = response.json()

            if response_data.get("errcode") == 42001:
                self.get_access_token()
                time.sleep(1)
                self.get_user_id_by_mobile(mobile)

            logger.success(f"{info} [成功]")

            return response_data

            # return response.text

        except Exception as e:
            logger.error(f"{info} [失败]")
            logger.exception(e)
            return None

    # def get_user_info(self, eid: str | None = None) -> dict | str | None:
    #     """eid: Enterprise ID"""
    #     try:
    #         if self.access_token is None:
    #             self.get_access_token()
    #         response = requests.get(f"{self.api_prefix}/cgi-bin/user/get?access_token={self.access_token}&userid={eid}", timeout=10)
    #         if response.status_code == 200:
    #             response_data: dict = response.json()
    #             if response_data.get('errcode') == 42001:
    #                 self.get_access_token()
    #                 time.sleep(1)
    #                 self.get_user_info(eid)
    #             return response_data
    #         return response.text
    #     except Exception as e:
    #         logger.exception(e)
    #         return None

    def send_message_by_mobile(self, mobile: str | list, message: str) -> bool:
        """发送消息"""

        # 参考文档:
        # https://developer.work.weixin.qq.com/document/path/90235

        info: str = "发送消息"

        try:

            logger.info(f"{info} ......")

            if not utils.isTrue(self.access_token, str):
                if not self.get_access_token():
                    logger.error(f"{info} [失败]")
                    return False

            users: list = []

            if isinstance(mobile, str) and utils.isTrue(mobile, str):
                users.append(mobile)
            elif isinstance(mobile, list) and utils.isTrue(mobile, list):
                users += mobile
            else:
                logger.error(f"{info} [电话号码错误]")
                return False

            for user in users:

                logger.info(f"{info} [用户 {user}]")

                user_object = self.get_user_id_by_mobile(user)

                if not (isinstance(user_object, dict) and utils.isTrue(user_object, dict)):
                    logger.error(f"{info} [获取用户ID错误: {user}]")
                    continue

                if user_object.get("errcode", -1) != 0 or user_object.get("errmsg", "") != "ok":
                    logger.error(f"{user_object.get('errcode')}: {user_object.get('errmsg')}")
                    continue

                json_dict = {
                    "touser": user_object.get("userid"),
                    "msgtype": "text",
                    "agentid": self.agent_id,
                    "text": {"content": message},
                    "safe": 0,
                    "enable_id_trans": 0,
                    "enable_duplicate_check": 0,
                    "duplicate_check_interval": 1800,
                }

                json_string = json.dumps(json_dict)

                response = requests.post(
                    f"{self.api_prefix}/cgi-bin/message/send?access_token={self.access_token}",
                    data=json_string,
                    timeout=10,
                )

                if response.status_code != 200:
                    logger.error(f"{info} [发送消息失败: {user}]")
                    continue

                response_data: dict = response.json()

                if response_data.get("errcode") == 42001:
                    self.get_access_token()
                    time.sleep(1)
                    self.send_message_by_mobile(mobile, message)

                logger.success(f"{info} [成功: 用户 {user}]")

            logger.success(f"{info} [完成]")

            return True

        except Exception as e:
            logger.error(f"{info} [失败]")
            logger.exception(e)
            return False
