# import os
# from pydantic_settings import BaseSettings
# from functools import lru_cache
#
#
# class Settings(BaseSettings):
#     # API Keys
#     GROQ_API_KEY: str
#     OPENAI_API_KEY: str
#
#     # Database
#     QUBE_DATABASE_URL: str
#
#     # ChromaDB
#     CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
#     CHROMA_COLLECTION_NAME: str = "database_registry"
#
#     # Embedding Model
#     EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
#
#     # LLM Models
#     GROQ_MODEL: str = "llama-3.3-70b-versatile"
#     OPENAI_MODEL: str = "gpt-4o-mini"
#
#     # Query Settings
#     MAX_ROWS_PREVIEW: int = 10
#     MAX_ROWS_EXPORT: int = 100000
#     QUERY_TIMEOUT_SECONDS: int = 30
#     TOP_K_TABLES: int = 5  # Retrieve top 5, then filter to top 3
#
#     # Security
#     ALLOWED_QUERY_TYPES: list = ["SELECT"]
#
#     class Config:
#         env_file = ".env"
#         case_sensitive = True
#
#
# @lru_cache()
# def get_settings():
#     return Settings()
#
# from pydantic_settings import BaseSettings, SettingsConfigDict
# from functools import lru_cache
#
# class Settings(BaseSettings):
#     # API Keys
#     GROQ_API_KEY: str
#     OPENAI_API_KEY: str
#
#     # Database
#     QUBE_DATABASE_URL: str
#
#     # ChromaDB
#     CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
#     CHROMA_COLLECTION_NAME: str = "database_registry"
#
#     # Embedding Model
#     EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
#
#     # LLM Models
#     GROQ_MODEL: str = "llama-3.3-70b-versatile"
#     OPENAI_MODEL: str = "gpt-4o-mini"
#
#     # Query Settings
#     MAX_ROWS_PREVIEW: int = 10
#     MAX_ROWS_EXPORT: int = 100000
#     QUERY_TIMEOUT_SECONDS: int = 30
#     TOP_K_TABLES: int = 5
#
#     # Security
#     ALLOWED_QUERY_TYPES: list[str] = ["SELECT"]
#
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         case_sensitive=True,
#         extra="ignore"   # 👈 THIS IS THE KEY LINE
#     )
#
# @lru_cache()
# def get_settings():
#     return Settings()


import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str
    OPENAI_API_KEY: str

    # Database
    QUBE_DATABASE_URL: str

    # ChromaDB
    CHROMA_API_KEY:str

    CHROMA_TENANT:str

    CHROMA_DATABASE:str

    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "database_registry"

    # Embedding Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # LLM Models
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Query Settings
    MAX_ROWS_PREVIEW: int = 10
    MAX_ROWS_EXPORT: int = 100000
    QUERY_TIMEOUT_SECONDS: int = 30
    TOP_K_TABLES: int = 5  # Retrieve top 5, then filter to top 3

    # Security
    ALLOWED_QUERY_TYPES: list = ["SELECT"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()
