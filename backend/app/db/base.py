from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models so Base.metadata is fully populated for Alembic autogenerate
from app.models import (  # noqa: E402,F401
    User,
    UserRole,
    MemberProfile,
    MembershipCard,
    FirearmsLicense,
)