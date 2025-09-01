from pathlib import Path
from fyuneru.lib import read_json
from fyuneru.fp_utils import json_file_to_origin, to_export


def main():
    SRC = r"/root/fyuneru-pylib/test/"
    task_config, export_config, items = to_export(
        json_file_to_origin(Path(SRC) / "data.json")
    )


if __name__ == "__main__":
    main()
