from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, SessionDep
from app.schemas.place import PlaceOut
from app.services.places import search_places

router = APIRouter(prefix="/places", tags=["places"])


@router.get("/search")
async def search(
    session: SessionDep, _: CurrentUser, q: Annotated[str, Query(max_length=80)] = ""
) -> list[PlaceOut]:
    return await search_places(session, q)
