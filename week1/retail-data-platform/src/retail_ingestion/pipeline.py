from collections.abc import Iterable

from retail_ingestion.models import BatchSummary
from retail_ingestion.validation import validate_sale


def record_rejection(
    summary: BatchSummary,
    reasons: list[str],
) -> None:
    for reason in reasons:
        summary.rejection_reasons[reason] = (
            summary.rejection_reasons.get(reason, 0) + 1
        )
    summary.records_rejected += 1


def process_sales(
    sales: Iterable[dict[str, str]],
    summary: BatchSummary,
) -> BatchSummary:
    seen_sale_ids: set[str] = set()
    for sale in sales:
        summary.records_read += 1
        is_valid, errors = validate_sale(sale)
        if not is_valid:
            record_rejection(summary, errors)
            continue
        if sale["sale_id"] in seen_sale_ids:
            record_rejection(summary, ["Duplicate sale_id"])
            continue
        seen_sale_ids.add(sale["sale_id"])
        summary.records_loaded += 1
    return summary