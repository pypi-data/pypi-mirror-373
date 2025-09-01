from enum import Enum
from functools import singledispatch
from inspect import signature
from itertools import islice
from pathlib import Path
from typing import NamedTuple
from .lib import read_json

from .fp_entity import (
    ExportConfig,
    Frame,
    Item,
    Label,
    LabelConfig,
    OriginData,
    TaskConfig,
)


def fst(iterable):
    return next(iter(iterable))


def snd(iterable, default=None):
    return next(islice(iterable, 1, None), default)


def deep_get(obj: dict, path: str, default=None):
    """多级字典取值"""
    if not obj or not path:
        return default

    def _get_value(obj: dict | list, key: str, default=None):
        if key.isdigit():
            return obj[int(key)]
        return obj.get(key, default)

    keys = path.split(".", maxsplit=1)
    key = fst(keys)
    other_key = snd(keys, None)
    if other_key:
        return deep_get(_get_value(obj, key, default), other_key, default)
    return _get_value(obj, key, default)


def get_label_alias(task_alias: dict) -> dict[str, str]:
    """获取任务标签别名"""

    def _get_alias(label_alias: dict):
        if not isinstance(label_alias, dict):
            return None
        return label_alias.get("label", None)

    return {key: _get_alias(label_alias) for key, label_alias in task_alias.items()}


def get_label_config(label_config: list[dict]) -> dict[str, LabelConfig]:
    """获取任务标签设置"""

    def _extract_label_config(label_config: dict):
        return LabelConfig(
            label=label_config["label"],
            color=label_config["color"],
            draw_type=label_config["drawType"],
        )

    return {
        label_config["label"]: _extract_label_config(label_config)
        for label_config in label_config
    }


@singledispatch
def to_export(data) -> tuple[TaskConfig, ExportConfig, list[Item]]:
    raise NotImplementedError(f"to_export not implemented for {type(data)}")


def extract_export_config(export_config: dict) -> ExportConfig:
    """
    提取导出配置
    Args:
        export_config (dict): 导出配置 # TODO 兼容前端拉取与originData

    Returns:
        label_alias_map (dict[str, str]): 标签别名映射
        export_items (list[str]): 导出条目id
    """
    label_alias_path = "taskAlias"
    label_alias_map = get_label_alias(deep_get(export_config, label_alias_path))
    item_uids_path = "match.itemIds"
    item_uids = deep_get(export_config, item_uids_path)
    return ExportConfig(
        label_alias_map=label_alias_map,
        item_uids=item_uids,
        origin=export_config,
    )


def extract_task_config(task_data: dict) -> TaskConfig:
    label_config_path = "setting.labelConfig"
    label_configs = get_label_config(deep_get(task_data, label_config_path))
    return TaskConfig(
        uid=task_data["_id"],
        domain_id=task_data["domainId"],
        name=task_data["name"],
        label_configs=label_configs,
        task_type=task_data["type"],
        origin=task_data,
    )


def zip_urls_and_sizes(
    url_list: list[str], sizes: list[dict]
) -> list[tuple[str, dict]]:
    if len(url_list) % len(sizes) != 0:
        raise ValueError("url_list and sizes length mismatch")
    repeat_times = (len(url_list) + len(sizes) - 1) // len(sizes)
    # 扩展 sizes
    sizes = (sizes * repeat_times)[: len(url_list)]
    return zip(url_list, sizes)


def extract_frames_iat(item_info: dict) -> list[Frame]:
    url_list: list[str] = deep_get(item_info, "info.info.url", [])
    sizes: list[dict] = deep_get(item_info, "info.info.size", [])
    return [
        Frame(index=idx, url=url, size=size, urls=None, origin=item_info)
        for idx, (url, size) in enumerate(zip_urls_and_sizes(url_list, sizes))
    ]


def extract_labels(item_labels: dict) -> list[Label]:
    def _extract_label(label_data: dict) -> Label:
        return Label(
            uid=label_data["_id"],
            label_id=deep_get(label_data, "data.id"),
            label=deep_get(label_data, "data.label"),
            draw_type=deep_get(label_data, "data.drawType"),
            frame_index=deep_get(label_data, "data.frameIndex", default=0),
            hash=deep_get(label_data, "data.hash", default=None),
            group=deep_get(label_data, "data.group", default=0),
            points=deep_get(label_data, "data.points", default=[]),
            lens_index=deep_get(label_data, "data.lensIndex", default=0),
            origin=label_data,
        )

    return [_extract_label(label_data) for label_data in item_labels]


@to_export.register
def _(data: OriginData) -> tuple[TaskConfig, ExportConfig, list[Item]]:
    export_config = extract_export_config(data.config)
    task_config = extract_task_config(data.task)

    def _extract_item(item_data: dict) -> Item:
        return Item(
            uid=item_data["_id"],
            batch_uid=deep_get(item_data, "item.batchId"),
            frames=extract_frames_iat(item_data),
            labels=extract_labels(item_data["labels"]),
            origin=item_data,
        )

    items = [_extract_item(item_data) for item_data in data.data]

    return task_config, export_config, items


def json_file_to_origin(json_file: Path) -> OriginData:
    j = read_json(json_file)
    j["label_config"] = j.pop("labelConfig")
    return OriginData(**{k: j[k] for k in signature(OriginData).parameters if k in j})
