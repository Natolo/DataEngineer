from pathlib import Path

def get_data_file(filename: str) -> Path:
    return Path(__file__).parent.parent.parent / "data" / filename