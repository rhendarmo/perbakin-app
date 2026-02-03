from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.core.security import hash_password
from app.db.deps import get_db
from app.models.firearms_license import FirearmsLicense
from app.models.member import MemberProfile
from app.models.membership_card import MembershipCard
from app.models.user import User, UserRole
from app.schemas.eligibility import EligibilityResult
from app.schemas.firearms_license import (
    FirearmsLicenseCreate,
    FirearmsLicenseOut,
    FirearmsLicenseUpdate,
)
from app.schemas.member import MemberCreate, MemberOut
from app.schemas.membership_card import (
    MembershipCardCreate,
    MembershipCardOut,
    MembershipCardUpdate,
)
from app.services.eligibility import EligibilityService

router = APIRouter(prefix="/members", tags=["members"])


def _get_my_member_profile(db: Session, user_id: int) -> MemberProfile:
    member = db.query(MemberProfile).filter(MemberProfile.user_id == user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="member_profile_not_found")
    return member


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    """
    Bootstrap signup endpoint (no auth yet).
    Creates:
      - User(role=MEMBER)
      - MemberProfile
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="email_already_registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.MEMBER,
    )
    db.add(user)
    db.flush()  # user.id

    member = MemberProfile(
        user_id=user.id,
        full_name=payload.full_name,
        phone=payload.phone,
        member_number=payload.member_number,
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    return MemberOut(
        id=member.id,
        user_id=member.user_id,
        email=user.email,
        full_name=member.full_name,
        phone=member.phone,
        member_number=member.member_number,
        created_at=member.created_at,
        updated_at=member.updated_at,
        membership_card=member.membership_card,
        firearms_licenses=member.firearms_licenses,
    )


# -----------------------------
# ME endpoints (token-based)
# -----------------------------

@router.get("/me", response_model=MemberOut)
def get_me(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    member = _get_my_member_profile(db, user.id)

    return MemberOut(
        id=member.id,
        user_id=member.user_id,
        email=user.email,
        full_name=member.full_name,
        phone=member.phone,
        member_number=member.member_number,
        created_at=member.created_at,
        updated_at=member.updated_at,
        membership_card=member.membership_card,
        firearms_licenses=member.firearms_licenses,
    )


@router.get("/me/eligibility", response_model=EligibilityResult)
def get_my_eligibility(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    member = _get_my_member_profile(db, user.id)
    return EligibilityService.check_member(db, member.id)


# ---- Membership Card (ME) ----

@router.post("/me/membership-card", response_model=MembershipCardOut, status_code=status.HTTP_201_CREATED)
def upsert_my_membership_card(
    payload: MembershipCardCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = _get_my_member_profile(db, user.id)

    existing = member.membership_card
    if existing:
        existing.card_number = payload.card_number
        existing.issued_at = payload.issued_at
        existing.expires_at = payload.expires_at
        db.commit()
        db.refresh(existing)
        return existing

    card = MembershipCard(member_id=member.id, **payload.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.patch("/me/membership-card", response_model=MembershipCardOut)
def update_my_membership_card(
    payload: MembershipCardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = _get_my_member_profile(db, user.id)
    if not member.membership_card:
        raise HTTPException(status_code=404, detail="membership_card_not_found")

    card = member.membership_card
    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(card, k, v)

    db.commit()
    db.refresh(card)
    return card


# ---- Firearms Licenses (ME) ----

@router.post("/me/firearms-licenses", response_model=FirearmsLicenseOut, status_code=status.HTTP_201_CREATED)
def create_my_firearms_license(
    payload: FirearmsLicenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = _get_my_member_profile(db, user.id)

    lic = FirearmsLicense(member_id=member.id, **payload.model_dump())
    db.add(lic)
    db.commit()
    db.refresh(lic)
    return lic


@router.patch("/me/firearms-licenses/{license_id}", response_model=FirearmsLicenseOut)
def update_my_firearms_license(
    license_id: int,
    payload: FirearmsLicenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = _get_my_member_profile(db, user.id)

    lic = db.get(FirearmsLicense, license_id)
    if not lic or lic.member_id != member.id:
        raise HTTPException(status_code=404, detail="license_not_found")

    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(lic, k, v)

    db.commit()
    db.refresh(lic)
    return lic


@router.delete("/me/firearms-licenses/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_firearms_license(
    license_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = _get_my_member_profile(db, user.id)

    lic = db.get(FirearmsLicense, license_id)
    if not lic or lic.member_id != member.id:
        raise HTTPException(status_code=404, detail="license_not_found")

    db.delete(lic)
    db.commit()
    return None