from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    get_access_token_expire_minutes,
    verify_password,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise UnauthorizedError("Invalid credentials")

    access_token = create_access_token(subject=str(user.id), role=user.role)
    expires_in_seconds = get_access_token_expire_minutes() * 60

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_seconds=expires_in_seconds,
    )
