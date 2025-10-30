from typing import Iterable

from fastapi import Request, Header
from fastapi.responses import JSONResponse

from app.users.dependency.dependency import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from app.core.exceptions import UnauthorizedException, ServerException


class JWTAuthMiddleware:
    def __init__(self, app, allow_paths: Iterable[str] | None = None) -> None:
        self.app = app
        self.allow_paths = set(allow_paths or [])

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in self.allow_paths or path.startswith("/docs") or path.startswith("/openapi"):
            await self.app(scope, receive, send)
            return

        headers = dict((k.decode().lower(), v.decode()) for k, v in scope.get("headers", []))
        auth_header = headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            resp = JSONResponse(status_code=401, content={"status": 401, "message": "인증이 필요합니다.", "data": None})
            await resp(scope, receive, send)
            return

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            sub = payload.get("sub")
            if not sub:
                raise JWTError("sub 누락")
            request = Request(scope, receive=receive)
            request.state.user_seq = int(sub)
            await self.app(scope, receive, send)
        except Exception:
            resp = JSONResponse(status_code=401, content={"status": 401, "message": "유효하지 않거나 만료된 토큰입니다.", "data": None})
            await resp(scope, receive, send)
            return


# 통합 유틸/의존성: 토큰 또는 Authorization 헤더에서 user_seq 추출
async def get_user_seq(authorization: str = Header(None), token: str | None = None) -> int:
    try:
        if token is None:
            if not authorization or not authorization.startswith("Bearer "):
                raise UnauthorizedException("Authorization 헤더 누락 또는 형식 오류")
            token = authorization.split(" ", 1)[1].strip()

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise UnauthorizedException("토큰에 사용자 정보가 없습니다(sub).")
        return int(sub)
    except Exception as e:
        raise ServerException(f"토큰 파싱 실패: {e}")
