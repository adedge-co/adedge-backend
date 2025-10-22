from fastapi import APIRouter, Depends, HTTPException
from app.users.model.model import User
from app.users.schema.schemas import UserCreate, UserLogin, UserUpdate
from database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from app.users.dependency.dependency import pwd_context, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter()

@router.post("/auth/signup/")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user is not None:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

@router.post("/auth/login/")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user is None or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_payload = {
        "sub": db_user.username,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

    refresh_payload = {
        "sub": db_user.username,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.put("/user/")
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    if user.username is not None:
        db_user.username = user.username
    if user.email is not None:
        db_user.email = user.email

    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}