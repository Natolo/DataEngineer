import json
from pathlib import Path

def read_orders(file_path: Path) -> list[dict[str, object]]:
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)