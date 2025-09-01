"""
molar 客户端测试
"""

from pathlib import Path
from fyuneru.lib import read_json, write_json
from fyuneru.molar_client import MolarClient, MolarDomain

TOKEN = r"4374aa41-e56c-4a49-abb4-fe20aee65d12_67f6449d397661d5e98c3ad8_client"

molar_client = MolarClient(
    token=TOKEN,
    domain=MolarDomain.OTHER.value,
)


export_info, task_info, items = molar_client.get_export(
    read_json(Path("20-export-config.json")), thread_num=64, dsn_cache=True
)


write_json(data=task_info, json_path=Path("task_info.json"))
write_json(data=items, json_path=Path("items.json"))
