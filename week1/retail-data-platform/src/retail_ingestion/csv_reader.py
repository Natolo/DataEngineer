import csv
from pathlib import Path
from collections.abc import Iterator


# carica tutto il CSV in memoria
def read_sales(file_path: Path) -> list[dict[str, str]]:
    with open(file_path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


# legge il CSV riga per riga, utile per file grandi
def iter_sales(file_path: Path) -> Iterator[dict[str, str]]:
    with open(file_path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield row