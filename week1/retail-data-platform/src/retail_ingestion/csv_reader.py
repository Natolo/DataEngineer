import csv
from pathlib import Path

def read_sales(file_path: Path) -> list[dict[str, str]]:
    with open(file_path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)
