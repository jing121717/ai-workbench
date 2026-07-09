from datetime import timedelta
from sqlalchemy.orm import Session
from backend.app.repositories.user_repository import UserRepository
from backend.app.core.security import create_access_token, hash_password
from backend.app.core.config import settings
from backend.app.core.exceptions import AuthenticationError, NotFoundError


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def login(self, username: str, password: str) -> dict:
        user = self.repo.authenticate(username, password)
        if not user:
            raise AuthenticationError("用户名或密码错误")
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
        }

    def register(self, username: str, password: str, nickname: str = "") -> dict:
        existing = self.repo.get_by_username(username)
        if existing:
            raise AuthenticationError("用户名已存在")
        user = self.repo.create(username=username, password=password, nickname=nickname)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
        }

    def get_user_by_id(self, user_id: int) -> dict:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("用户不存在")
        return {"id": user.id, "username": user.username, "nickname": user.nickname, "is_superuser": user.is_superuser}
