"""Zabbix Library"""

import time
from copy import deepcopy

import requests
from loguru import logger

from . import utils


class Zabbix:
    """Zabbix"""

    api: str | None = None
    auth: str | None = None

    # ----------------------------------------------------------------------------------------------

    def __init__(self, api: str, username: str, password: str):
        """Initiation"""
        self.api = api
        self.auth = self.login(username=username, password=password)

    # ----------------------------------------------------------------------------------------------

    def request(
        self, method: str, params: dict | list, debug: bool = False, **kwargs
    ) -> dict | None:
        """Request Zabbix API"""

        try:

            # https://www.zabbix.com/documentation/current/en/manual/api#performing-requests
            # The request must have the Content-Type header set to one of these values:
            #     application/json-rpc, application/json or application/jsonrequest.
            headers = {"Content-Type": "application/json-rpc"}

            # https://www.zabbix.com/documentation/6.0/en/manual/api#authentication
            # jsonrpc - the version of the JSON-RPC protocol used by the API; the Zabbix API implements JSON-RPC version 2.0
            # method - the API method being called
            # params - parameters that will be passed to the API method
            # id - an arbitrary identifier of the request (请求标识符, 这里使用UNIX时间戳作为唯一标示)
            # auth - a user authentication token; since we don't have one yet, it's set to null
            data: dict = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "auth": None if method == "apiinfo.version" else self.auth,
                "id": int(time.time()),
            }

            if utils.isTrue(debug, bool):
                logger.info(f"request data: {data}")

            if self.api is None:
                logger.error("api is None")
                return None

            # 请求API
            response = requests.post(
                self.api, headers=headers, json=data, timeout=10, **kwargs
            )

            if utils.isTrue(debug, bool):
                logger.info(f"response: {response}")

            if response.status_code != 200:
                logger.error(f"response status code: {response.status_code}")
                return None

            # 返回结果
            return response.json()

        except Exception as e:
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def login(self, username: str, password: str) -> str | None:
        """User Login"""

        info: str = "Login"

        try:

            logger.info(f"{info} [started]")

            data: dict | None = self.request(
                method="user.login", params={"username": username, "password": password}
            )

            if data is None:
                return None

            if data.get("result") is None:
                logger.error(f"{info} [response result is None]")
                return None

            logger.success(f"{info} [succeeded]")
            return data["result"]

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def logout(self) -> bool:
        """User Logout"""

        info: str = "Logout"

        try:

            logger.info(f"{info} [started]")

            data = self.request(method="user.logout", params={})

            if data is not None and data.get("result"):
                logger.success(f"{info} [succeeded]")
                return True

            if data is not None and data.get("error"):
                logger.error(f"{info} [error: {data.get('error',{}).get('data')}]")
                return False

            logger.error(f"{info} [failed]")
            return False

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False

    # ----------------------------------------------------------------------------------------------

    # def logout_and_exit(self):
    #     """Logout and Exit"""

    #     try:
    #         self.logout()
    #     except Exception as e:
    #         logger.exception(e)
    #     finally:
    #         sys.exit()

    # ----------------------------------------------------------------------------------------------

    def get_version(self) -> str | None:
        """Get version"""

        info: str = "Get version"

        try:

            logger.info(f"{info} [started]")

            data = self.request("apiinfo.version", [])

            if data is None:
                return None

            logger.success(f"{info} [succeeded]")
            return data["result"]

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def get_ids_by_template_name(self, name: str) -> list | None:
        """Get ids by template name"""

        # https://www.zabbix.com/documentation/7.0/en/manual/api/reference/template
        # name: string/array
        # example: 'Linux by Zabbix agent' / ['Linux by Zabbix agent', 'Linux by Zabbix agent active']
        # 如果 name 为 '' (空), 返回所有 template id

        info: str = "Get ids by template name"

        try:

            logger.info(f"{info} [started]")

            data = self.request(
                "template.get", {"output": "templateid", "filter": {"name": name}}
            )

            if data is None:
                return None

            if not utils.isTrue(data["result"], list):
                logger.error(f"{info} [error: {data['error']}]")
                return None

            logger.success(f"{info} [succeeded]")
            return [i["templateid"] for i in data["result"]]

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def get_ids_by_hostgroup_name(self, name: str) -> list | None:
        """Get ids by hostgroup name"""

        # # https://www.zabbix.com/documentation/7.0/en/manual/api/reference/hostgroup
        # name: string/array
        # example: 'Linux servers' / ['Linux servers', 'Discovered hosts']
        # 如果 name 为 '' (空), 返回所有 hostgroup id

        info: str = "Get ids by hostgroup name"

        try:

            logger.info(f"{info} [started]")

            # Zabbix 6.0 -> output: groupid
            data = self.request(
                "hostgroup.get", {"output": "extend", "filter": {"name": name}}
            )

            if data is None:
                return None

            if not utils.isTrue(data.get("result"), list):
                logger.error(f"{info} [error: {data['error']}]")
                return None

            logger.success(f"{info} [succeeded]")
            return [i["groupid"] for i in data["result"]]

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def get_hosts_by_template_name(
        self, name: str, output: str = "extend", **kwargs
    ) -> list | None:
        """Get hosts by template name"""

        # name: string/array
        # example: 'Linux by Zabbix agent' / ['Linux by Zabbix agent', 'Linux by Zabbix agent active']
        # 如果 name 为 '' (空), 返回所有 host

        info: str = "Get hosts by template name"

        try:

            logger.info(f"{info} [started]")

            templates = self.request(
                "template.get", {"output": ["templateid"], "filter": {"host": name}}
            )

            if templates is None:
                return None

            if not utils.isTrue(templates.get("result"), list):
                logger.error(f"{info} [error: {templates['error']}]")
                return None

            templateids = [i["templateid"] for i in templates["result"]]

            hosts = self.request(
                "host.get", {"output": output, "templateids": templateids, **kwargs}
            )

            if hosts is None:
                return None

            if not utils.isTrue(hosts.get("result"), list):
                logger.error(f"{info} [error: {hosts['error']}]")
                return None

            logger.success(f"{info} [succeeded]")
            return hosts["result"]

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def get_hosts_by_hostgroup_name(
        self, name: str, output: str | list = "extend", **kwargs
    ) -> list | None:
        """Get hosts by hostgroup name"""

        # name: string/array
        # example: 'Linux servers' / ['Linux servers', 'Discovered hosts']
        # 如果 name 为 '' (空), 返回所有 hosts

        info: str = "Get hosts by hostgroup name"

        try:

            logger.info(f"{info} [started]")

            ids = self.get_ids_by_hostgroup_name(name)

            if ids is None:
                return None

            hosts = self.request(
                "host.get", {"output": output, "groupids": ids, **kwargs}
            )

            if hosts is None:
                return None

            if not utils.isTrue(hosts.get("result"), list):
                logger.error(f"{info} [error: {hosts['error']}]")
                return None

            logger.success(f"{info} [succeeded]")
            return hosts["result"]

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def get_interface_by_host_id(
        self, hostid: str, output: str = "extend"
    ) -> list | None:
        """Get interface by host id"""

        # hostids: string/array
        # example: '10792' / ['10792', '10793']

        info: str = "Get interface by host id"

        try:

            logger.info(f"{info} [started]")

            data = self.request(
                "hostinterface.get", {"output": output, "hostids": hostid}
            )

            if data is None:
                return None

            if not utils.isTrue(data.get("result"), list):
                logger.error(f"{info} [error: {data['error']}]")
                return None

            logger.success(f"{info} [succeeded]")
            return data["result"]

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def available_hosts(self, hosts: list) -> tuple | None:
        """可用服务器"""

        try:

            if not utils.isTrue(hosts, list):
                logger.error("hosts is not a list")
                return None

            # 可用服务器, 不可用服务器
            available, unavailable = [], []

            # 服务器排查
            for host in hosts:
                if host["interfaces"][0]["available"] != "1":
                    unavailable.append(host["name"])
                else:
                    available.append(host)

            return available, unavailable

        except Exception as e:
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def get_history_by_item_key(
        self,
        hosts: list,
        time_from: int,
        time_till: int,
        item_key: str,
        data_type: int = 3,
    ) -> list | None:
        """get history by item key"""

        # 1. 根据 item key 获取 item id, 通过 item id 获取 history
        # 2. 根据 host 的 item id 和 history 的 item id 将数据提取为一个 history list
        # 3. 根据 history list 中的 clock 排序, 然后将 history list 整合到 host 中
        # 4. 返回包含有 item key, item id 和 history list 的 host 的 host list
        #
        # 通过 Item Key 获取 Item history
        #
        #     hosts: 主机列表
        #     time_from: 开始时间
        #     time_till: 结束时间
        #     item_key: Item Key
        #     data_type: 数据类型
        #
        # 参考文档:
        #
        #     https://www.zabbix.com/documentation/6.0/en/manual/api/reference/history/get
        #
        # history
        #
        #     0 - numeric float
        #     1 - character
        #     2 - log
        #     3 - numeric unsigned
        #     4 - text
        #
        #     Default: 3
        #
        # 默认数据类型是 numeric unsigned (整数), 如果 history.get 返回的数据为 None, 有可能是 data_type 类型不对

        info: str = "Get history by item key"

        try:

            logger.info(f"{info} [started]")

            # match True:
            #     case True if not utils.isTrue(hosts, list):
            #         logger.error(f"{info} [hosts is not a list]")
            #         return None
            #     case True if not utils.isTrue(time_from, int):
            #         logger.error(f"{info} [time_from is not a integer]")
            #         return None
            #     case True if not utils.isTrue(time_till, int):
            #         logger.error(f"{info} [time_till is not a integer]")
            #         return None
            #     case True if not utils.isTrue(item_key, str):
            #         logger.error(f"{info} [item_key is not a string]")
            #         return None

            # 初始化变量
            # item_ids 获取历史数据时使用
            # item_history 历史数据集合, 最后返回
            item_ids: list = []
            item_history: list = []

            # Deep Copy(拷贝数据)
            # 父函数的变量是 list 或者 dict 类型, 父函数将变量传递个子函数, 如果子函数对变量数据进行了修改, 那么父函数的变量的数据也会被修改
            # 为了避免出现这种问题, 可以使用 Deep Copy 拷贝一份数据, 避免子函数修改父函数的变量的数据
            hosts = deepcopy(hosts)

            # --------------------------------------------------------------------------------------

            # Get Item
            hostids = [i["hostid"] for i in hosts]
            item_params = {
                "output": ["name", "itemid", "hostid"],
                "hostids": hostids,
                "filter": {"key_": item_key},
            }
            items = self.request("item.get", item_params)

            if items is None:
                return None

            # --------------------------------------------------------------------------------------

            # 因为 history 获取的顺序是乱的, 为了使输出和 hosts 列表顺序一致, 将 Item ID 追加到 hosts, 然后遍历 hosts 列表输出
            if not utils.isTrue(items.get("result"), list):
                logger.error(f"{info} [item key {item_key} not find]")
                return None

            for host in hosts:
                if not isinstance(items, dict):
                    return

                item: dict = next((item_object for item_object in items["result"] if host["hostid"] == item_object["hostid"]), "")  # type: ignore

                if utils.isTrue(item, dict) and item.get("itemid") is not None:
                    host["itemkey"] = item_key
                    host["itemid"] = item["itemid"]
                    item_ids.append(item["itemid"])
                    item_history.append(host)

            # 如果 ID 列表为空, 则返回 None
            if not utils.isTrue(item_ids, list):
                logger.error(f"{info} [item key {item_key} not find]")
                return None

            # --------------------------------------------------------------------------------------

            # Get History
            history_params = {
                "output": "extend",
                "history": data_type,
                "itemids": item_ids,
                "time_from": time_from,
                "time_till": time_till,
            }
            history = self.request("history.get", history_params)

            if history is None:
                return None

            # --------------------------------------------------------------------------------------------------

            if not utils.isTrue(history.get("result"), list):
                logger.error(f"{info} [item history not find]")
                return None

            for item in item_history:
                # 根据 itemid 提取数据
                item_history_data = [
                    history_result
                    for history_result in history["result"]
                    if item["itemid"] == history_result["itemid"]
                ]
                # 根据 clock 排序
                item_history_data = utils.list_dict_sorted_by_key(
                    item_history_data, "clock"
                )
                # 整合数据
                item["history"] = item_history_data

            logger.success(f"{info} [succeeded]")
            return item_history

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def get_history_by_interface(
        self,
        hosts: list,
        interfaces: list,
        time_from: int,
        time_till: int,
        direction: str,
    ) -> list | None:
        """获取网卡历史数据"""

        info: str = "Get history by interface"

        try:

            logger.info(f"{info} [started]")

            # match True:
            #     case True if not utils.isTrue(hosts, list):
            #         logger.error('ERROR!! hosts is not list or none')
            #         return None
            #     case True if not utils.isTrue(interfaces, list):
            #         logger.error('ERROR!! interfaces is not list or none')
            #         return None
            #     case True if not utils.isTrue(time_from, int):
            #         logger.error('ERROR!! time_from is not integer or zero')
            #         return None
            #     case True if not utils.isTrue(time_till, int):
            #         logger.error('ERROR!! time_till is not integer or zero')
            #         return None
            #     case True if not utils.isTrue(direction, str):
            #         logger.error('ERROR!! direction is not string or none')
            #         return None

            # 创建一个只有 网卡名称 的 列表
            interfaces_names: set = set(
                interface["interface"] for interface in interfaces
            )

            # 创建一个 Key 为 网卡名称 的 dictionary
            interfaces_dict: dict = {key: [] for key in interfaces_names}

            # 汇集 相同网卡名称 的 IP
            for interface in interfaces:
                interfaces_dict[interface["interface"]].append(interface["host"])

            # 获取历史数据
            history: list = []

            for key, value in interfaces_dict.items():

                hosts_by_ip = [
                    host
                    for v in value
                    for host in hosts
                    if v == host["interfaces"][0]["ip"]
                ]

                data = self.get_history_by_item_key(
                    hosts=hosts_by_ip,
                    time_from=time_from,
                    time_till=time_till,
                    item_key=f'net.if.{direction}["{key}"]',
                    data_type=3,
                )

                if data is None:
                    continue

                history += data

            logger.success(f"{info} [succeeded]")

            # 根据 name 排序
            return utils.list_dict_sorted_by_key(history, "name")

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def get_ips_by_hostgroup_name(self, hostgroup_name: str) -> list | None:
        """Get ips by hostgroup name"""

        info: str = "Get ips by hostgroup name"

        try:

            logger.info(f"{info} [started]")

            hosts = self.get_hosts_by_hostgroup_name(hostgroup_name)

            if hosts is None:
                return None

            hostids = [i["hostid"] for i in hosts]

            hostinterface = self.request(
                method="hostinterface.get", params={"hostids": hostids}
            )

            if hostinterface is None:
                return None

            logger.success(f"{info} [succeeded]")
            return [i["ip"] for i in hostinterface.get("result", [])]

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return None

    # ----------------------------------------------------------------------------------------------

    def create_object(
        self,
        ips: list,
        item: dict | None = None,
        trigger: dict | None = None,
        graph: bool | dict = False,
    ) -> bool:
        """create object"""

        # 创建对象
        #
        #     ips: IP列表
        #
        #     item:
        #
        #         name
        #         key_
        #
        #     trigger:
        #
        #         description
        #         expression (必须包含 {host}, 用于定义HOST)
        #
        # 参考文档:
        #
        #     https://www.zabbix.com/documentation/6.0/en/manual/api/reference/item/object
        #     https://www.zabbix.com/documentation/6.0/en/manual/config/items/itemtypes/zabbix_agent
        #     https://www.zabbix.com/documentation/6.0/en/manual/api/reference/trigger/object
        #
        # type:
        #
        #     0 - Zabbix agent
        #     2 - Zabbix trapper
        #     3 - Simple check
        #     5 - Zabbix internal
        #     7 - Zabbix agent (active)
        #     9 - Web item
        #     10 - External check
        #     11 - Database monitor
        #     12 - IPMI agent
        #     13 - SSH agent
        #     14 - Telnet agent
        #     15 - Calculated
        #     16 - JMX agent
        #     17 - SNMP trap
        #     18 - Dependent item
        #     19 - HTTP agent
        #     20 - SNMP agent
        #     21 - Script
        #
        # value_type:
        #
        #     0 - numeric float
        #     1 - character
        #     2 - log
        #     3 - numeric unsigned
        #     4 - text
        #
        # priority (integer): Severity of the trigger
        #
        #     0 - (default) not classified
        #     1 - information
        #     2 - warning
        #     3 - average
        #     4 - high
        #     5 - disaster

        info: str = "Create object"

        try:

            logger.info(f"{info} [started]")

            if not utils.isTrue(ips, list):
                logger.error(f"{info} [ips is not a list]")
                return False

            for ip in ips:

                item_id: str | None = None

                # ----------------------------------------------------------------------------------

                # Host Object

                logger.info(f"{info} [get host object]")

                response = self.request(
                    "hostinterface.get", {"filter": {"ip": ip}, "selectHosts": ["host"]}
                )

                if response is None:
                    continue

                # match True:
                #     case True if utils.isTrue(response, dict) and utils.isTrue(response.get('result'), list):
                #         logger.success(f"{info} [get host object] success: {response['result'][0]['hosts'][0]['host']}")
                #     case True if utils.isTrue(response, dict) and response.get('error'):
                #         logger.error(f"{info} [get host object] error: {response.get('error', {}).get('data')}")
                #         continue
                #     case _:
                #         logger.error(f"{info} [get host object] error: {ip}")
                #         continue

                host = response["result"][0]["hosts"][0]["host"]
                host_id = response["result"][0]["hostid"]
                interface_id = response["result"][0]["interfaceid"]

                # ----------------------------------------------------------------------------------

                # Create Item

                if isinstance(item, dict) and utils.isTrue(item, dict):

                    logger.info(f"{info} [create item]")

                    params = {
                        # 'name': None,
                        # 'key_': None,
                        "hostid": host_id,
                        "type": 7,
                        "value_type": 3,
                        "interfaceid": interface_id,
                        "delay": "1m",
                        "history": "7d",
                        "trends": "7d",
                    } | item

                    response = self.request("item.create", params)

                    if response is None or response.get("result") is None:
                        continue

                    # match True:
                    #     case True if utils.isTrue(response, dict) and response.get('result'):
                    #         logger.success(f"{log_prefix} success: {response.get('result')}")
                    #     case True if utils.isTrue(response, dict) and response.get('error'):
                    #         logger.error(f"{log_prefix} error: {response.get('error', {}).get('data')}")
                    #         continue
                    #     case True if utils.isTrue(response, utils.NoneType):
                    #         logger.error(f"{log_prefix} error: {response.get('error', {}).get('data')}")
                    #         continue
                    #     case _:
                    #         logger.error(f"{log_prefix} error: {item.get('name')}")
                    #         continue

                    item_id = response["result"]["itemids"][0]

                # ----------------------------------------------------------------------------------

                # Create Trigger

                if isinstance(trigger, dict) and utils.isTrue(trigger, dict):

                    logger.info(f"{info} [create trigger]")

                    params = {
                        # 'description': None,
                        "priority": "2",
                        # 'expression': None,
                        "manual_close": "1",
                    } | trigger

                    # Trigger 的 expression 需要指定 HOST, 例如:
                    #   'last(/DIYCL-110-30/system.uptime)<10m'
                    # DIYCL-110-30 就是 HOST
                    # 但是 HOST 是根据 IP 调用接口获取的, 所以可以写成动态的配置
                    #   'last(/{host}/system.uptime)<10m'.format(host='DIYCL-110-30')
                    # 所以, 传递参数的时候, expression 中就必须要有 {host}, 用于定义 HOST
                    # 如果传递参数的时候使用了 f-strings, 要保留 {host}, 再套一层 {} 即可
                    #   f'last(/{{host}}/system.uptime)<10m'
                    params["expression"] = f"{params['expression']}".format(host=host)

                    # 注意: create trigger 的 params 的类型是 list
                    response = self.request("trigger.create", [params])

                    if response is None or response.get("result") is None:
                        continue

                    # logger.warning(f'{log_prefix} response: {response}') if utils.isTrue(self.debug, bool) else next

                    # match True:
                    #     case True if utils.isTrue(response, dict) and response.get('result'):
                    #         logger.success(f"{log_prefix} success: {response.get('result')}")
                    #     case True if utils.isTrue(response, dict) and response.get('error'):
                    #         logger.error(f"{log_prefix} error: {response.get('error', {}).get('data')}")
                    #         continue
                    #     case True if utils.isTrue(response, utils.NoneType):
                    #         logger.error(f"{log_prefix} error: {response.get('error', {}).get('data')}")
                    #         continue
                    #     case _:
                    #         logger.error(f"{log_prefix} error: {trigger.get('name')}")
                    #         continue

                # ----------------------------------------------------------------------------------

                # Create Graph

                if utils.isTrue(graph, bool) or (
                    isinstance(graph, dict) and utils.isTrue(graph, dict)
                ):

                    log_prefix = "create graph"

                    logger.info(f"{log_prefix} ......")

                    # Graph object:
                    #
                    #   https://www.zabbix.com/documentation/current/en/manual/api/reference/graph/object
                    #
                    # yaxismax (float) The fixed maximum value for the Y axis.
                    #   Default: 100.
                    # yaxismin (float) The fixed minimum value for the Y axis.
                    #   Default: 0.
                    # ymax_type (integer) Maximum value calculation method for the Y axis.
                    #   Possible values:
                    #   0 - (default) calculated;
                    #   1 - fixed;
                    #   2 - item.
                    # ymin_type (integer) Minimum value calculation method for the Y axis.
                    #   Possible values:
                    #   0 - (default) calculated;
                    #   1 - fixed;
                    #   2 - item.
                    #
                    # 'ymin_type': 2,
                    # 'ymin_itemid':item_id,
                    # 'ymax_type': 2,
                    # 'ymax_itemid':item_id,

                    if item is None:
                        continue

                    params: dict = {
                        "name": item.get("name"),
                        "width": 900,
                        "height": 200,
                        "gitems": [{"itemid": item_id, "color": "0040FF"}],
                    }

                    if isinstance(graph, dict) and utils.isTrue(graph, dict):

                        params = params | graph

                        if utils.isTrue(params.get("gitems"), list):
                            gitems = params.get("gitems")
                            if gitems is None:
                                continue
                            for gitem in gitems:
                                if (
                                    isinstance(gitem, dict)
                                    and utils.isTrue(gitem, dict)
                                    and gitem.get("itemid") == "{}"
                                ):
                                    gitem["itemid"] = item_id

                    response = self.request("graph.create", params)

                    if response is None:
                        continue

                    # logger.warning(f'{log_prefix} response: {response}') if utils.isTrue(self.debug, bool) else next

                    # match True:
                    #     case True if utils.isTrue(response, dict) and response.get('result'):
                    #         logger.success(f"{log_prefix} success: {response.get('result')}")
                    #     case True if utils.isTrue(response, dict) and response.get('error'):
                    #         logger.error(f"{log_prefix} error: {response.get('error', {}).get('data')}")
                    #         continue
                    #     case True if utils.isTrue(response, utils.NoneType):
                    #         logger.error(f"{log_prefix} error: {response.get('error', {}).get('data')}")
                    #         continue
                    #     case _:
                    #         logger.error(f"{log_prefix} error: {params.get('name')}")
                    #         continue

                # ----------------------------------------------------------------------------------

            logger.success(f"{info} [succeeded]")
            return True

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False
