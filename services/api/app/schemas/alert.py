import uuid
from datetime import datetime

from app.models.enums import AlertKind
from app.schemas.common import Schema, UserSummary


class AlertOut(Schema):
    id: uuid.UUID
    kind: AlertKind
    text: str = ""
    actor: UserSummary | None
    trip_id: uuid.UUID | None
    created_at: datetime
    read_at: datetime | None
