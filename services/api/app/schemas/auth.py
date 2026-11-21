from typing import Annotated

from pydantic import Field

from app.schemas.common import Schema

Phone = Annotated[str, Field(pattern=r"^\+[1-9]\d{7,14}$", examples=["+919800000001"])]


class OtpRequest(Schema):
    phone: Phone


class OtpRequested(Schema):
    sent: bool = True
    dev_code: str | None = Field(None, description="Only returned outside production.")


class OtpVerify(Schema):
    phone: Phone
    code: Annotated[str, Field(pattern=r"^\d{6}$")]


class RefreshIn(Schema):
    refresh_token: str


class Tokens(Schema):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
