from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.user import User, UserRole
from app.models.member import MemberProfile
from app.models.membership_card import MembershipCard
from app.models.firearms_license import FirearmsLicense
from app.schemas.member import MemberCreate, MemberOut
from app.schemas.membership_card import MembershipCardCreate, MembershipCardUpdate, MembershipCardOut
from app.schemas.firearms_license import FirearmsLicenseCreate, FirearmsLicenseUpdate, FirearmsLicenseOut
from app.services.eligibility import EligibilityService
from app.schemas.eligibility import EligibilityResult
from app.core.security import hash_password  # we’ll add this file in Step 4

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    # NOTE: this is a “bootstrap” endpoint for now; later we’ll do auth-based signup.
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="email_already_registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=UserRole.MEMBER)
    db.add(user)
    db.flush()  # get user.id

    member = MemberProfile(user_id=user.id, full_name=payload.full_name, phone=payload.phone, member_number=payload.member_number)
    db.add(member)
    db.commit()
    db.refresh(member)

    # attach email for response convenience
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


@router.get("/{member_id}", response_model=MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.get(MemberProfile, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="member_not_found")

    user = db.get(User, member.user_id)
    return MemberOut(
        id=member.id,
        user_id=member.user_id,
        email=user.email if user else "",
        full_name=member.full_name,
        phone=member.phone,
        member_number=member.member_number,
        created_at=member.created_at,
        updated_at=member.updated_at,
        membership_card=member.membership_card,
        firearms_licenses=member.firearms_licenses,
    )


@router.get("/{member_id}/eligibility", response_model=EligibilityResult)
def get_member_eligibility(member_id: int, db: Session = Depends(get_db)):
    return EligibilityService.check_member(db, member_id)


# ---- Membership Card ----

@router.post("/{member_id}/membership-card", response_model=MembershipCardOut, status_code=status.HTTP_201_CREATED)
def upsert_membership_card(member_id: int, payload: MembershipCardCreate, db: Session = Depends(get_db)):
    member = db.get(MemberProfile, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="member_not_found")

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


@router.patch("/{member_id}/membership-card", response_model=MembershipCardOut)
def update_membership_card(member_id: int, payload: MembershipCardUpdate, db: Session = Depends(get_db)):
    member = db.get(MemberProfile, member_id)
    if not member or not member.membership_card:
        raise HTTPException(status_code=404, detail="membership_card_not_found")

    card = member.membership_card
    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(card, k, v)

    db.commit()
    db.refresh(card)
    return card


# ---- Firearms Licenses ----

@router.post("/{member_id}/firearms-licenses", response_model=FirearmsLicenseOut, status_code=status.HTTP_201_CREATED)
def create_firearms_license(member_id: int, payload: FirearmsLicenseCreate, db: Session = Depends(get_db)):
    member = db.get(MemberProfile, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="member_not_found")

    lic = FirearmsLicense(member_id=member.id, **payload.model_dump())
    db.add(lic)
    db.commit()
    db.refresh(lic)
    return lic


@router.patch("/{member_id}/firearms-licenses/{license_id}", response_model=FirearmsLicenseOut)
def update_firearms_license(member_id: int, license_id: int, payload: FirearmsLicenseUpdate, db: Session = Depends(get_db)):
    member = db.get(MemberProfile, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="member_not_found")

    lic = db.get(FirearmsLicense, license_id)
    if not lic or lic.member_id != member.id:
        raise HTTPException(status_code=404, detail="license_not_found")

    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(lic, k, v)

    db.commit()
    db.refresh(lic)
    return lic


@router.delete("/{member_id}/firearms-licenses/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_firearms_license(member_id: int, license_id: int, db: Session = Depends(get_db)):
    member = db.get(MemberProfile, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="member_not_found")

    lic = db.get(FirearmsLicense, license_id)
    if not lic or lic.member_id != member.id:
        raise HTTPException(status_code=404, detail="license_not_found")

    db.delete(lic)
    db.commit()
    return None