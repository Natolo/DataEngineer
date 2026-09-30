from pathlib import Path

import pytest
from retail_ingestion.csv_reader import read_sales


@pytest.fixture
def sales_csv_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "sales.csv"
    file_path.write_text("sale_id,sale_date,amount\nS001,2026-09-20,19.90\n", encoding="utf-8")
    return file_path


def test_read_sales_from_temporary_file(sales_csv_file: Path) -> None:
    # Act
    result = read_sales(sales_csv_file)

    # Assert
    assert len(result) == 1
    assert result[0]["sale_id"] == "S001"
    assert result[0]["amount"] == "19.90"
