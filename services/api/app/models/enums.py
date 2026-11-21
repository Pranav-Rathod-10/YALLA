from enum import StrEnum


class Gender(StrEnum):
    female = "female"
    male = "male"
    other = "other"
    undisclosed = "undisclosed"


class Joining(StrEnum):
    approval = "approval"
    instant = "instant"


class TripStatus(StrEnum):
    open = "open"
    full = "full"
    cancelled = "cancelled"
    completed = "completed"


class RequestStatus(StrEnum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    cancelled = "cancelled"


class MemberRole(StrEnum):
    host = "host"
    traveller = "traveller"


class AlertKind(StrEnum):
    request = "request"
    accepted = "accepted"
    declined = "declined"
    query = "query"
    new_trip = "new_trip"
