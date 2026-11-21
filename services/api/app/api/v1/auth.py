from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import OtpDep, SessionDep, is_prod
from app.core.errors import UnauthorizedError
from app.core.security import create_token, decode_token
from app.models import User
from app.schemas.auth import OtpRequest, OtpRequested, OtpVerify, RefreshIn, Tokens
from app.services.otp import new_code

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/request", status_code=status.HTTP_202_ACCEPTED)
async def request_otp(body: OtpRequest, otp: OtpDep) -> OtpRequested:
    code = new_code()
    await otp.put(body.phone, code)
    # SMS delivery is not wired yet (spec 13.1). Outside prod the code is echoed back.
    return OtpRequested(dev_code=None if is_prod() else code)


@router.post("/otp/verify")
async def verify_otp(body: OtpVerify, otp: OtpDep, session: SessionDep) -> Tokens:
    if not await otp.pop_if_match(body.phone, body.code):
        raise UnauthorizedError("Code is wrong or expired.")
    user = await session.scalar(select(User).where(User.phone == body.phone))
    if user is None:
        user = User(phone=body.phone)
        session.add(user)
        await session.commit()
    return Tokens(
        access_token=create_token(user.id, "access"),
        refresh_token=create_token(user.id, "refresh"),
    )


@router.post("/refresh")
async def refresh(body: RefreshIn) -> Tokens:
    user_id = decode_token(body.refresh_token, "refresh")
    return Tokens(access_token=create_token(user_id, "access"))
