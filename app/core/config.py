from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Document Processing API"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png", ".tiff", ".xlsx", ".csv"]
    UPLOAD_DIR: str = "uploads"
    
    # OCR Configuration
    TESSERACT_PATH: Optional[str] = None  # Set if tesseract not in PATH
    
    # AI Models
    SPACY_MODEL: str = "en_core_web_sm"
    CLASSIFICATION_MODEL: str = "distilbert-base-uncased"
    NER_MODEL: str = "dslim/bert-base-NER"
    
    # Redis/Celery (Optional)
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()