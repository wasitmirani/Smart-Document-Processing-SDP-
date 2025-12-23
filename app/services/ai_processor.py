import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Any, Optional
import nltk
from nltk.tokenize import sent_tokenize
import torch
import logging

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            
        # Initialize transformers pipelines
        self.classifier = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        
        self.ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
        
        # Download NLTK data
        nltk.download('punkt', quiet=True)
        
    def classify_document(self, text: str, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Classify document type based on content"""
        if not text.strip():
            return {"type": "unknown", "confidence": 0.0}
            
        # Use rule-based classification first
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['invoice', 'bill', 'total', 'amount due']):
            return {"type": "invoice", "confidence": 0.9}
        elif any(keyword in text_lower for keyword in ['contract', 'agreement', 'terms and conditions']):
            return {"type": "contract", "confidence": 0.85}
        elif any(keyword in text_lower for keyword in ['resume', 'cv', 'experience', 'education']):
            return {"type": "resume", "confidence": 0.8}
        elif any(keyword in text_lower for keyword in ['receipt', 'payment', 'thank you for your purchase']):
            return {"type": "receipt", "confidence": 0.85}
            
        # Fallback to ML model
        try:
            result = self.classifier(text[:512])  # Limit text length
            return {
                "type": result[0]['label'],
                "confidence": result[0]['score']
            }
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return {"type": "other", "confidence": 0.5}
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        entities = []
        
        try:
            # Use spaCy
            doc = self.nlp(text[:10000])  # Limit text length
            
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.9  # spaCy doesn't provide confidence
                })
                
            # Use BERT NER for additional entities
            ner_results = self.ner_pipeline(text[:512])
            for entity in ner_results:
                entities.append({
                    "text": entity['word'],
                    "type": entity['entity_group'],
                    "start": entity['start'],
                    "end": entity['end'],
                    "confidence": entity['score']
                })
                
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            
        return entities
    
    def extract_key_value_pairs(self, text: str, patterns: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract key-value pairs from structured documents"""
        kv_pairs = {}
        
        # Common patterns for invoices/receipts
        default_patterns = {
            'date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            'total': r'(?:total|amount due|balance)[:\s]*[\$€£]?\s*[\d,]+\.?\d*',
            'invoice_number': r'(?:invoice|inv)\.?\s*#?\s*[A-Z0-9\-]+',
            'tax': r'(?:tax|vat|gst)[:\s]*[\$€£]?\s*[\d,]+\.?\d*',
        }
        
        import re
        search_patterns = patterns or default_patterns
        
        for key, pattern in search_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                kv_pairs[key] = match.group()
                
        return kv_pairs
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """Generate a summary of the text"""
        sentences = sent_tokenize(text)
        if len(sentences) <= max_sentences:
            return text
            
        # Simple extraction-based summarization
        # In production, use BART or T5 for better results
        return ' '.join(sentences[:max_sentences])