from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    INVOICE = "invoice"
    CONTRACT = "contract"
    RESUME = "resume"
    REPORT = "report"
    RECEIPT = "receipt"
    FORM = "form"
    OTHER = "other"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentUpload(BaseModel):
    filename: str
    content_type: str
    file_size: int

class DocumentBase(BaseModel):
    filename: str
    document_type: Optional[DocumentType] = None
    page_count: Optional[int] = None
    file_size: int

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: str
    upload_date: datetime
    processing_status: ProcessingStatus
    metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True

class ExtractionRequest(BaseModel):
    document_id: str
    extract_text: bool = True
    perform_ocr: bool = False
    extract_entities: bool = False
    classify_document: bool = False

class ExtractionResult(BaseModel):
    document_id: str
    text_content: Optional[str] = None
    entities: Optional[List[Dict[str, Any]]] = None
    document_type: Optional[DocumentType] = None
    confidence: Optional[float] = None
    pages: Optional[List[Dict[str, Any]]] = None
    processing_time: float
    metadata: Dict[str, Any] = {}

class BatchProcessingRequest(BaseModel):
    document_ids: List[str]
    operations: List[str] = Field(default=["extract", "classify"])

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None