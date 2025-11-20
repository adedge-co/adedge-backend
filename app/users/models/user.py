from sqlalchemy import Column, Integer, String

from app.base.base_time_entity import BaseTimeEntity


class User(BaseTimeEntity):
    __tablename__ = 'users'
    # PK
    user_seq = Column(Integer, primary_key=True, index=True)

    # 구분: PERSONAL / CORPORATE (필수)
    account_type = Column(String(20), nullable=False)

    business_name = Column(String(100), nullable=True)
    business_number = Column(String(50), unique=True, nullable=True)

    user_name = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(512), nullable=False)
