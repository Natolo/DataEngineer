import json
from pathlib import Path
from typing import TypedDict
class Order(TypedDict):
    order_id: str
    order_date: str
    customer_id: str | None
    total: float | str
    status: str

def read_orders(file_path: Path) -> list[Order]:
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)