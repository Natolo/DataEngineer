from datetime import datetime

from retail_ingestion.models import BatchSummary


def test_batch_summary_has_expected_defaults() -> None:
    started_at = datetime.fromisoformat("2024-06-01T12:00:00")

    summary = BatchSummary(
        batch_id="batch_1",
        started_at=started_at,
    )

    assert summary.batch_id == "batch_1"
    assert summary.started_at == started_at
    assert summary.status == "running"
    assert summary.records_read == 0
    assert summary.records_loaded == 0
    assert summary.records_rejected == 0
    assert summary.rejection_reasons == {}
    assert summary.finished_at is None


def test_batch_summaries_do_not_share_rejection_reasons() -> None:
    started_at = datetime.fromisoformat("2024-06-01T12:00:00")
    first_summary = BatchSummary(
        batch_id="batch_1",
        started_at=started_at,
    )
    second_summary = BatchSummary(
        batch_id="batch_2",
        started_at=started_at,
    )

    first_summary.rejection_reasons["invalid_format"] = 2

    assert first_summary.rejection_reasons == {"invalid_format": 2}
    assert second_summary.rejection_reasons == {}