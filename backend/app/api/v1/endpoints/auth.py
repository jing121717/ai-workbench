from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, svc: AuthService = Depends(get_auth_service)):
    return svc.login(req.username, req.password)


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, svc: AuthService = Depends(get_auth_service)):
    return svc.register(req.username, req.password, req.nickname)


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: int,
    svc: AuthService = Depends(get_auth_service),
):
    return svc.get_user_by_id(user_id)
