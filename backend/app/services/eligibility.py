from datetime import date
from sqlalchemy.orm import Session

from app.models.member import MemberProfile
from app.models.membership_card import MembershipCard
from app.models.firearms_license import FirearmsLicense
from app.schemas.eligibility import EligibilityResult


class EligibilityService:
    """
    Rule A:
    Eligible if membership card is valid AND at least one firearms license is valid.
    """

    @staticmethod
    def check_member(db: Session, member_id: int, today: date | None = None) -> EligibilityResult:
        if today is None:
            today = date.today()

        member = db.get(MemberProfile, member_id)
        if not member:
            return EligibilityResult(
                eligible=False,
                reasons=["member_not_found"],
                checked_at=today,
                membership_valid=False,
                has_valid_license=False,
            )

        # Membership validity
        membership: MembershipCard | None = member.membership_card
        membership_valid = bool(membership and membership.expires_at >= today)

        # At least one valid license
        licenses: list[FirearmsLicense] = member.firearms_licenses or []
        has_valid_license = any(lic.expires_at >= today for lic in licenses)

        reasons: list[str] = []
        if not membership:
            reasons.append("membership_missing")
        elif membership.expires_at < today:
            reasons.append("membership_expired")

        if not licenses:
            reasons.append("no_firearms_license")
        elif not has_valid_license:
            reasons.append("no_valid_firearms_license")

        eligible = membership_valid and has_valid_license

        return EligibilityResult(
            eligible=eligible,
            reasons=reasons,
            checked_at=today,
            membership_valid=membership_valid,
            has_valid_license=has_valid_license,
        )