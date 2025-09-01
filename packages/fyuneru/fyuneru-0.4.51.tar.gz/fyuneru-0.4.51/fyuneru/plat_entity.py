"""
molar平台导入导出实体
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple

from fyuneru.lib import NonSerializable

from .d3_entity import SElement
from .plat_export import Label

OSS_HTTP_ROOT = r"https://molar-app-prod-v5.oss-cn-hangzhou.aliyuncs.com/"


@dataclass
class CameraConfig:
    """
    相机配置
    """

    name: str = field(default="")
    extrinsic: list[list[float]] = field(default_factory=list)
    intrinsic: list[float] = field(default_factory=list)
    distortion: dict[str, float] = field(default_factory=dict)
    fusionModel: str = field(default="")


@dataclass
class CameraConfigV3:
    name: str = field(default=None)
    extrinsic: list = field(default_factory=list)
    intrinsic: list = field(default_factory=list)
    distortion: dict = field(default=None)
    projectionModel: str = field(default=None)


class ImportItem(NamedTuple):
    """平台导入数据条目单位"""

    info: any
    preData: list | NonSerializable


@dataclass
class Location:
    name: str = field(default=None)
    urls: list[str] = field(default=None)
    posMatrix: list[float] = field(default=None)


@dataclass
class LabelConfig:
    """
    标签配置
    """

    key: str = field(default=None)
    color: str = field(default=None)
    name: str = field(default=None)
    draw_type: str = field(default=None)
    alias: str = field(default=None)


# 支持平台任务类型
class PlatTaskType(Enum):
    IAT = "iat"
    PCAT_D23 = "pcat_d23"


@dataclass
class TaskConfig:
    id: str
    type: str = field(default=None)
    camera_num: int = field(default=1)
    labels: dict[str, Label] = field(default_factory=dict)
    origin_config: dict = field(default_factory=dict)
    origin_task: dict = field(default_factory=dict)


@dataclass
class Annotation:
    uuid: str = field(default=None)
    id: int = field(default=None)
    lens_index: int = field(default=0)
    frame_index: int = field(default=-1)
    draw_type: str = field(default=None)
    points: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
    group: int = field(default=-1)
    alias: str = field(default=None)
    p_label_id_map: list[int] = field(default_factory=list)
    connection: int = field(default=-1)


@dataclass
class Frame:
    url: str = field(default=None)
    width: int = field(default=1024)
    height: int = field(default=1024)
    frame_index: int = field(default=-1)
    lens_index: int = field(default=0)
    annotations: dict[str, Annotation] = field(default_factory=dict)
    urls: list[str] = field(default_factory=list)
    pose: SElement = field(default=None)
    camera_config: list[CameraConfig] = field(default=None)


@dataclass
class Item:
    uid: str
    batch_uid: str
    task_config: TaskConfig
    frames: dict = field(default_factory=dict)
    origin_data: dict = field(default_factory=dict)


@dataclass
class D2Info:

    @dataclass
    class Size:
        width: int
        height: int

    url: list[str] = field(default_factory=list)
    size: list[Size] = field(default=None)


@dataclass
class Lod:
    baseUrl: str = field(default=None)
    loadUrl: str = "metadata.json"
    offset: list[float] = field(default=None)


@dataclass
class D3Info:
    pcdUrl: list[str]
    imgUrls: list[str] = field(default=None)
    cameraConfigs: list[list[CameraConfig]] = field(default=None)
    locations: list[Location] = field(default=None)


@dataclass
class D4Info:
    pcdUrl: list[str]
    cameraConfigs: list[list[CameraConfig]] = field(default=None)
    locations: list[Location] = field(default=None)


@dataclass
class ImportInfo:
    info: any
    preData: list = field(default_factory=list)
