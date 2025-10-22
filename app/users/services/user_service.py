from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.users.models.user import User
from app.users.schema.schemas import UserCreate, UserLogin, UserUpdate
from app.users.dependency.dependency import pwd_context
from datetime import datetime, timedelta
from jose import jwt
from app.users.dependency.dependency import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    ServerException,
    UnauthorizedException
)


class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate, db: AsyncSession) -> dict:
        result = await db.execute(select(User).where(User.username == user_data.username))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ConflictException("이미 등록된 사용자입니다.")

        hashed_password = pwd_context.hash(user_data.password)

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )

        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
        except Exception as e:
            await db.rollback()
            raise ServerException(f"사용자 생성 중 오류가 발생했습니다: {str(e)}")

        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }

    @staticmethod
    async def authenticate_user(login_data: UserLogin, db: AsyncSession) -> dict:
        result = await db.execute(select(User).where(User.username == login_data.username))
        user = result.scalar_one_or_none()

        if not user or not pwd_context.verify(login_data.password, user.hashed_password):
            raise UnauthorizedException("잘못된 사용자명 또는 비밀번호입니다.")

        access_payload = {
            "sub": user.username,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

        refresh_payload = {
            "sub": user.username,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        }
        refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def update_user(user_id: int, update_data: UserUpdate, db: AsyncSession) -> dict:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("사용자를 찾을 수 없습니다.")

        if update_data.username is not None:
            user.username = update_data.username
        if update_data.email is not None:
            user.email = update_data.email

        try:
            await db.commit()
            await db.refresh(user)
        except Exception as e:
            await db.rollback()
            raise ServerException(f"사용자 정보 수정 중 오류가 발생했습니다: {str(e)}")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }

    @staticmethod
    async def get_user_by_id(user_id: int, db: AsyncSession) -> dict:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("사용자를 찾을 수 없습니다.")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
