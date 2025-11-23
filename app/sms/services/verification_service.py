import secrets
from typing import Optional
from app.core.redis_config import RedisClient
from app.core.exception import BadRequestException, UnauthorizedException, ServerException
from app.sms.services.solapi_client import SolapiClient


def generate_verification_code() -> str:
    return f"{secrets.randbelow(1000000):06d}"


async def send_verification_code(phone_number: str) -> None:
    # 인증번호 생성
    verification_code = generate_verification_code()

    # Redis에 저장 (5분 TTL)
    try:
        redis_client = await RedisClient.get_client()
        redis_key = f"sms:verification:{phone_number}"
        ttl_seconds = 180  # 5분
        await redis_client.setex(redis_key, ttl_seconds, verification_code)
    except Exception as e:
        raise ServerException(f"인증번호를 Redis에 저장하는 중 오류가 발생했습니다: {str(e)}")

    # SMS 발송
    message = f"[AdEdge] 인증번호는 {verification_code}입니다. 3분 내에 입력해주세요."
    try:
        await SolapiClient.send_sms(to=phone_number, message=message)
    except Exception as e:
        # SMS 발송 실패 시 Redis에서도 삭제
        try:
            redis_client = await RedisClient.get_client()
            redis_key = f"sms:verification:{phone_number}"
            await redis_client.delete(redis_key)
        except Exception:
            pass
        raise ServerException(f"인증번호 SMS 발송 중 오류가 발생했습니다: {str(e)}")


async def verify_code(phone_number: str, verification_code: str) -> bool:
    if not phone_number or not verification_code:
        raise BadRequestException("전화번호와 인증번호를 모두 입력해주세요.")

    if len(verification_code) != 6:
        raise BadRequestException("인증번호는 6자리입니다.")

    try:
        redis_client = await RedisClient.get_client()
        redis_key = f"sms:verification:{phone_number}"
        stored_code = await redis_client.get(redis_key)

        if stored_code is None:
            raise UnauthorizedException("인증번호가 만료되었거나 존재하지 않습니다. 다시 발송해주세요.")

        if stored_code != verification_code:
            raise UnauthorizedException("인증번호가 일치하지 않습니다. 다시 확인해주세요.")

        # 검증 성공 시 Redis에서 삭제 (1회용)
        await redis_client.delete(redis_key)
        return True

    except UnauthorizedException:
        raise
    except Exception as e:
        raise ServerException(f"인증번호 검증 중 오류가 발생했습니다: {str(e)}")
