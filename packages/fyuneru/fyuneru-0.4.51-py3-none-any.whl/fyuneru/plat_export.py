"""平台导出工程"""

from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from .lib import read_json
from .molar_client import MolarClient


@dataclass
class LabelConfig:
    """标签配置"""

    label: str
    alias: str
    drawType: str  # pylint: disable=invalid-name
    color: str
    key: str


@dataclass
class TaskConfig:
    """任务配置"""

    task_id: str
    export_id: str
    label_configs: dict[str, LabelConfig] = field(default_factory=dict)


@dataclass
class Frame:
    """帧"""

    index: int
    lens_index: int
    url: str
    urls: list[str] = field(default_factory=list)
    # x: width, y: height, z: depth
    size: list[float] = field(default_factory=list)


@dataclass
class Label:
    """标签"""

    label_id: int
    uid: str
    label: str
    draw_type: str
    frame_index: int
    points: list = field(default_factory=list)
    lens_index: int = field(default=0)
    group: int = field(default=0)
    attributes: dict = field(default_factory=dict)


@dataclass
class Item:
    """条目"""

    uid: str
    batch_uid: str
    task_config: TaskConfig
    frames: dict[int, Frame] = field(default_factory=dict)
    labels: dict[str, Label] = field(default_factory=dict)


def get_label_config(
    export_info: MolarClient.ExportInfo, task_info: MolarClient.TaskInfo
):
    """获取标签配置"""
    label_configs: dict[str, LabelConfig] = {}
    for label_config in task_info.label_config:
        label = label_config["label"]
        alias = label
        draw_type = label_config["drawType"]
        color = label_config["color"]
        key = label_config["key"]
        label_configs[alias] = LabelConfig(
            label=label, alias=alias, drawType=draw_type, color=color, key=key
        )
    if not export_info.task_alias:
        logger.info("Task alias not configured")
        return label_configs
    for label, values in export_info.task_alias.items():

        if not isinstance(values, dict) or "label" not in values:
            continue
        alias = values["label"]
        label_configs[label].alias = alias
        label_configs[alias] = label_configs.pop(label)
    return label_configs


def parse_iat_frames(
    item: MolarClient.ItemInfo,
) -> dict[int, Frame]:
    """解析条目"""
    frames: dict[int, Frame] = {}
    for idx, frame in enumerate(item.info["url"]):
        frame_url = frame
        size = [item.info["size"][idx]["width"], item.info["size"][idx]["height"]]
        len_index = 0
        frames[idx] = Frame(
            index=idx,
            lens_index=len_index,
            url=frame_url,
            size=size,
        )
    return frames


def parse_iat_labels(labels: list[MolarClient.LabelInfo]) -> dict[str, Label]:
    """解析标签"""
    export_labels: dict[str, Label] = {}
    for label in labels:
        label_id = label["data"]["id"]
        uid = label.uid
        label = label["data"]["label"]
        draw_type = label["data"]["drawType"]
        group = label["data"]["group"]
        attributes = label["data"].get("attributes", {})
        frame_index = label["data"]["frameIndex"]
        lens_index = label["data"]["lensIndex"]
        points = label["data"]["points"]
        export_labels[uid] = Label(
            label_id=label_id,
            uid=uid,
            label=label,
            draw_type=draw_type,
            frame_index=frame_index,
            lens_index=lens_index,
            group=group,
            attributes=attributes,
            points=points,
        )
    return export_labels


def get_items(task_config: TaskConfig, items: list[MolarClient.ItemInfo]):
    """获取条目"""
    export_items: list[Item] = []
    for item in items:
        item_uid = item.uid
        batch_uid = item.batch_id
        item_frames: dict[int, Frame] = parse_iat_frames(item=item)
        item_labels: dict[str, Label] = parse_iat_labels(labels=item.labels)
        export_items.append(
            Item(
                uid=item_uid,
                batch_uid=batch_uid,
                task_config=task_config,
                frames=item_frames,
                labels=item_labels,
            )
        )
    return export_items


def get_export_task_info(
    task_info: MolarClient.TaskInfo, export_info: MolarClient.ExportInfo
):
    """获取导出任务信息"""
    task_id = task_info.uid
    export_id = (
        export_info.origin_data.get("_id", None)
        or export_info.origin_data["exportTaskId"]
    )
    label_configs = get_label_config(export_info, task_info)
    return TaskConfig(
        task_id=task_id,
        export_id=export_id,
        label_configs=label_configs,
    )


def export(token: str, export_jsons_path: Path, domain: str) -> tuple[list[Item], int]:
    """导出数据"""
    molar_client = MolarClient(token=token, domain=domain)
    export_jsons = read_json(export_jsons_path)
    export_idx = len(export_jsons) - 1
    export_info, task_info, items = molar_client.get_export(
        export_config=export_jsons[export_idx], thread_num=64, dsn_cache=True
    )
    task_config = get_export_task_info(task_info=task_info, export_info=export_info)
    export_items = get_items(task_config=task_config, items=items)
    return export_items, export_idx
