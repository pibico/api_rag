"""
Configuration management for RAG application
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = Field(default="RAG Document Chat", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    ROOT_PATH: str = Field(default="", env="ROOT_PATH")  # Set to /rag when behind nginx proxy

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen2.5:7b-instruct", env="OLLAMA_MODEL")
    ollama_temperature: float = Field(default=0.1, env="OLLAMA_TEMPERATURE")
    ollama_max_tokens: int = Field(default=8000, env="OLLAMA_MAX_TOKENS")
    ollama_num_gpu: int = Field(default=1, env="OLLAMA_NUM_GPU")
    ollama_num_threads: int = Field(default=8, env="OLLAMA_NUM_THREADS")

    # LEANN Configuration
    leann_index_path: str = Field(default="./data/leann_index", env="LEANN_INDEX_PATH")
    leann_backend: str = Field(default="hnsw", env="LEANN_BACKEND")
    leann_embedding_batch_size: int = Field(default=32, env="LEANN_EMBEDDING_BATCH_SIZE")
    leann_use_gpu: bool = Field(default=True, env="LEANN_USE_GPU")
    leann_num_threads: int = Field(default=4, env="LEANN_NUM_THREADS")
    leann_default_similarity_threshold: float = Field(default=0.0, env="LEANN_DEFAULT_SIMILARITY_THRESHOLD")

    # Database
    database_url: str = Field(default="sqlite:///./rag_app.db", env="DATABASE_URL")

    # File Upload
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_upload_size: int = Field(default=100000000, env="MAX_UPLOAD_SIZE")  # 100MB

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(os.path.dirname(settings.leann_index_path) if os.path.dirname(settings.leann_index_path) else settings.leann_index_path, exist_ok=True)
