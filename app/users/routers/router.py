from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_user_seq
from app.users.schema.schemas import (
    UserLogin, PersonalSignupRequest,
    CorporateSignupRequest, UseridDuplicateRequest,
)
from app.base.base_response import BaseResponse
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.services.user_service import UserService

router = APIRouter()


@router.post("/auth/signup/personal", response_model=BaseResponse[dict])
async def signup_personal(request: PersonalSignupRequest, db: AsyncSession = Depends(get_db)):
    await UserService.create_personal_user(request, db)
    return BaseResponse.of_success(status.HTTP_201_CREATED, "SUCCESS")


@router.post("/auth/signup/corporate", response_model=BaseResponse[dict])
async def signup_corporate(request: CorporateSignupRequest, db: AsyncSession = Depends(get_db)):
    await UserService.create_corporate_user(request, db)
    return BaseResponse.of_success(status.HTTP_201_CREATED, "SUCCESS")


@router.post("/auth/login", response_model=BaseResponse[dict])
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await UserService.login_user(request, db)
    return BaseResponse.of_success(status.HTTP_200_OK, result)


@router.post("/auth/user_id/duplicate", response_model=BaseResponse[dict])
async def user_id_duplicate(request: UseridDuplicateRequest, db: AsyncSession = Depends(get_db)):
    await UserService.user_id_duplicate(request, db)
    return BaseResponse.of_success(status.HTTP_200_OK, "SUCCESS")
