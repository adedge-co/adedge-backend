from database import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    hashed_password = Column(String(512), nullable=False)
