from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from app.core.database import AsyncSessionLocal

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 14
SECRET_KEY = "change-this-to-a-long-random-secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()
