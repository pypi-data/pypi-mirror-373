"""
molar http 客户端
"""

import random
import socket

from dataclasses import dataclass, field
from enum import Enum

import requests
from joblib import Parallel, delayed
from loguru import logger


from fyuneru.http_utils import find_labels, get_item_info, get_task_info


class MolarDomain(Enum):
    """
    域名
    """

    CN = "https://app.molardata.com"
    OTHER = "https://app.abaka.ai"


@dataclass
class MolarClient:
    """
    molar http 客户端
    """

    token: str
    domain: str = field(default=MolarDomain.CN.value)

    __required_structure = {
        "taskId": None,
        "exportMetadata": {"match": {"itemIds": None}},
    }

    def __to_export_info(self, export_config: dict) -> "MolarClient.ExportInfo":
        """
        将导出配置转换为导出信息
        """
        metadata = (
            export_config.get("exportMetadata", {})
            or export_config.get("metadata", {})
            or export_config.get("config", {})
        )
        return MolarClient.ExportInfo(
            origin_data=export_config,
            task_uid=export_config["taskId"],
            item_ids=metadata["match"].get("itemIds", []),
            task_alias=metadata["match"].get("taskAlias", {}),
        )

    def get_export(
        self, export_config: dict, thread_num: int = 16, dsn_cache: bool = False
    ) -> tuple[
        "MolarClient.ExportInfo", "MolarClient.TaskInfo", list["MolarClient.ItemInfo"]
    ]:
        """
        从http客户端导出
        """
        # self.__validate_export_task(export_config, self.__required_structure)
        # 使用 DNS 缓存
        sessions = [requests.Session() for _ in range(thread_num)]
        # host = None
        # if dsn_cache:
        #     origin_domain = self.domain
        #     host = origin_domain.replace("https://", "")
        #     ip = socket.gethostbyname(host)
        #     self.domain = f"https://{ip}"
        #     for session in sessions:
        #         session.mount("https://", SSLAdapter(server_hostname=host))
        export_info = self.__to_export_info(export_config=export_config)
        task_info = self.get_task_info(
            export_info.task_uid, session=random.choice(sessions)
        )
        logger.info(f"export: {len(export_info.item_ids)} items")

        items = Parallel(n_jobs=thread_num, backend="threading")(
            delayed(self.process_item)(
                item_id,
                task_info.uid,
                session=random.choice(sessions),
                # host=host,
            )
            for item_id in set(export_info.item_ids)
        )
        items = list(filter(None, items))

        if len(items) != len(export_info.item_ids):
            raise ValueError(
                f"items length: {len(items)} != export_info.item_ids length: {len(export_info.item_ids)}"
            )

        # if dsn_cache:
        #     self.domain = origin_domain
        return export_info, task_info, items

    def process_item(
        self,
        item_id: str,
        task_id: str,
        session: requests.Session | None = None,
        host: str | None = None,
    ) -> "MolarClient.ItemInfo":
        """处理条目"""
        item_info = self.get_item_info(item_id=item_id, session=session, host=host)
        labels = self.find_labels(
            task_id=task_id, item_id=item_id, session=session, host=host
        )
        item_info.labels = labels
        return item_info

    def get_task_info(
        self,
        task_id: str,
        session: requests.Session | None = None,
        host: str | None = None,
    ) -> "MolarClient.TaskInfo":
        """
        获取任务信息
        """
        while (
            response_json := get_task_info(
                task_id=task_id,
                token=self.token,
                domain=self.domain,
                session=session,
                host=host,
            )
        ) is None:
            continue
        data: dict = response_json.pop("data")
        return MolarClient.TaskInfo(
            uid=data.pop("_id"),
            domain_id=data.pop("domainId"),
            name=data.pop("name"),
            type=data.pop("type"),
            label_config=data["setting"].pop("labelConfig"),
            label_alias=data["setting"].pop("labelAlias"),
            origin_data=data,
        )

    def get_item_info(
        self,
        item_id: str,
        session: requests.Session | None = None,
        host: str | None = None,
    ) -> "MolarClient.ItemInfo":
        """获取条目"""
        while (
            response_json := get_item_info(
                item_id=item_id,
                token=self.token,
                domain=self.domain,
                session=session,
                host=host,
            )
        ) is None:
            continue
        data = response_json.pop("data")
        return MolarClient.ItemInfo(
            uid=data.pop("_id"),
            task_id=data.pop("taskId"),
            batch_id=data["packageInfo"].pop("_id"),
            info=data.pop("info"),
            origin_data=data,
        )

    def find_labels(
        self,
        task_id: str,
        item_id: str,
        session: requests.Session | None = None,
        host: str | None = None,
    ) -> list["MolarClient.LabelInfo"]:
        """获取标签"""
        while (
            response_json := find_labels(
                task_id=task_id,
                item_id=item_id,
                token=self.token,
                domain=self.domain,
                session=session,
                host=host,
            )
        ) is None:
            continue
        labels: list[dict] = response_json.pop("data")
        return [
            MolarClient.LabelInfo(
                origin_data=label,
                uid=label.pop("_id"),
                task_uid=label.pop("taskId"),
                item_uid=label.pop("itemId"),
                status=label.pop("status"),
                data=label.pop("data"),
            )
            for label in labels
        ]

    @dataclass
    class TaskInfo:
        """任务信息"""

        origin_data: dict
        uid: str
        domain_id: str
        name: str
        type: str
        label_config: dict = field(default_factory=dict)
        label_alias: dict = field(default_factory=dict)
        items: list["MolarClient.ItemInfo"] = field(default_factory=list)

    @dataclass
    class ItemInfo:
        """条目信息"""

        origin_data: list[dict]
        uid: str
        task_id: str
        batch_id: str
        info: dict = field(default_factory=dict)
        labels: list["MolarClient.LabelInfo"] = field(default_factory=list)

    @dataclass
    class LabelInfo:
        """标签信息"""

        origin_data: dict
        uid: str
        task_uid: str
        item_uid: str
        status: str
        data: dict = field(default_factory=dict)

    @dataclass
    class ExportInfo:
        """
        平台导出信息
        """

        origin_data: dict
        task_uid: str
        item_ids: list[str] = field(default_factory=list)
        task_alias: dict = field(default_factory=dict)
