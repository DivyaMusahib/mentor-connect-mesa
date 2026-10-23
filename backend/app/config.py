from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "Mentor Connect"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "mentor-connect-development-secure-session-key-replace-in-prod"
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"

    # CORS origins
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @property
    def cors_origins(self) -> List[str]:
        origins = list(self.ALLOWED_ORIGINS)
        if self.FRONTEND_URL and self.FRONTEND_URL.rstrip("/") not in origins:
            origins.append(self.FRONTEND_URL.rstrip("/"))
        return origins

    # Database: SQLite default for instant dev & evaluation, PostgreSQL supported
    DATABASE_URL: str = "sqlite:///./mentor_connect.db"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Session Cookie Configuration
    SESSION_COOKIE_NAME: str = "mentor_connect_session"
    SESSION_MAX_AGE_SECONDS: int = 60 * 60 * 24 * 7  # 7 days
    COOKIE_SECURE: bool = False  # Set to True in production (HTTPS)
    COOKIE_SAMESITE: str = "lax"  # "lax" or "none" (if cross-domain with secure)
    COOKIE_DOMAIN: Optional[str] = None

    # Google Gemini AI (google-genai SDK)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # n8n Cloud Automation Integration
    N8N_BASE_URL: str = "https://mentor-connect-demo.app.n8n.cloud"
    N8N_WEBHOOK_SECRET: str = "mentor-connect-n8n-shared-secret-key"
    FASTAPI_WEBHOOK_SECRET: str = "mentor-connect-fastapi-callback-secret-key"

    # Host Calendar identifier for n8n scheduling
    HOST_CALENDAR_ID: str = "primary"

    # Transcription Provider
    TRANSCRIPTION_PROVIDER: str = "fathom"  # fathom | simulation | recall_ai | fireflies
    TRANSCRIPTION_API_KEY: str = ""
    TRANSCRIPTION_WEBHOOK_SECRET: str = "mentor-connect-transcript-secret"

    # Mentor dataset path
    MENTOR_DATA_PATH: Path = BASE_DIR / "data" / "mentors_50.csv"

    # Evaluator Demo Mode
    ENABLE_EVALUATOR_DEMO: bool = True

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
