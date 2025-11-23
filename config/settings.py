import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional


class Settings:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.active_profile = self._get_active_profile()
        self._load_environment_config()
    
    def _get_active_profile(self) -> str:
        profile = os.getenv('ACTIVE_PROFILE')
        if profile:
            return profile
        
        default_env_path = self.base_dir / 'default.env'
        if default_env_path.exists():
            load_dotenv(default_env_path)
            profile = os.getenv('ACTIVE_PROFILE')
            if profile:
                return profile
        
        return 'local'
    
    def _load_environment_config(self):
        env_file = self.base_dir / f'{self.active_profile}.env'
        
        if env_file.exists():
            load_dotenv(env_file)
        else:
            raise FileNotFoundError(f"환경 설정 파일을 찾을 수 없습니다: {env_file}")
    
    @property
    def database_url(self) -> str:
        url = os.getenv('DATABASE_URL')
        if not url:
            raise ValueError(f"DATABASE_URL이 설정되지 않았습니다. ({self.active_profile} 환경)")
        return url
    
    @property
    def debug(self) -> bool:
        return os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    @property
    def log_level(self) -> str:
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def redis_host(self) -> str:
        host = self.get_env('REDIS_HOST')
        if not host:
            raise ValueError(f"REDIS_HOST이 설정되지 않았습니다. ({self.active_profile} 환경)")
        return host
    
    @property
    def redis_port(self) -> int:
        port = self.get_env('REDIS_PORT')
        if not port:
            raise ValueError(f"REDIS_PORT이 설정되지 않았습니다. ({self.active_profile} 환경)")
        return int(port)
    
    @property
    def redis_password(self) -> Optional[str]:
        return self.get_env('REDIS_PASSWORD')
    
    @property
    def redis_db(self) -> int:
        db = self.get_env('REDIS_DB', '0')
        return int(db)
    
    @property
    def solapi_api_key(self) -> str:
        api_key = self.get_env('SOLAPI_API_KEY')
        if not api_key:
            raise ValueError(f"SOLAPI_API_KEY이 설정되지 않았습니다. ({self.active_profile} 환경)")
        return api_key
    
    @property
    def solapi_api_secret(self) -> str:
        api_secret = self.get_env('SOLAPI_API_SECRET')
        if not api_secret:
            raise ValueError(f"SOLAPI_API_SECRET이 설정되지 않았습니다. ({self.active_profile} 환경)")
        return api_secret
    
    @property
    def solapi_from_number(self) -> str:
        from_number = self.get_env('SOLAPI_FROM_NUMBER')
        if not from_number:
            raise ValueError(f"SOLAPI_FROM_NUMBER이 설정되지 않았습니다. ({self.active_profile} 환경)")
        return from_number
    
    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default)
    
    def __str__(self):
        return f"Settings(profile={self.active_profile}, debug={self.debug})"
