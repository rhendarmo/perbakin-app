from sqlalchemy.orm import Session

from app.core.security import verify_password, hash_password
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.models.user import User, UserRole


class AuthService:
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User | None:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def issue_tokens(user: User) -> tuple[str, str]:
        access = create_access_token(subject=str(user.id), role=user.role.value)
        refresh = create_refresh_token(subject=str(user.id), role=user.role.value)
        return access, refresh

    @staticmethod
    def create_user(db: Session, email: str, password: str, role: UserRole = UserRole.MEMBER) -> User:
        user = User(email=email, hashed_password=hash_password(password), role=role)
        db.add(user)
        db.flush()
        return user

    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("invalid_token_type")
        user_id = payload.get("sub")
        role = payload.get("role")
        return create_access_token(subject=str(user_id), role=str(role))