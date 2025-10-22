import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional


class Settings:
    """
    Spring의 active profile과 같은 기능을 제공하는 설정 관리 클래스
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.active_profile = self._get_active_profile()
        self._load_environment_config()
    
    def _get_active_profile(self) -> str:
        """
        환경 변수에서 ACTIVE_PROFILE을 읽어옵니다.
        기본값은 'local'입니다.
        """
        # 환경 변수에서 먼저 확인
        profile = os.getenv('ACTIVE_PROFILE')
        if profile:
            return profile
        
        # default.env 파일에서 확인
        default_env_path = self.base_dir / 'default.env'
        if default_env_path.exists():
            load_dotenv(default_env_path)
            profile = os.getenv('ACTIVE_PROFILE')
            if profile:
                return profile
        
        # 기본값 반환
        return 'local'
    
    def _load_environment_config(self):
        """
        활성 프로필에 해당하는 환경 설정을 로드합니다.
        """
        env_file = self.base_dir / f'{self.active_profile}.env'
        
        if env_file.exists():
            load_dotenv(env_file)
        else:
            raise FileNotFoundError(f"환경 설정 파일을 찾을 수 없습니다: {env_file}")
    
    @property
    def database_url(self) -> str:
        """데이터베이스 URL을 반환합니다."""
        url = os.getenv('DATABASE_URL')
        if not url:
            raise ValueError(f"DATABASE_URL이 설정되지 않았습니다. ({self.active_profile} 환경)")
        return url
    
    @property
    def debug(self) -> bool:
        """디버그 모드 여부를 반환합니다."""
        return os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    @property
    def log_level(self) -> str:
        """로그 레벨을 반환합니다."""
        return os.getenv('LOG_LEVEL', 'INFO')
    
    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """환경 변수 값을 가져옵니다."""
        return os.getenv(key, default)
    
    def __str__(self):
        return f"Settings(profile={self.active_profile}, debug={self.debug})"
