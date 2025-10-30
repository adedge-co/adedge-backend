from fastapi import APIRouter, Depends, HTTPException, status
from app.users.schema.schemas import (
    UserLogin,
    PersonalSignupRequest,
    CorporateSignupRequest,
)
from app.base.base_response import BaseResponse
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.services.user_service import UserService

router = APIRouter()


@router.post("/auth/signup/personal", response_model=BaseResponse[dict])
async def signup_personal(user: PersonalSignupRequest, db: AsyncSession = Depends(get_db)):
    result = await UserService.create_personal_user(user, db)
    return BaseResponse.of_success(status.HTTP_201_CREATED, result)


@router.post("/auth/signup/corporate", response_model=BaseResponse[dict])
async def signup_corporate(user: CorporateSignupRequest, db: AsyncSession = Depends(get_db)):
    result = await UserService.create_corporate_user(user, db)
    return BaseResponse.of_success(status.HTTP_201_CREATED, result)


@router.post("/auth/login/", response_model=BaseResponse[dict])
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await UserService.authenticate_user(user, db)
    return BaseResponse.of_success(status.HTTP_200_OK, result)


 
