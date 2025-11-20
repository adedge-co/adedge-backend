from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Column

from app.users.models.user import User
from app.users.schema.schemas import (
    UserLogin,
    PersonalSignupRequest,
    CorporateSignupRequest, UseridDuplicateRequest,
)
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
    async def create_personal_user(request: PersonalSignupRequest, db: AsyncSession) -> None:
        if request.password_confirm != request.password:
            raise BadRequestException("비밀번호가 일치하지 않습니다.")

        result = await db.execute(select(User).where(User.user_id == request.user_id))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ConflictException("이미 등록된 사용자입니다.")

        new_user = User(
            account_type="PERSONAL",
            user_name=request.user_name,
            phone_number=request.phone_number,
            user_id=request.user_id,
            hashed_password=pwd_context.hash(request.password)
        )

        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
        except Exception as e:
            await db.rollback()
            raise ServerException(f"사용자 생성 중 오류가 발생했습니다: {str(e)}")

    @staticmethod
    async def create_corporate_user(request: CorporateSignupRequest, db: AsyncSession) -> None:
        result = await db.execute(select(User).where(User.user_id == request.user_id))
        if result.scalar_one_or_none():
            raise ConflictException("이미 등록된 사용자입니다.")

        new_user = User(
            account_type="CORPORATE",
            business_name=request.business_name,
            business_number=request.business_number,
            phone_number=request.phone_number,
            user_id=request.user_id,
            hashed_password=pwd_context.hash(request.password),
        )

        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
        except Exception as e:
            await db.rollback()
            raise ServerException(f"사용자 생성 중 오류가 발생했습니다: {str(e)}")

    @staticmethod
    async def login_user(request: UserLogin, db: AsyncSession) -> dict:
        result = await db.execute(select(User).where(User.user_id == request.user_id))
        user = result.scalar_one_or_none()

        if not user or not pwd_context.verify(request.password, user.hashed_password):
            raise UnauthorizedException("잘못된 사용자명 또는 비밀번호입니다.")

        access_payload = {
            "sub": str(user.user_seq),
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

        refresh_payload = {
            "sub": str(user.user_seq),
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
    async def user_id_duplicate(request: UseridDuplicateRequest, db: AsyncSession) -> None:
        result = await db.execute(select(User).where(User.user_id == request.user_id))
        user = result.scalar_one_or_none()

        if user:
            raise BadRequestException("이미 사용 중인 아이디입니다.")
