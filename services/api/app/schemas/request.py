import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from app.models.enums import RequestStatus
from app.schemas.common import Schema, UserSummary


class RequestCreate(Schema):
    message: Annotated[str | None, Field(max_length=1024)] = None


class RequestDecision(Schema):
    status: Literal[RequestStatus.accepted, RequestStatus.declined]


class TripRequestOut(Schema):
    id: uuid.UUID
    trip_id: uuid.UUID
    trip_title: str
    requester: UserSummary
    host: UserSummary
    message: str | None
    status: RequestStatus
    created_at: datetime
    decided_at: datetime | None
