from fastapi import FastAPI, status

from database import engine, Base
from app.users.routers.router import router
from config import settings

# 환경별 설정에 따라 FastAPI 앱을 생성합니다
app = FastAPI(
    title="AdEdge Backend API",
    description=f"AdEdge Backend API - {settings.active_profile.upper()} Environment",
    debug=settings.debug,
    version="1.0.0"
)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(router)

# 헬스체크 엔드포인트
@app.get("/actuator/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy", "environment": settings.active_profile}

# 시작 시 현재 환경 정보를 출력 (프로덕션에서는 로그만)
@app.on_event("startup")
async def startup_event():
    if settings.debug:
        print(f"🚀 AdEdge Backend 시작됨 - 환경: {settings.active_profile}")
        print(f"📊 데이터베이스: {settings.database_url}")
        print(f"🐛 디버그 모드: {settings.debug}")
        print(f"📝 로그 레벨: {settings.log_level}")
    else:
        print(f"AdEdge Backend started - Environment: {settings.active_profile}")