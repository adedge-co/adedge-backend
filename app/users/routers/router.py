from fastapi import APIRouter, Depends, HTTPException, status
from app.users.schema.schemas import UserCreate, UserLogin, UserUpdate
from app.base.base_response import BaseResponse
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.services.user_service import UserService

router = APIRouter()


@router.post("/auth/signup/", response_model=BaseResponse[dict])
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await UserService.create_user(user, db)
    return BaseResponse.of_success(status.HTTP_201_CREATED, result)


@router.post("/auth/login/", response_model=BaseResponse[dict])
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await UserService.authenticate_user(user, db)
    return BaseResponse.of_success(status.HTTP_200_OK, result)


@router.put("/user/", response_model=BaseResponse[dict])
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await UserService.update_user(user_id, user, db)
    return BaseResponse.of_success(status.HTTP_200_OK, result)


@router.get("/user/{user_id}", response_model=BaseResponse[dict])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await UserService.get_user_by_id(user_id, db)
    return BaseResponse.of_success(status.HTTP_200_OK, result)
