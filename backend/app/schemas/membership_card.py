from datetime import date
from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema


class MembershipCardBase(BaseModel):
    card_number: str = Field(..., max_length=100)
    issued_at: date
    expires_at: date


class MembershipCardCreate(MembershipCardBase):
    pass


class MembershipCardUpdate(BaseModel):
    card_number: str | None = Field(default=None, max_length=100)
    issued_at: date | None = None
    expires_at: date | None = None


class MembershipCardOut(MembershipCardBase, TimestampedSchema):
    id: int
    member_id: int

    class Config:
        from_attributes = True