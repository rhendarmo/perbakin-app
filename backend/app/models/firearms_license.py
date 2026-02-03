from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FirearmsLicense(Base):
    __tablename__ = "firearms_licenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    member_id: Mapped[int] = mapped_column(
        ForeignKey("member_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    license_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    license_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    issued_at: Mapped[date] = mapped_column(Date, nullable=False)
    expires_at: Mapped[date] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    member: Mapped["MemberProfile"] = relationship(back_populates="firearms_licenses")
