import uuid
from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Time,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAt, UUIDPk
from app.models._types import str_enum
from app.models.enums import Joining, MemberRole, RequestStatus, TripStatus


class Trip(UUIDPk, CreatedAt, Base):
    """Fields follow spec sections 7.5, 11 and 12 as written."""

    __tablename__ = "trips"

    host_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    tag: Mapped[str | None] = mapped_column(String(40))
    from_place_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("places.id"))
    to_place_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("places.id"))
    pickup: Mapped[str] = mapped_column(String(255))
    depart_date: Mapped[date] = mapped_column(Date)
    window_start: Mapped[time] = mapped_column(Time)
    window_minutes: Mapped[int] = mapped_column(SmallInteger)
    # Spec 7.5: total = seats + 1 (host included), going starts at 1 (the host).
    seats_total: Mapped[int] = mapped_column(SmallInteger)
    going: Mapped[int] = mapped_column(SmallInteger, default=1)
    vehicle: Mapped[str] = mapped_column(String(40), default="Cab")
    cost_per_person: Mapped[int | None] = mapped_column(Integer)
    cost_shared: Mapped[bool] = mapped_column(Boolean, default=True)
    joining: Mapped[Joining] = mapped_column(str_enum(Joining, "joining"), default=Joining.approval)
    females_only: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[TripStatus] = mapped_column(
        str_enum(TripStatus, "trip_status"), default=TripStatus.open
    )

    __table_args__ = (
        CheckConstraint("window_minutes IN (15, 30)", name="window_minutes"),
        CheckConstraint("seats_total BETWEEN 2 AND 4", name="seats_total"),
        CheckConstraint("going BETWEEN 1 AND seats_total", name="going"),
        CheckConstraint("cost_per_person IS NULL OR cost_per_person >= 0", name="cost"),
        Index("ix_trips_status_date", "status", "depart_date"),
    )


class TripMember(Base):
    __tablename__ = "trip_members"

    trip_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role: Mapped[MemberRole] = mapped_column(str_enum(MemberRole, "member_role"))
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class TripRequest(UUIDPk, CreatedAt, Base):
    __tablename__ = "trip_requests"

    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    requester_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str | None] = mapped_column(String(1024))
    status: Mapped[RequestStatus] = mapped_column(
        str_enum(RequestStatus, "request_status"), default=RequestStatus.pending
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index(
            "uq_trip_requests_live",
            "trip_id",
            "requester_id",
            unique=True,
            postgresql_where=text("status IN ('pending', 'accepted')"),
        ),
        Index("ix_trip_requests_requester", "requester_id", "created_at"),
        Index("ix_trip_requests_trip_status", "trip_id", "status"),
    )


class SavedTrip(Base):
    __tablename__ = "saved_trips"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"), primary_key=True
    )
