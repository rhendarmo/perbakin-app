from datetime import date
from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema


class FirearmsLicenseBase(BaseModel):
    license_number: str = Field(..., max_length=100)
    license_type: str | None = Field(default=None, max_length=50)
    issued_at: date
    expires_at: date


class FirearmsLicenseCreate(FirearmsLicenseBase):
    pass


class FirearmsLicenseUpdate(BaseModel):
    license_number: str | None = Field(default=None, max_length=100)
    license_type: str | None = Field(default=None, max_length=50)
    issued_at: date | None = None
    expires_at: date | None = None


class FirearmsLicenseOut(FirearmsLicenseBase, TimestampedSchema):
    id: int
    member_id: int

    class Config:
        from_attributes = True