from datetime import datetime

from retail_ingestion.models import BatchSummary
from retail_ingestion.pipeline import record_rejection
from retail_ingestion.pipeline import process_sales


def test_record_rejection_updates_summary() -> None:
    started_at = datetime.fromisoformat("2024-06-01T12:00:00")
    summary = BatchSummary(
        batch_id="batch_1",
        started_at=started_at,
    )

    record_rejection(
        summary,
        ["Invalid amount", "Missing sale_id"],
    )
    record_rejection(
        summary,
        ["Invalid amount"],
    )

    assert summary.rejection_reasons == {
        "Invalid amount": 2,
        "Missing sale_id": 1,
    }
    assert summary.records_rejected == 2


def test_process_sales_updates_summary() -> None:
    started_at = datetime.fromisoformat("2024-06-01T12:00:00")
    summary = BatchSummary(
        batch_id="batch_1",
        started_at=started_at,
    )
    sales = [
        {"sale_id": "1", "amount": "100", "sale_date": "2026-09-20"},
        {"sale_id": "2", "amount": "abc", "sale_date": "2026-09-20"},
        {"sale_id": "", "amount": "-10", "sale_date": "2026-09-20"},
    ]

    result = process_sales(sales, summary)
    assert result is summary
    assert summary.records_read == 3
    assert summary.records_loaded == 1
    assert summary.records_rejected == 2
    assert summary.rejection_reasons == {
        "Missing sale_id": 1,
        "Invalid amount": 2,
    }


def test_process_valid_duplicates() -> None:
    started_at = datetime.fromisoformat("2024-06-01T12:00:00")
    summary = BatchSummary(
        batch_id="batch_1",
        started_at=started_at,
    )

    sales = [
        {"sale_id": "S001", "amount": "10", "sale_date": "2026-09-20"},
        {"sale_id": "S001", "amount": "10", "sale_date": "2026-09-20"},
        {"sale_id": "S002", "amount": "20", "sale_date": "2026-09-20"},
    ]

    result = process_sales(sales, summary)
    assert result is summary
    assert summary.records_read == 3
    assert summary.records_loaded == 2
    assert summary.records_rejected == 1
    assert summary.rejection_reasons == {
        "Duplicate sale_id": 1,
    }


def test_process_invalid_duplicates() -> None:
    started_at = datetime.fromisoformat("2024-06-01T12:00:00")
    summary = BatchSummary(
        batch_id="batch_1",
        started_at=started_at,
    )

    sales = [
        {"sale_id": "S001", "amount": "abc", "sale_date": "2026-09-20"},
        {"sale_id": "S001", "amount": "10", "sale_date": "2026-09-20"},
    ]

    result = process_sales(sales, summary)
    assert result is summary
    assert summary.records_read == 2
    assert summary.records_loaded == 1
    assert summary.records_rejected == 1
    assert summary.rejection_reasons == {
        "Invalid amount": 1,
    }