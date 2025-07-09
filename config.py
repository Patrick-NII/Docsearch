import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    
    # Vector Database
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./vector_db")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Document Processing
    SOURCE_DIR: str = os.getenv("SOURCE_DIR", "./source")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50"))  # MB
    SUPPORTED_FORMATS: list = [
        '.pdf', '.txt', '.docx', '.doc', 
        '.xlsx', '.xls', '.csv',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'
    ]
    
    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Image Processing
    ENABLE_OCR: bool = os.getenv("ENABLE_OCR", "true").lower() == "true"
    OCR_LANGUAGES: list = ["en", "fr"]  # Languages for OCR
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_TOKEN: str = os.getenv("API_TOKEN", "your-secret-token-here")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/app.log")
    
    # Security
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://yourdomain.com"
    ]
    
    class Config:
        env_file = ".env"

# Instance globale des paramètres
settings = Settings()

def get_model_config() -> Dict[str, Any]:
    """Retourne la configuration du modèle LLM"""
    return {
        "model": settings.OPENAI_MODEL,
        "temperature": settings.OPENAI_TEMPERATURE,
        "max_tokens": settings.OPENAI_MAX_TOKENS,
        "api_key": settings.OPENAI_API_KEY
    }

def get_embedding_config() -> Dict[str, Any]:
    """Retourne la configuration des embeddings"""
    return {
        "model_name": settings.EMBEDDING_MODEL,
        "model_kwargs": {"device": "cpu"},
        "encode_kwargs": {"normalize_embeddings": True}
    }

def get_rag_config() -> Dict[str, Any]:
    """Retourne la configuration RAG"""
    return {
        "chunk_size": settings.CHUNK_SIZE,
        "chunk_overlap": settings.CHUNK_OVERLAP,
        "top_k": settings.TOP_K_RESULTS
    } 