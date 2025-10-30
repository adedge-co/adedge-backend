from sqlalchemy import Column, Integer, String

from app.base.base_time_entity import BaseTimeEntity


class User(BaseTimeEntity):
    __tablename__ = 'users'
    # PK
    user_seq = Column(Integer, primary_key=True, index=True)

    # 구분: PERSONAL / CORPORATE (필수)
    account_type = Column(String(20), nullable=False)

    # 개인 전용 필드 (선택)
    user_name = Column(String(50), nullable=True)
    resident_number = Column(String(50), unique=True, nullable=True)

    # 법인 전용 필드 (선택)
    business_name = Column(String(100), nullable=True)
    business_number = Column(String(50), unique=True, nullable=True)

    # 공통(선택)
    address = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)

    # 로그인 계정 (필수)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(512), nullable=False)
