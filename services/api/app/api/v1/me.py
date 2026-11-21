from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.core.errors import NotFoundError
from app.models import Place
from app.schemas.user import Me, MeUpdate

router = APIRouter(prefix="/me", tags=["me"])


@router.get("")
async def get_me(user: CurrentUser) -> Me:
    return Me.model_validate(user)


@router.patch("")
async def update_me(body: MeUpdate, user: CurrentUser, session: SessionDep) -> Me:
    changes = body.model_dump(exclude_unset=True)
    if changes.get("home_place_id") and not await session.get(Place, changes["home_place_id"]):
        raise NotFoundError("Home place not found.")
    for field, value in changes.items():
        setattr(user, field, value)
    await session.commit()
    return Me.model_validate(user)
