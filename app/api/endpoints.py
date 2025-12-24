from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import os
import json

from app.models.schemas import (
    Document, ExtractionRequest, ExtractionResult, 
    BatchProcessingRequest, DocumentUpload, User, Token
)
from app.services.document_processor import DocumentProcessor
from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()
processor = DocumentProcessor(settings.UPLOAD_DIR)

@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    extract_text: bool = True,
    perform_ocr: bool = False,
    extract_entities: bool = False,
    classify_document: bool = False,
    # current_user: User = Depends(get_current_user)
):
    """Upload and process a document"""
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset pointer
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    try:
        # Process document
        result = await processor.process_document(
            file=file,
            filename=file.filename,
            extract_text=extract_text,
            perform_ocr=perform_ocr,
            extract_entities=extract_entities,
            classify_document=classify_document
        )
        
        # Get document record
        document = processor.get_document(result["document_id"])
        
        return document
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/extract", response_model=ExtractionResult)
async def extract_from_document(
    request: ExtractionRequest
    # current_user: User = Depends(get_current_user)
):
    """Extract information from already uploaded document"""
    document = processor.get_document(request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Re-process with new parameters
    with open(document["file_path"], 'rb') as f:
        class FakeFile:
            def __init__(self, content, filename):
                self.file = content
                self.filename = filename
        
        fake_file = FakeFile(f, document["filename"])
        
        result = await processor.process_document(
            file=fake_file,
            filename=document["filename"],
            extract_text=request.extract_text,
            perform_ocr=request.perform_ocr,
            extract_entities=request.extract_entities,
            classify_document=request.classify_document
        )
    
    return result

@router.post("/batch-process")
async def batch_process_documents(
    request: BatchProcessingRequest,
    background_tasks: BackgroundTasks,
    # current_user: User = Depends(get_current_user)
):
    """Process multiple documents in batch"""
    batch_id = str(uuid.uuid4())
    results = []
    
    for doc_id in request.document_ids:
        document = processor.get_document(doc_id)
        if document:
            background_tasks.add_task(
                process_single_document,
                document,
                request.operations
            )
            results.append({
                "document_id": doc_id,
                "status": "queued",
                "batch_id": batch_id
            })
    
    return {
        "batch_id": batch_id,
        "total_documents": len(results),
        "results": results
    }

@router.get("/documents", response_model=List[Document])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    # current_user: User = Depends(get_current_user)
):
    """List all processed documents"""
    return processor.list_documents(skip=skip, limit=limit)

@router.get("/documents/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    # current_user: User = Depends(get_current_user)
):
    """Get document by ID"""
    document = processor.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/documents/{document_id}/text")
async def get_document_text(
    document_id: str,
    # current_user: User = Depends(get_current_user)
):
    """Get extracted text from document"""
    document = processor.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # In production, you would retrieve this from a database
    return {"text": "Extracted text would be here..."}

@router.get("/documents/{document_id}/entities")
async def get_document_entities(
    document_id: str,
    # current_user: User = Depends(get_current_user)
):
    """Get entities extracted from document"""
    document = processor.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # In production, you would retrieve this from a database
    return {"entities": []}

@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    # current_user: User = Depends(get_current_user)
):
    """Download original document"""
    document = processor.get_document(document_id)
    if not document or not os.path.exists(document["file_path"]):
        raise HTTPException(status_code=404, detail="Document not found")
    
    return FileResponse(
        path=document["file_path"],
        filename=document["filename"],
        media_type="application/octet-stream"
    )

@router.post("/classify")
async def classify_text(
    text: str,
    # current_user: User = Depends(get_current_user)
):
    """Classify text content"""
    from app.services.ai_processor import AIProcessor
    processor = AIProcessor()
    result = processor.classify_document(text)
    return result

@router.post("/extract-entities")
async def extract_entities_from_text(
    text: str,
    # current_user: User = Depends(get_current_user)
):
    """Extract entities from text"""
    from app.services.ai_processor import AIProcessor
    processor = AIProcessor()
    entities = processor.extract_entities(text)
    return {"entities": entities}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Smart Document Processing API",
        "version": "1.0.0"
    }

# Helper function for batch processing
async def process_single_document(document: dict, operations: List[str]):
    """Process a single document (for background tasks)"""
    # Implementation for background processing
    pass