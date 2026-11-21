"""Small helpers to insert rows directly in tests."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Place

# name, address, city, lat, lng
GOA = [
    ("Panjim", "Panjim, North Goa, Goa", "Goa", 15.4909, 73.8278),
    ("Margao", "Margao, South Goa, Goa", "Goa", 15.2832, 73.9862),
    ("Vagator", "Vagator, North Goa, Goa", "Goa", 15.6020, 73.7440),
    ("Anjuna", "Anjuna, North Goa, Goa", "Goa", 15.5733, 73.7407),
    ("Calangute", "Calangute, North Goa, Goa", "Goa", 15.5440, 73.7553),
    ("Candolim", "Candolim, North Goa, Goa", "Goa", 15.5180, 73.7620),
    ("Gokarna", "Gokarna, Uttara Kannada, Karnataka", "Gokarna", 14.5479, 74.3188),
    ("Dudhsagar Falls", "Sonaulim, Sanguem, Goa border", "Goa", 15.3144, 74.3143),
    ("Vasco da Gama", "Vasco da Gama, South Goa, Goa", "Goa", 15.3860, 73.8440),
]


async def add_place(
    session: AsyncSession, name: str, address: str, city: str, lat: float, lng: float
) -> Place:
    place = Place(name=name, address=address, city=city, location=f"POINT({lng} {lat})")
    session.add(place)
    await session.flush()
    return place


async def add_places(session: AsyncSession) -> dict[str, Place]:
    places = {row[0]: await add_place(session, *row) for row in GOA}
    await session.commit()
    return places
