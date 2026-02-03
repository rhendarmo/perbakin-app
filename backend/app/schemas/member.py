from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema
from app.schemas.membership_card import MembershipCardOut
from app.schemas.firearms_license import FirearmsLicenseOut


class MemberBase(BaseModel):
    full_name: str = Field(..., max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    member_number: str | None = Field(default=None, max_length=100)


class MemberCreate(MemberBase):
    # for now, we’ll create members without auth
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

class MemberOut(MemberBase, TimestampedSchema):
    id: int
    user_id: int
    email: str
    membership_card: MembershipCardOut | None = None
    firearms_licenses: list[FirearmsLicenseOut] = []

    class Config:
        from_attributes = True
