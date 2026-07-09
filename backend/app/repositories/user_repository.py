from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.core.security import hash_password, verify_password


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, username: str, password: str, nickname: str = "") -> User:
        user = User(
            username=username,
            hashed_password=hash_password(password),
            nickname=nickname or username,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> User | None:
        user = self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
