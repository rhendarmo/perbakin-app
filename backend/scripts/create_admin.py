from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.auth import AuthService
from app.models.user import UserRole
from app.models.member import MemberProfile

EMAIL = "admin@perbakin.local"
PASSWORD = "AdminPassword123!"


def main():
    db: Session = SessionLocal()
    try:
        user = AuthService.create_user(db, EMAIL, PASSWORD, role=UserRole.ADMIN)
        # Admin doesn’t need a member profile, but harmless to omit.
        db.commit()
        print("Created admin:", EMAIL)
    finally:
        db.close()


if __name__ == "__main__":
    main()
