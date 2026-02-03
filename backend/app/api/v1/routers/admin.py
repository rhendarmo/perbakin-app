from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps.auth import require_admin
from app.db.deps import get_db
from app.models.member import MemberProfile
from app.models.user import User
from app.services.eligibility import EligibilityService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/members/search")
def search_members(q: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """
    Admin-only member search across:
      - member full_name
      - member_number
      - user email
    Returns basic member fields + eligibility summary.
    """
    results = (
        db.query(MemberProfile)
        .join(User, User.id == MemberProfile.user_id)
        .filter(
            or_(
                MemberProfile.full_name.ilike(f"%{q}%"),
                MemberProfile.member_number.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
            )
        )
        .limit(50)
        .all()
    )

    payload = []
    for m in results:
        user = db.get(User, m.user_id)
        elig = EligibilityService.check_member(db, m.id)
        payload.append(
            {
                "member_id": m.id,
                "user_id": m.user_id,
                "email": user.email if user else None,
                "full_name": m.full_name,
                "member_number": m.member_number,
                "eligibility": elig.model_dump(),
            }
        )

    return {"count": len(payload), "results": payload}


@router.get("/members/{member_id}/eligibility")
def admin_member_eligibility(member_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """
    Admin-only eligibility check by member_id.
    """
    return EligibilityService.check_member(db, member_id)


@router.get("/members/{member_id}")
def admin_get_member(member_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """
    Admin-only member detail endpoint (useful for admin profile view page).
    """
    member = db.get(MemberProfile, member_id)
    if not member:
        return {"detail": "member_not_found"}

    user = db.get(User, member.user_id)

    return {
        "member_id": member.id,
        "user_id": member.user_id,
        "email": user.email if user else None,
        "full_name": member.full_name,
        "phone": member.phone,
        "member_number": member.member_number,
        "membership_card": member.membership_card,
        "firearms_licenses": member.firearms_licenses,
    }