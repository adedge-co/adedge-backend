from pydantic import BaseModel, Field


class SendVerificationCodeRequest(BaseModel):
    phone_number: str = Field(..., description="인증번호를 받을 전화번호", example="01012345678")


class VerifyCodeRequest(BaseModel):
    phone_number: str = Field(..., description="인증번호를 받은 전화번호", example="01012345678")
    verification_code: str = Field(..., description="인증번호", example="123456", min_length=6, max_length=6)
