import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Optional, List, Tuple
import io
from pdf2image import convert_from_bytes
import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, tesseract_path: Optional[str] = None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Remove noise
        denoised = cv2.medianBlur(thresh, 3)
        
        return denoised
    
    def extract_text_from_image(self, image_bytes: bytes, lang: str = 'eng') -> str:
        """Extract text from image bytes"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)
            processed_image = self.preprocess_image(image_np)
            
            # Perform OCR
            text = pytesseract.image_to_string(
                processed_image,
                lang=lang,
                config='--psm 3 --oem 3'
            )
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, pdf_bytes: bytes, lang: str = 'eng') -> List[Tuple[int, str]]:
        """Extract text from PDF with page numbers"""
        results = []
        
        try:
            # Try PyMuPDF first for native PDF text
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():  # If text exists
                    results.append((page_num + 1, text))
                else:  # Fallback to OCR for scanned PDFs
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    ocr_text = self.extract_text_from_image(img_bytes, lang)
                    results.append((page_num + 1, ocr_text))
            doc.close()
        except Exception as e:
            logger.warning(f"PyMuPDF failed, using OCR: {str(e)}")
            # Fallback to pdf2image + OCR
            images = convert_from_bytes(pdf_bytes)
            for i, image in enumerate(images):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                text = self.extract_text_from_image(img_byte_arr.getvalue(), lang)
                results.append((i + 1, text))
                
        return results