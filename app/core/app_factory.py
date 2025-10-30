"""
애플리케이션 팩토리
"""
from fastapi import FastAPI
from config import settings
from app.core.middleware import setup_exception_handlers
from app.users.routers.router import router
from app.core.auto_migration import auto_update_schema
from app.users.models.user import User  # 모델 등록을 위해 임포트


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성"""
    
    app = FastAPI(
        title="AdEdge Backend API",
        description=f"AdEdge Backend API - {settings.active_profile.upper()} Environment",
        debug=settings.debug,
        version="1.0.0",
    )
    
    # 예외 핸들러 설정
    setup_exception_handlers(app)
    
    # 라우터 등록
    app.include_router(router)
    
    # 헬스 체크 엔드포인트
    from fastapi import status
    from app.base.base_response import BaseResponse
    
    @app.get("/actuator/health", response_model=BaseResponse[dict], status_code=status.HTTP_200_OK)
    async def health_check():
        health_data = {"status": "healthy", "environment": settings.active_profile}
        return BaseResponse.of_success(status.HTTP_200_OK, health_data)
    
    # 시작 이벤트
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
