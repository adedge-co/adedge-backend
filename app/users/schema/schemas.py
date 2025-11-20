from pydantic import BaseModel
from typing import Optional


class UserLogin(BaseModel):
    user_id: str
    password: str


class PersonalSignupRequest(BaseModel):
    user_name: str
    phone_number: str
    user_id: str
    password: str
    password_confirm: str


class CorporateSignupRequest(BaseModel):
    business_name: str
    business_number: str
    phone_number: str
    user_id: str
    password: str
    password_confirm: str


class UseridDuplicateRequest(BaseModel):
    user_id: str
