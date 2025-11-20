import redis.asyncio as redis
from typing import Optional
from config import settings
from app.core.exceptions import ServerException


class RedisClient:
    _instance: Optional[redis.Redis] = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Redis 클라이언트 싱글톤 인스턴스 반환"""
        if cls._instance is None:
            try:
                if settings.redis_password:
                    redis_url = f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
                else:
                    redis_url = f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"

                cls._instance = await redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
                await cls._instance.ping()
            except Exception as e:
                raise ServerException(f"Redis 연결 실패: {str(e)}")
        return cls._instance

    @classmethod
    async def close(cls):
        """Redis 연결 종료"""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

    @classmethod
    async def ping(cls) -> bool:
        """Redis 연결 상태 확인"""
        try:
            client = await cls.get_client()
            await client.ping()
            return True
        except Exception:
            return False


# FastAPI 의존성: Redis 클라이언트 반환
async def get_redis() -> redis.Redis:
    """FastAPI 의존성으로 사용할 Redis 클라이언트 반환"""
    return await RedisClient.get_client()
