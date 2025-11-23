import hmac
import hashlib
import secrets
import aiohttp
from datetime import datetime, timezone
from typing import Dict, Any
from config import settings
from app.core.exception import ServerException


class SolapiClient:
    BASE_URL = "https://api.solapi.com"

    @staticmethod
    def _generate_salt() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def _generate_signature(date: str, salt: str, api_secret: str) -> str:
        data = date + salt
        signature = hmac.new(
            api_secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    @staticmethod
    def _generate_authorization_header() -> str:
        date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        salt = SolapiClient._generate_salt()
        signature = SolapiClient._generate_signature(date, salt, settings.solapi_api_secret)

        return (
            f"HMAC-SHA256 apiKey={settings.solapi_api_key}, "
            f"date={date}, salt={salt}, signature={signature}"
        )

    @staticmethod
    async def send_sms(to: str, message: str, from_number: str = None) -> Dict[str, Any]:
        url = f"{SolapiClient.BASE_URL}/messages/v4/send"

        # from_number가 없으면 환경 변수에서 가져오기
        if from_number is None:
            from_number = settings.solapi_from_number

        payload = {
            "message": {
                "to": to,
                "from": from_number,
                "text": message
            }
        }

        headers = {
            "Authorization": SolapiClient._generate_authorization_header(),
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    return await response.json()
        except aiohttp.ClientError as e:
            raise ServerException(f"SOLAPI API 호출 중 네트워크 오류가 발생했습니다: {str(e)}")
        except Exception as e:
            raise ServerException(f"SOLAPI 문자 발송 중 오류가 발생했습니다: {str(e)}")
