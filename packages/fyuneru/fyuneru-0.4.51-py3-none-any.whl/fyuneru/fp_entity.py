from enum import Enum
from typing import NamedTuple


class OriginData(NamedTuple):
    task: dict
    config: dict
    data: dict
    label_config: dict


class Frame(NamedTuple):
    index: int
    url: str
    urls: list[str] | None
    size: dict | None
    origin: dict


class Label(NamedTuple):
    uid: str
    hash: str
    label_id: int
    group: int
    label: str
    draw_type: str
    points: list
    frame_index: int
    lens_index: int
    origin: dict


class Item(NamedTuple):
    uid: str
    batch_uid: str
    frames: list[Frame]
    labels: list[Label]
    origin: dict


class LabelConfig(NamedTuple):
    label: str
    color: str
    draw_type: str


class TaskType(Enum):
    IAT: str = "IAT"
    PCAT: str = "PCAT"
    PCAT3: str = "PCAT3"


class TaskConfig(NamedTuple):
    uid: str
    domain_id: str
    name: str
    label_configs: dict[str, LabelConfig]
    task_type: str
    origin: dict


class ExportConfig(NamedTuple):
    item_uids: list[str]
    label_alias_map: dict[str, str]
    origin: dict
