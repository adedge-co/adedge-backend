from pydantic import BaseModel
from typing import Optional


class UserLogin(BaseModel):
    user_id: str
    password: str


class PersonalSignupRequest(BaseModel):
    user_id: str
    password: str
    user_name: str
    resident_number: str
    address: Optional[str] = None
    phone_number: Optional[str] = None


class CorporateSignupRequest(BaseModel):
    user_id: str
    password: str
    business_name: str
    business_number: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
