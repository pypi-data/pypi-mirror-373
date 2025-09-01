# /bin/env python
# -*- coding: utf-8 -*-
"""
@author: inklov3
@date: 2025-07-16
@description: molar function tools
"""

import base64
import datetime
import hashlib
import json
from re import L
import sys
import uuid
from pathlib import Path, PurePath
from typing import Callable, Generator, Iterable, TextIO, TypeVar
from urllib.parse import unquote, urlparse

from tqdm import tqdm
import numpy as np
from blake3 import blake3
from loguru import logger
from loguru._logger import Logger as LoguruLogger
from returns.io import IO, impure_safe


def replace_suffix(file_name: str, suffix: str) -> str:
    """替换后缀"""
    parts = file_name.rsplit(".", maxsplit=1)
    stem_idx = 0
    return parts[stem_idx] + suffix


@impure_safe
def mkdir(path: Path) -> None:
    """创建目录"""
    path.mkdir(parents=True, exist_ok=True)


@impure_safe
def init_logger(level: str = "WARNING", logs_path: Path = Path("logs")) -> LoguruLogger:
    """
    初始化日志
    """
    print("init_logger")
    if getattr(logger, "_configured", False):
        return logger

    logger.remove()
    logger.add(
        sink=sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <7}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        level=level,
    )
    if logs_path:
        logs_path.mkdir(parents=True, exist_ok=True)
        log_path = logs_path / f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.log"
        logger.add(
            str(log_path),
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <7}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
            level=level,
            enqueue=True,
            encoding="utf-8",
        )
    setattr(logger, "_configured", True)
    logger.info("日志初始化完成")
    return logger


@impure_safe
def log_message(logger: LoguruLogger, message: str, level: str = "INFO") -> None:
    logger.log(level, message)


@impure_safe
def log_info(message: str) -> None:
    log_message(logger, message, "INFO")


@impure_safe
def log_warning(message: str) -> None:
    log_message(logger, message, "WARNING")


@impure_safe
def log_error(message: str) -> None:
    log_message(logger, message, "ERROR")


@impure_safe
def log_debug(message: str) -> None:
    log_message(logger, message, "DEBUG")


def tqdm_loguru(iterable, level="INFO", **tqdm_kwargs):
    """
    使用 loguru 打印 tqdm 进度的函数式包装器

    Args:
        iterable: 可迭代对象
        level: loguru 日志级别 (默认 INFO)
        **tqdm_kwargs: 传给 tqdm 的其它参数
    """

    class TqdmToLoguru:
        def __init__(self, log_level):
            self.log_level = log_level

        def write(self, buf):
            buf = buf.strip()
            if buf:
                logger.log(self.log_level, buf)

        def flush(self):
            pass

    return tqdm(iterable, file=TqdmToLoguru(level), **tqdm_kwargs)


def read_jsonl(file: Path) -> Iterable[dict]:
    """
    读jsonl
    """
    with open(file, "r", encoding="utf8") as file:
        for line in file:
            yield json.loads(line.strip())


def read_json(file: Path) -> dict:
    """
    读json
    """
    return json.loads(file.read_text())


class NonSerializable:
    """标记字段为不可序列化：序列化时将跳过此字段"""

    def __repr__(self):
        return "<NonSerializable>"


NON_SERIALIZABLE = NonSerializable()


def serialize(obj):
    """
    序列化
    """
    result = None
    # 基础类型或 None
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        result = obj
    elif isinstance(obj, (np.generic,)):
        result = obj.item()
    # NumPy 数组 -> Python 原生嵌套 list
    elif isinstance(obj, np.ndarray):
        result = obj.tolist()
    # 字典
    elif isinstance(obj, dict):
        result = {k: serialize(v) for k, v in obj.items() if v is not NON_SERIALIZABLE}
    # 具名元组（namedtuple）
    elif hasattr(obj, "_fields") and callable(getattr(obj, "_asdict", None)):
        return serialize(obj._asdict())
    # 列表/元组/集合
    elif isinstance(obj, (list, tuple, set)):
        result = [serialize(v) for v in obj if v is not NON_SERIALIZABLE]
    # 普通对象
    elif hasattr(obj, "__dict__"):
        filtered = {
            k: v for k, v in vars(obj).items() if not isinstance(v, NonSerializable)
        }
        result = serialize(filtered)
    else:
        raise TypeError(f"Unsupported serialization type: {type(obj)}")
    return result


def write_json(data: any, file: Path, indent=2):
    """
    写json
    """
    with open(file, "w", encoding="utf8") as file:
        json.dump(data, file, ensure_ascii=False, indent=indent, default=serialize)


def open_jsonl_writer(file: Path) -> TextIO:
    """
    打开jsonl写入器
    """
    return open(file, "a", encoding="utf8")


def send_jsonl(jsonl_writer: TextIO, data: dict, indent=2, default=serialize):
    line = json.dumps(data, ensure_ascii=False, indent=indent, default=default) + "\n"
    """
    发送jsonl
    """
    jsonl_writer.write(line)
    jsonl_writer.flush()


def hash_string(s: str, method="md5") -> str:
    """
    字符串hash
    """
    h = hashlib.new(method)
    h.update(s.encode("utf-8"))
    return h.hexdigest()


def partial_hash(file: Path, chunk_size=4 * 1024 * 1024) -> str:
    """
    分块hash
    """
    size = file.stat().st_size
    md5 = hashlib.md5()

    ranges = []
    ranges.append((0, chunk_size))  # 开头

    if size > chunk_size * 2:
        middle = max((size // 2) - (chunk_size // 2), chunk_size)
        ranges.append((middle, chunk_size))  # 中间

    if size > chunk_size:
        ranges.append((size - chunk_size, chunk_size))  # 结尾

    with file.open("rb") as f:
        for offset, length in ranges:
            f.seek(offset)
            md5.update(f.read(length))

    return md5.hexdigest()


def get_uuid() -> str:
    """
    获取uuid
    """
    random_uuid = uuid.uuid4()
    return str(random_uuid)


def get_timestamp() -> str:
    """
    获取时间戳
    """
    time = datetime.datetime.now()
    return time.strftime("%Y.%m.%d-%H:%M:%S.%f")


def search_with_suffix(path: Path, suffixes: set[str]) -> Generator[Path, None, None]:
    """递归查找目录后缀文件"""
    for f in path.rglob(r"*"):
        if f.suffix not in suffixes:
            continue
        yield f


def cut_url(
    url: str, start_level: int = 2, end_level: int = -1, with_file_name: bool = False
) -> PurePath:
    """切割url"""
    url_parse = urlparse(url)
    url_path = url_parse.path
    unquoted_url_path = Path(unquote(url_path))
    if with_file_name:
        end_level = len(unquoted_url_path.parts)
    return PurePath(*unquoted_url_path.parts[start_level:end_level])


def extract_url_path(url: str) -> PurePath:
    """提取url路径"""
    url_parse = urlparse(url)
    path = unquote(url_parse.path)
    return PurePath(path)


def recursive_replace(s: str, replace_map: dict[str, str]) -> str:
    """假递归替换"""
    for k, v in replace_map.items():
        s = s.replace(k, v)
    return s


def recursive_clean(s: str, clean_words: Iterable[str]) -> str:
    """假递归清理"""
    return recursive_replace(s, {word: "" for word in clean_words})


def to_hash(data: bytes, scheme: str = "blake3") -> str:
    match scheme:
        case "blake3":
            return blake3(data).hexdigest()
        case "md5":
            return hashlib.md5(data).hexdigest()
        case _:
            raise NotImplementedError(f"Unsupported hash scheme: {scheme}")


def to_base64(data: bytes) -> str:
    """
    转换为base64
    """
    return base64.b64encode(data).decode("utf-8")


def sort_dict(data: dict, sort_rule: Callable[any, int]) -> dict:
    """
    排序字典
    """
    return dict(sorted(data.items(), key=lambda x: sort_rule(x)))
