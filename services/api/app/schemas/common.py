import uuid

from pydantic import BaseModel, ConfigDict


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserSummary(Schema):
    id: uuid.UUID
    name: str
