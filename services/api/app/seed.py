"""Demo data for local development:  uv run python -m app.seed

Idempotent: does nothing if places already exist. Covers several cities (YAL-001), so the app
is never tested as Goa-only. All people and events are made up."""

import asyncio
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.models import Event, Place, Trip, TripMember, User
from app.models.enums import Gender, Joining, MemberRole

IST, GST = "Asia/Kolkata", "Asia/Dubai"

# name, address, city, lat, lng, timezone
PLACES = [
    ("Panjim", "Panjim, North Goa, Goa", "Goa", 15.4909, 73.8278, IST),
    ("Margao", "Margao, South Goa, Goa", "Goa", 15.2832, 73.9862, IST),
    ("Vasco da Gama", "Vasco da Gama, South Goa, Goa", "Goa", 15.3860, 73.8440, IST),
    ("Mapusa", "Mapusa, North Goa, Goa", "Goa", 15.5915, 73.8089, IST),
    ("Calangute", "Calangute, North Goa, Goa", "Goa", 15.5440, 73.7553, IST),
    ("Candolim", "Candolim, North Goa, Goa", "Goa", 15.5180, 73.7620, IST),
    ("Anjuna", "Anjuna, North Goa, Goa", "Goa", 15.5733, 73.7407, IST),
    ("Vagator", "Vagator, North Goa, Goa", "Goa", 15.6020, 73.7440, IST),
    ("Palolem", "Palolem, Canacona, South Goa", "Goa", 15.0100, 74.0232, IST),
    ("Dudhsagar Falls", "Sonaulim, Sanguem, Goa border", "Goa", 15.3144, 74.3143, IST),
    ("Manohar International Airport", "Mopa, Pernem, North Goa", "Goa", 15.7442, 73.8606, IST),
    ("Gokarna", "Gokarna, Uttara Kannada, Karnataka", "Gokarna", 14.5479, 74.3188, IST),
    ("Hampi", "Hampi, Vijayanagara, Karnataka", "Hampi", 15.3350, 76.4600, IST),
    ("Bandra", "Bandra West, Mumbai, Maharashtra", "Mumbai", 19.0596, 72.8295, IST),
    ("Mumbai Airport T2", "Andheri East, Mumbai, Maharashtra", "Mumbai", 19.0989, 72.8746, IST),
    ("Lonavala", "Lonavala, Pune, Maharashtra", "Lonavala", 18.7546, 73.4062, IST),
    ("Indiranagar", "Indiranagar, Bengaluru, Karnataka", "Bengaluru", 12.9784, 77.6408, IST),
    ("Kempegowda Airport", "Devanahalli, Bengaluru, Karnataka", "Bengaluru", 13.1986, 77.7066, IST),
    ("Nandi Hills", "Nandi Hills, Chikkaballapur, Karnataka", "Nandi Hills", 13.3702, 77.6835, IST),
    ("Dubai Marina", "Dubai Marina, Dubai", "Dubai", 25.0805, 55.1403, GST),
    ("Hatta", "Hatta, Dubai", "Hatta", 24.7969, 56.1137, GST),
]

USERS = [
    ("+919800000001", "Pranav R", Gender.male, "Panjim"),
    ("+919800000002", "Akash K", Gender.male, "Panjim"),
    ("+919800000003", "Meera N", Gender.female, "Margao"),
    ("+919800000004", "Rohan S", Gender.male, "Bandra"),
    ("+919800000005", "Sana K", Gender.female, "Indiranagar"),
    ("+971500000001", "Aditi M", Gender.female, "Dubai Marina"),
]

# host phone, from, to, days ahead, local start, seats, joining, females_only, cost, title, tag
TRIPS = [
    (
        "+919800000001",
        "Panjim",
        "Dudhsagar Falls",
        1,
        time(6, 0),
        2,
        Joining.approval,
        False,
        900,
        "Dudhsagar Falls Day Trip",
        "Day trip",
    ),
    (
        "+919800000003",
        "Margao",
        "Gokarna",
        1,
        time(7, 0),
        1,
        Joining.approval,
        False,
        1800,
        "Gokarna Weekend Road Trip",
        "Road trip",
    ),
    (
        "+919800000003",
        "Calangute",
        "Vagator",
        2,
        time(16, 0),
        2,
        Joining.instant,
        True,
        500,
        "North Goa Beach Hopping",
        "Beach",
    ),
    (
        "+919800000002",
        "Vasco da Gama",
        "Hampi",
        6,
        time(21, 0),
        1,
        Joining.approval,
        False,
        4200,
        "Hampi 3-Day Trip",
        "Long trip",
    ),
    (
        "+919800000001",
        "Panjim",
        "Vagator",
        1,
        time(16, 0),
        2,
        Joining.approval,
        False,
        350,
        "Sunset Beats: ride there",
        "Event",
    ),
    (
        "+919800000002",
        "Vagator",
        "Panjim",
        2,
        time(0, 0),
        1,
        Joining.approval,
        False,
        350,
        "Sunset Beats: ride back",
        "Event",
    ),
    (
        "+919800000004",
        "Bandra",
        "Mumbai Airport T2",
        1,
        time(5, 30),
        3,
        Joining.instant,
        False,
        250,
        "Early flight share",
        "Airport",
    ),
    (
        "+919800000004",
        "Bandra",
        "Lonavala",
        3,
        time(8, 0),
        3,
        Joining.approval,
        False,
        700,
        "Lonavala monsoon drive",
        "Day trip",
    ),
    (
        "+919800000005",
        "Indiranagar",
        "Nandi Hills",
        2,
        time(4, 30),
        2,
        Joining.approval,
        True,
        400,
        "Nandi Hills sunrise",
        "Day trip",
    ),
    (
        "+919800000005",
        "Indiranagar",
        "Kempegowda Airport",
        1,
        time(19, 0),
        3,
        Joining.instant,
        False,
        600,
        "Airport run",
        "Airport",
    ),
    (
        "+971500000001",
        "Dubai Marina",
        "Hatta",
        3,
        time(7, 0),
        3,
        Joining.approval,
        False,
        None,
        "Hatta kayak morning",
        "Day trip",
    ),
]

# name, venue, days ahead, local start
EVENTS = [
    ("Sunset Beats Festival", "Vagator", 1, time(17, 0)),
    ("Electro Dunes Night", "Anjuna", 8, time(20, 0)),
    ("Candolim Live", "Candolim", 9, time(18, 0)),
    ("Bandra Jazz Evening", "Bandra", 4, time(19, 30)),
]


def _at(days: int, local: time, tz: str) -> datetime:
    return datetime.combine(date.today() + timedelta(days=days), local, ZoneInfo(tz))


async def seed(session: AsyncSession) -> bool:
    if await session.scalar(select(func.count()).select_from(Place)):
        return False
    places: dict[str, Place] = {}
    for name, address, city, lat, lng, tz in PLACES:
        places[name] = Place(
            name=name, address=address, city=city, timezone=tz, location=f"POINT({lng} {lat})"
        )
    session.add_all(places.values())
    await session.flush()

    users: dict[str, User] = {}
    for phone, name, gender, home in USERS:
        users[phone] = User(phone=phone, name=name, gender=gender, home_place_id=places[home].id)
    session.add_all(users.values())
    await session.flush()

    for host, frm, to, days, start, seats, joining, females, cost, title, tag in TRIPS:
        tz = places[frm].timezone
        trip = Trip(
            host_id=users[host].id,
            title=title,
            tag=tag,
            from_place_id=places[frm].id,
            to_place_id=places[to].id,
            pickup=frm,
            departs_at=_at(days, start, tz),
            timezone=tz,
            window_minutes=30,
            passenger_seats=seats,
            vehicle="Cab",
            cost_per_person=cost,
            joining=joining,
            females_only=females,
        )
        session.add(trip)
        await session.flush()
        session.add(TripMember(trip_id=trip.id, user_id=users[host].id, role=MemberRole.host))

    for name, venue, days, start in EVENTS:
        session.add(
            Event(
                name=name,
                venue_place_id=places[venue].id,
                starts_at=_at(days, start, places[venue].timezone).astimezone(UTC),
            )
        )
    await session.commit()
    return True


async def main() -> None:
    async with SessionLocal() as session:
        created = await seed(session)
    print("Seeded demo data." if created else "Places already exist; nothing to do.")


if __name__ == "__main__":
    asyncio.run(main())
