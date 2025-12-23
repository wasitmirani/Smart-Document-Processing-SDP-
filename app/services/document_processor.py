from typing import Dict, Any, Optional, List
import os
import uuid
from datetime import datetime
import logging
from .ocr_service import OCRService
from .ai_processor import AIProcessor
from app.utils.file_handlers import FileHandler

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.ocr_service = OCRService()
        self.ai_processor = AIProcessor()
        self.file_handler = FileHandler(upload_dir)
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # In-memory storage (replace with database in production)
        self.documents: Dict[str, Dict] = {}
        
    async def process_document(
        self,
        file,
        filename: str,
        extract_text: bool = True,
        perform_ocr: bool = False,
        extract_entities: bool = False,
        classify_document: bool = False
    ) -> Dict[str, Any]:
        """Process a document with specified operations"""
        
        start_time = datetime.now()
        document_id = str(uuid.uuid4())
        
        # Save file
        file_path = await self.file_handler.save_file(file, filename)
        file_size = os.path.getsize(file_path)
        
        # Initialize document record
        document = {
            "id": document_id,
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "upload_date": datetime.now(),
            "processing_status": "processing",
            "metadata": {}
        }
        
        self.documents[document_id] = document
        
        try:
            results = {
                "document_id": document_id,
                "text_content": None,
                "entities": None,
                "document_type": None,
                "confidence": None,
                "pages": [],
                "key_value_pairs": {},
                "summary": None
            }
            
            # Extract text based on file type
            if extract_text:
                text_content = await self.file_handler.extract_text(file_path)
                results["text_content"] = text_content
                
                # If text extraction yields little content and OCR is requested
                if perform_ocr or (len(text_content.strip()) < 50 and extract_text):
                    if filename.lower().endswith('.pdf'):
                        pages = self.ocr_service.extract_text_from_pdf(
                            open(file_path, 'rb').read()
                        )
                        results["pages"] = [
                            {"page_number": page_num, "text": text}
                            for page_num, text in pages
                        ]
                        results["text_content"] = "\n".join([text for _, text in pages])
                    else:
                        # For images
                        with open(file_path, 'rb') as f:
                            ocr_text = self.ocr_service.extract_text_from_image(f.read())
                            results["text_content"] = ocr_text
                            
            # Classify document
            if classify_document and results["text_content"]:
                classification = self.ai_processor.classify_document(results["text_content"])
                results["document_type"] = classification["type"]
                results["confidence"] = classification["confidence"]
                document["document_type"] = classification["type"]
                
            # Extract entities
            if extract_entities and results["text_content"]:
                entities = self.ai_processor.extract_entities(results["text_content"])
                results["entities"] = entities
                
                # Extract key-value pairs for structured documents
                if results["document_type"] in ["invoice", "receipt", "form"]:
                    kv_pairs = self.ai_processor.extract_key_value_pairs(results["text_content"])
                    results["key_value_pairs"] = kv_pairs
                    
            # Generate summary for long documents
            if results["text_content"] and len(results["text_content"]) > 500:
                results["summary"] = self.ai_processor.summarize_text(results["text_content"])
                
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            results["processing_time"] = processing_time
            
            # Update document status
            document["processing_status"] = "completed"
            document["metadata"].update({
                "processing_time": processing_time,
                "page_count": len(results.get("pages", [])),
                "operations_performed": {
                    "extract_text": extract_text,
                    "perform_ocr": perform_ocr,
                    "extract_entities": extract_entities,
                    "classify_document": classify_document
                }
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            document["processing_status"] = "failed"
            document["metadata"]["error"] = str(e)
            raise
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """Retrieve document by ID"""
        return self.documents.get(document_id)
    
    def list_documents(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """List all processed documents"""
        return list(self.documents.values())[skip:skip + limit]