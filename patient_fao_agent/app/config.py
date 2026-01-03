from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # API Keys
    OPENAI_API_KEY: str
    GROQ_API_KEY: str
    DEEPGRAM_API_KEY: str
    ELEVENLABS_API_KEY: str

    # Model Configuration
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Voice Configuration
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"

    # Token Limits
    MAX_INPUT_TOKENS: int = 4000
    MAX_OUTPUT_TOKENS: int = 1000

    # File Processing
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: list = ["application/pdf"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()