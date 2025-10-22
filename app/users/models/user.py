from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text

from app.base.base_time_entity import BaseTimeEntity


class User(BaseTimeEntity):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), nullable=True)
    hashed_password = Column(String(512), nullable=False)
    full_name = Column(String(100), nullable=True)
    # 예시: 추가 가능 필드들 (자동 마이그레이션으로 반영)
    # phone_number = Column(String(20), nullable=True)
    # bio = Column(Text, nullable=True)
    # last_login = Column(DateTime, nullable=True)

