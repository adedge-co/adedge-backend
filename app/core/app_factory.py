from fastapi import FastAPI, status
from config import settings
from app.core.middleware import setup_exception_handlers
from app.users.routers.router import router
from app.core.auto_migration import auto_update_schema
from app.base.base_response import BaseResponse
from app.core.security import JWTAuthMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="AdEdge Backend API",
        description=f"AdEdge Backend API - {settings.active_profile.upper()} Environment",
        debug=settings.debug,
        version="1.0.0",
    )

    setup_exception_handlers(app)

    app.add_middleware(
        JWTAuthMiddleware,
        allow_paths=(
            "/auth/login/",
            "/auth/signup/personal",
            "/auth/signup/corporate",
            "/actuator/health",
            "/docs"
        ),
    )

    app.include_router(router)

    @app.get("/actuator/health", response_model=BaseResponse[dict], status_code=status.HTTP_200_OK)
    async def health_check():
        health_data = {"status": "healthy", "environment": settings.active_profile}
        return BaseResponse.of_success(status.HTTP_200_OK, health_data)

    @app.on_event("startup")
    async def startup_event():
        print("🔄 자동 스키마 업데이트 시작...")
        await auto_update_schema()

        if settings.debug:
            print(f"🚀 AdEdge Backend 시작됨 - 환경: {settings.active_profile}")
            print(f"📊 데이터베이스: {settings.database_url}")
            print(f"🐛 디버그 모드: {settings.debug}")
            print(f"📝 로그 레벨: {settings.log_level}")
        else:
            print(f"AdEdge Backend started - Environment: {settings.active_profile}")

    return app
