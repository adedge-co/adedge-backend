from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.users.models.user import User
from app.users.schema.schemas import (
    UserLogin,
    PersonalSignupRequest,
    CorporateSignupRequest,
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
    async def create_personal_user(user_data: PersonalSignupRequest, db: AsyncSession) -> dict:
        # user_id 중복 체크
        result = await db.execute(select(User).where(User.user_id == user_data.user_id))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ConflictException("이미 등록된 사용자입니다.")

        # 주민번호 중복 체크(선택: 필수로 받으므로 고유 보장)
        result = await db.execute(select(User).where(User.resident_number == user_data.resident_number))
        if result.scalar_one_or_none():
            raise ConflictException("이미 등록된 주민번호입니다.")

        hashed_password = pwd_context.hash(user_data.password)

        new_user = User(
            account_type="PERSONAL",
            user_id=user_data.user_id,
            hashed_password=hashed_password,
            user_name=user_data.user_name,
            resident_number=user_data.resident_number,
            address=user_data.address,
            phone_number=user_data.phone_number,
        )

        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
        except Exception as e:
            await db.rollback()
            raise ServerException(f"사용자 생성 중 오류가 발생했습니다: {str(e)}")

        return {
            "user_seq": new_user.user_seq,
            "user_id": new_user.user_id,
            "account_type": new_user.account_type
        }

    @staticmethod
    async def create_corporate_user(user_data: CorporateSignupRequest, db: AsyncSession) -> dict:
        # user_id 중복 체크
        result = await db.execute(select(User).where(User.user_id == user_data.user_id))
        if result.scalar_one_or_none():
            raise ConflictException("이미 등록된 사용자입니다.")

        # 사업자번호 중복 체크
        result = await db.execute(select(User).where(User.business_number == user_data.business_number))
        if result.scalar_one_or_none():
            raise ConflictException("이미 등록된 사업자번호입니다.")

        hashed_password = pwd_context.hash(user_data.password)

        new_user = User(
            account_type="CORPORATE",
            user_id=user_data.user_id,
            hashed_password=hashed_password,
            business_name=user_data.business_name,
            business_number=user_data.business_number,
            address=user_data.address,
            phone_number=user_data.phone_number,
        )

        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
        except Exception as e:
            await db.rollback()
            raise ServerException(f"사용자 생성 중 오류가 발생했습니다: {str(e)}")

        return {
            "user_seq": new_user.user_seq,
            "user_id": new_user.user_id,
            "account_type": new_user.account_type
        }

    @staticmethod
    async def authenticate_user(login_data: UserLogin, db: AsyncSession) -> dict:
        result = await db.execute(select(User).where(User.user_id == login_data.user_id))
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
