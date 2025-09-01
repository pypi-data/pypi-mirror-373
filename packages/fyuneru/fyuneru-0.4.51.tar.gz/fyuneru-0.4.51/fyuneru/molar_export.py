from pathlib import Path
from typing import NamedTuple
from urllib.parse import unquote, urlparse

from fyuneru.geometry3d import SElement
from returns.maybe import Maybe
from toolz import curry


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


def parse_task_config(task: dict) -> dict:
    return task


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
    task_config: dict
    export_config: dict
    items: list[Item]


def parse_origin(origin: dict) -> ExportTask:
    task = origin.get("task")
    config = origin.get("config")
    data = origin.get("data")

    export_config = parse_export_config(config)
    task_config = parse_task_config(task)
    items = parse_items(data)

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
