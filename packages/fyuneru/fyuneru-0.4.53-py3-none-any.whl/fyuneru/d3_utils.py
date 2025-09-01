import re
from pathlib import Path

import lzf
import numpy as np
import pandas as pd

HEADER_PATTERN = re.compile(
    r"^(VERSION|FIELDS|SIZE|TYPE|COUNT|WIDTH|HEIGHT|VIEWPOINT|POINTS|DATA)"
)

TYPE_MAP = {
    ("U", 1): np.uint8,
    ("U", 2): np.uint16,
    ("U", 4): np.uint32,
    ("U", 8): np.uint64,
    ("I", 1): np.int8,
    ("I", 2): np.int16,
    ("I", 4): np.int32,
    ("I", 8): np.int64,
    ("F", 4): np.float32,
    ("F", 8): np.float64,
}


def parse_header(pcd_path: Path) -> tuple[dict, int, str]:
    """解析PCD文件头部信息, 平台sdk复制

    Args:
        pcd_path (Path): Path(../../xxx.pcd)

    Returns:
        tuple[dict, int, str]: header, data_start, encoding?
    """
    headers: dict = dict()
    data_start = 0
    encoding = "utf-8"

    try:
        with pcd_path.open("r", encoding=encoding) as f:
            lines = [next(f) for _ in range(11)]
    except UnicodeDecodeError:
        with pcd_path.open("rb") as f:
            lines = [next(f).decode("latin-1") for _ in range(11)]
        encoding = "binary"

    for idx, line in enumerate(lines):
        if match := HEADER_PATTERN.match(line):
            key = match.group()
            parts = line.strip().split()
            if key == "DATA":
                headers[key] = parts[1]
                data_start = idx + 1
            else:
                headers[key] = parts[1:] if len(parts) > 1 else parts[1]

    # 类型转换关键字段
    headers["POINTS"] = int(headers.get("POINTS", 0)[0])
    headers["WIDTH"] = int(headers.get("WIDTH", [0])[0])
    headers["HEIGHT"] = int(headers.get("HEIGHT", [0])[0])
    return headers, data_start, encoding


def build_dtype(fields: list, types: list, sizes: list, counts: list) -> np.dtype:
    """构建pcd numpy结构

    Args:
        fields (list): _description_
        types (list): _description_
        sizes (list): _description_
        counts (list): _description_

    Raises:
        ValueError: _description_

    Returns:
        np.dtype: _description_
    """
    dtype = []
    for field, type_char, size, count in zip(fields, types, sizes, counts):
        np_type = TYPE_MAP.get((type_char.upper(), int(size)), None)
        if np_type is None:
            raise ValueError(f"Unsupported type: {type_char}{size}")

        count = int(count)
        if count > 1:
            dtype.extend([(f"{field}_{i}", np_type) for i in range(count)])
        else:
            dtype.append((field, np_type))
    return np.dtype(dtype)


def read_ascii_data(pcd_path: str, data_start: int, dtype: np.dtype) -> np.ndarray:
    """读取ASCII格式的点云数据"""
    try:
        return np.loadtxt(pcd_path, skiprows=data_start, dtype=dtype)
    except ValueError:
        df = pd.read_csv(
            pcd_path,
            skiprows=data_start,
            sep=r"\s+",
            header=None,
            engine="python",
            dtype=dtype.str,
            on_bad_lines="warn",
        )
        return df.iloc[:, : len(dtype.names)].to_numpy().view(dtype)


def read_binary_data(
    pcd_path: str, data_start: int, dtype: np.dtype, encoding: str
) -> np.ndarray:
    with open(pcd_path, "rb") as f:
        for _ in range(data_start):
            f.readline()
        return np.fromfile(f, dtype=dtype)


def read_compressed_data(
    pcd_path: str, data_start: int, dt: np.dtype, width: int, height: int
) -> np.ndarray:
    with open(pcd_path, "rb") as f:
        for _ in range(data_start):
            _ = f.readline()

        compressed_size = np.frombuffer(f.read(4), dtype=np.uint32)[0]
        decompressed_size = np.frombuffer(f.read(4), dtype=np.uint32)[0]
        compressed_data = f.read(compressed_size)

        decompressed_data = lzf.decompress(compressed_data, decompressed_size)

    total_points = width * height
    pc_array_empty = np.empty(total_points, dtype=dt)

    buffer = memoryview(decompressed_data)

    for name in dt.names:
        itemsize = dt.fields[name][0].itemsize
        bytes_total = itemsize * total_points
        column = np.frombuffer(buffer[:bytes_total], dt.fields[name][0])
        pc_array_empty[name] = column
        buffer = buffer[bytes_total:]

    return pc_array_empty


def read_pcd(pcd_path: Path) -> tuple[np.ndarray, dict]:
    """
    读PCD
    Args:
        pcd_path: pcd路径
    Returns:
        points: NxM np数组
        headers: 头字典
    """
    # 解析头信息
    headers, data_start, encoding = parse_header(pcd_path)

    # 构建结构化数据类型
    dtype = build_dtype(
        headers["FIELDS"], headers["TYPE"], headers["SIZE"], headers["COUNT"]
    )

    # 根据数据格式进行读取
    data_format = headers["DATA"]
    if data_format == "ascii":
        points = read_ascii_data(pcd_path, data_start, dtype)
    elif data_format == "binary":
        data = read_binary_data(pcd_path, data_start, dtype, encoding)
        # 过滤全零数据点（根据实际需求可调整）
        # points = data[~np.all(data.view(np.uint8) == 0, axis=1)]
        points = data
    elif data_format == "binary_compressed":
        points = read_compressed_data(
            pcd_path, data_start, dtype, headers["WIDTH"], headers["HEIGHT"]
        )
    else:
        raise ValueError(f"Unsupported data format: {data_format}")

    # 转换为二维数组视图
    return np.array(points.view(dtype).tolist()), headers


def _read_pcd(file_path: str) -> tuple[np.ndarray, list[float]]:
    with open(file_path, "rb") as rbf:
        # read pcd header and get data type
        for line in rbf:
            line = line.strip().decode("utf-8")
            if line.startswith("VIEWPOINT"):
                viewpoint = [float(x) for x in line.split()[1:]]
            elif line.startswith("POINTS"):
                points_cnt = int(line.split()[1])
            elif line.startswith("DATA"):
                data_type = line.split()[1]
                break
        # read pcd data by binary, compressed or ascii
        if data_type == "binary":
            data = np.fromfile(rbf, dtype=np.float32).reshape(points_cnt, -1)
        # use lzf to decompress binary compressed data
        elif data_type == "binary_compressed":
            import lzf

            s0, s1 = np.frombuffer(rbf.read(8), dtype=np.uint32)
            data = np.frombuffer(lzf.decompress(rbf.read(s0), s1), dtype=np.float32)
            data = data.reshape(-1, points_cnt).T
        # read ascii data by loadtxt
        elif data_type == "ascii":
            data = np.loadtxt(rbf, dtype=np.float32)
        # raise error if data type is unknown
        else:
            raise ValueError(f"Unknown data type: {data_type}")
    return data, viewpoint
