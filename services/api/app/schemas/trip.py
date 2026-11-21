import uuid
from datetime import date, time
from typing import Annotated, Literal

from pydantic import Field

from app.models.enums import Joining, TripStatus
from app.schemas.common import Schema, UserSummary
from app.schemas.place import PlaceOut


class TripCreate(Schema):
    from_place_id: uuid.UUID
    to_place_id: uuid.UUID
    depart_date: date
    window_start: time
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
    depart_date: date
    window_start: time
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


class TripDetail(TripOut):
    travellers: list[UserSummary]
