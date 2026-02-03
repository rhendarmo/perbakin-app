from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.deps import get_db
from app.models.member import MemberProfile
from app.models.user import User
from app.services.eligibility import EligibilityService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/members/search")
def search_members(q: str, db: Session = Depends(get_db)):
    """
    Simple search across member full name, member number, and user email.
    Returns members + eligibility summary.
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
def admin_member_eligibility(member_id: int, db: Session = Depends(get_db)):
    return EligibilityService.check_member(db, member_id)
