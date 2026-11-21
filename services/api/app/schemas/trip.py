import uuid
from datetime import date, datetime, time
from typing import Annotated, Literal

from pydantic import Field

from app.models.enums import Joining, TripStatus
from app.schemas.common import Schema, UserSummary
from app.schemas.place import PlaceOut


class TripCreate(Schema):
    from_place_id: uuid.UUID
    to_place_id: uuid.UUID
    depart_date: date = Field(description="Local date at the pickup place")
    window_start: time = Field(description="Local start of the departure window")
    window_minutes: Literal[15, 30] = 30
    passenger_seats: Annotated[
        int, Field(ge=1, le=3, description="Passenger seats, host not counted.")
    ] = 2
    joining: Joining = Joining.approval
    females_only: bool = False
    cost_shared: bool = True
    cost_per_person: Annotated[int | None, Field(ge=0)] = None
    title: Annotated[str | None, Field(max_length=120)] = None
    pickup: Annotated[str | None, Field(max_length=255)] = None
    vehicle: Annotated[str, Field(max_length=40)] = "Cab"


class TripOut(Schema):
    id: uuid.UUID
    title: str
    tag: str | None
    from_place: PlaceOut
    to_place: PlaceOut
    pickup: str
    departs_at: datetime = Field(description="Window start, ISO 8601 in the trip's timezone")
    window_ends_at: datetime
    timezone: str
    window_minutes: int
    passenger_seats: int
    seats_taken: int
    seats_left: int
    vehicle: str
    cost_per_person: int | None
    cost_shared: bool
    joining: Joining
    females_only: bool
    status: TripStatus
    host: UserSummary
    can_request: bool = Field(description="Whether the viewer may request this trip")


class TripDetail(TripOut):
    travellers: list[UserSummary]
