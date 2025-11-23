from fastapi import APIRouter, status
from app.sms.schema.schemas import SendVerificationCodeRequest, VerifyCodeRequest
from app.sms.services.verification_service import send_verification_code, verify_code
from app.base.base_response import BaseResponse

router = APIRouter(prefix="/sms", tags=["SMS"])


@router.post("/send", response_model=BaseResponse[dict])
async def send_verification_code_endpoint(request: SendVerificationCodeRequest):
    """
    인증번호 발송
    
    전화번호를 받아서 6자리 인증번호를 생성하고 SMS로 발송합니다.
    인증번호는 5분간 유효합니다.
    """
    await send_verification_code(request.phone_number)
    return BaseResponse.of_success(status.HTTP_200_OK, {"message": "인증번호가 발송되었습니다."})


@router.post("/verify", response_model=BaseResponse[dict])
async def verify_code_endpoint(request: VerifyCodeRequest):
    """
    인증번호 검증
    
    전화번호와 인증번호를 받아서 검증합니다.
    검증 성공 시 인증번호는 삭제되어 재사용할 수 없습니다.
    """
    await verify_code(request.phone_number, request.verification_code)
    return BaseResponse.of_success(status.HTTP_200_OK, {"message": "인증번호가 확인되었습니다."})
