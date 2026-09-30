from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BatchSummary:
    batch_id: str
    started_at: datetime
    status: str = "running"
    records_read: int = 0
    records_rejected: int = 0
    records_loaded: int = 0
    rejection_reasons: dict[str, int] = field(default_factory=dict)
    finished_at: datetime | None = None