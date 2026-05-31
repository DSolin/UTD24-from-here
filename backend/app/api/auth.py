import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    display_name: str | None = None


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    r = db.execute(select(User).where(User.username == req.username))
    if r.scalar_one_or_none():
        raise HTTPException(400, "Username already taken")
    r = db.execute(select(User).where(User.email == req.email))
    if r.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    
    user = User(
        id=uuid.uuid4(),
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
        display_name=req.display_name or req.username,
    )
    db.add(user)
    db.commit()
    
    token = create_access_token(user.id)
    return {
        "access_token": token, "token_type": "bearer",
        "user": {"id": str(user.id), "username": user.username, "email": user.email, "display_name": user.display_name}
    }


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    r = db.execute(select(User).where((User.username == req.username_or_email) | (User.email == req.username_or_email)))
    user = r.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    token = create_access_token(user.id)
    return {
        "access_token": token, "token_type": "bearer",
        "user": {"id": str(user.id), "username": user.username, "email": user.email, "display_name": user.display_name}
    }


async def get_current_user(authorization: str = Header(None), db: AsyncSession = Depends(get_db)):
    """从 JWT 解析当前用户"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return None
    r = db.execute(select(User).where(User.id == uid))
    return r.scalar_one_or_none()
