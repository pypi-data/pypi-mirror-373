from pathlib import Path
from typing import NamedTuple
from urllib.parse import unquote, urlparse

import numpy as np
from fyuneru.geometry3d import SElement
from returns.maybe import Maybe
from toolz import curry


class TaskConfig(NamedTuple):
    uid: str
    domain_id: str
    name: str


class Label(NamedTuple):
    uid: str
    id: int
    draw_type: str
    hash: str
    label: str
    frame_index: int
    lens_index: Maybe[int]
    points: Maybe[list]
    attributes: Maybe[dict]


class Frame(NamedTuple):
    idx: int
    url: str
    imgUrls: Maybe[list[str]]
    location: Maybe[SElement]


class Item(NamedTuple):
    uid: str
    batch_uid: str
    labels: list[Label]
    frames: list[Frame]


def is_merge(urls: list[str]) -> bool:
    """
    urls 是否是合并任务
    """
    return len(urls) == 1


def extract_frames(item: dict) -> list[Frame]:
    info = item["info"]["info"]
    locations = info.get("locations", [])
    image_urls = (
        info.get("url")
        or info.get("imgUrls")
        or [location["imgUrls"] for location in locations]
    )
    urls = info.get("pcdUrls") or info["urls"]
    # locations 出现可能是叠帧、重建
    if locations:
        if is_merge(urls):
            return [
                Frame(idx=idx, url=url, imgUrls=imgUrls, location=location)
                for idx, (url, imgUrls, location) in enumerate(
                    zip(urls * len(locations), image_urls, locations)
                )
            ]
        return [
            Frame(idx=idx, url=url, imgUrls=imgUrls, location=location)
            for idx, (url, imgUrls, location) in enumerate(
                zip(urls, image_urls, locations)
            )
        ]
    # 没有 locations 但是有 urls 单帧点云
    elif urls:
        return [
            Frame(idx=idx, url=url, imgUrls=imgUrls, location=None)
            for idx, (url, imgUrls) in enumerate(zip(urls, image_urls))
        ]
    # 没有 pcd 就是 2D 任务
    elif image_urls:
        return [
            Frame(idx=idx, url=url, imgUrls=None, location=None)
            for idx, url in enumerate(image_urls)
        ]
    else:
        raise ValueError("Unknown task")


def extract_label(label: dict) -> Label:
    label_data = label["data"]
    uid = label["_id"]
    id = label_data["id"]
    draw_type = label_data["drawType"]
    hash = label_data["hash"]
    label = label_data["label"]
    frame_index = label_data["frameIndex"]
    lens_index = label_data.get("lensIndex", None)
    points = label_data.get("points", None)
    attributes = label_data.get("attributes", None)
    return Label(
        uid=uid,
        id=id,
        draw_type=draw_type,
        hash=hash,
        label=label,
        frame_index=frame_index,
        lens_index=lens_index,
        points=points,
        attributes=attributes,
    )


def extract_labels(item: dict) -> list[Label]:
    return [extract_label(label=label) for label in item["labels"]]


def parse_task_config(task: dict) -> TaskConfig:
    uid = task["_id"]
    domain_id = task["domainId"]
    name = task["name"]
    return TaskConfig(uid=uid, domain_id=domain_id, name=name)


def parse_export_config(config: dict) -> dict:
    return config


def parse_item(item: dict) -> Item:
    uid = item["_id"]
    batch_uid = item["item"]["batchId"]
    labels = extract_labels(item)
    frames = extract_frames(item)

    return Item(uid=uid, batch_uid=batch_uid, labels=labels, frames=frames)


def parse_items(items: list[dict]) -> list[Item]:
    return [parse_item(item) for item in items]


class ExportTask(NamedTuple):
    task_config: TaskConfig
    export_config: dict
    items: list[Item]


def parse_origin(origin: dict) -> ExportTask:
    task = origin.get("task")
    config = origin.get("config")
    data = origin.get("data")

    export_config = parse_export_config(config)
    task_config: TaskConfig = parse_task_config(task)
    items: list[Item] = parse_items(data)

    return ExportTask(task_config=task_config, export_config=export_config, items=items)


def url_to_path(url: str) -> Path:
    parsed_url_path = urlparse(url).path
    unquote_path = unquote(parsed_url_path)
    return Path(unquote_path)


def calculate_resource_dst(sub_path: Path, dst_root: Path, level: int) -> Path:
    return dst_root / Path(*sub_path.parts[level:])


@curry
def build_frame_resource(frame: Frame, dst_root: Path, level: int) -> dict[Path, str]:
    path_url_dict = dict()
    main_resource_path = url_to_path(frame.url)
    path_url_dict[calculate_resource_dst(main_resource_path, dst_root, level)] = (
        frame.url
    )
    if frame.imgUrls:
        path_url_dict.update(
            {
                calculate_resource_dst(url_to_path(img_url), dst_root, level): img_url
                for img_url in frame.imgUrls
            }
        )
    return path_url_dict


def extract_translation(label: Label) -> np.ndarray:
    points = label.points
    translation = slice(0, 3)
    return np.array(points[translation])


def extract_rpy(label: Label) -> np.ndarray:
    points = label.points
    rpy = slice(3, 6)
    return np.array(points[rpy])


def extract_half_size(label: Label) -> np.ndarray:
    points = label.points
    # 兼容预设矩形
    if len(points) != 9:
        points = points.tolist() + [0] * (9 - len(points))
    box_lwh = slice(6, 9)
    box_lwh = np.array(points[box_lwh])
    box_size = box_lwh / 2
    box_size = np.array(
        [
            -box_size[0],
            box_size[0],
            -box_size[1],
            box_size[1],
            -box_size[2],
            box_size[2],
        ]
    )
    return box_size
