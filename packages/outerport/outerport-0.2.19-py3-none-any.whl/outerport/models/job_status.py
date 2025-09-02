# outerport/models/job_status_model.py
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict


class JobStatus(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    status: str  # e.g. "queued", "processing", "done", "error", "cancelled"
    error_message: Optional[str] = None
    created_at: str

    def is_done(self) -> bool:
        return self.status == "done"

    def is_error(self) -> bool:
        return self.status == "error"

    def is_cancelled(self) -> bool:
        return self.status == "cancelled"
