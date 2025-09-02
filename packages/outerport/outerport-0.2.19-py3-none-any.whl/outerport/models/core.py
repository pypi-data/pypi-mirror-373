from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Union


class BoundingBox(BaseModel):
    x0: Union[int, float]
    y0: Union[int, float]
    x1: Union[int, float]
    y1: Union[int, float]


class VisualComponent(BaseModel):
    id: UUID
    type: str
    document_id: UUID
    page_number: int
    label: str
    bbox: BoundingBox
    description: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None
