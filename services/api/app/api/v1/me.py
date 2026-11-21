from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUser, SessionDep
from app.core.errors import NotFoundError
from app.models import Place
from app.schemas.alert import AlertOut
from app.schemas.user import Me, MeUpdate
from app.services import notifications

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


@router.get("/alerts")
async def my_alerts(user: CurrentUser, session: SessionDep) -> list[AlertOut]:
    return await notifications.list_alerts(session, user)


@router.post("/alerts/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_alerts_read(user: CurrentUser, session: SessionDep) -> Response:
    await notifications.mark_all_read(session, user)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
