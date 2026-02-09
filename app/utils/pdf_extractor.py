"""
PDF Text Extraction Utility

CONCEPT: Extract raw text from PDF files for AI processing

WHY PYPDF2?
- Lightweight (no heavy dependencies)
- Handles most PDF formats
- Free and open-source

FLOW:
PDF bytes → PyPDF2.PdfReader → Extract each page → Concatenate text
"""

from PyPDF2 import PdfReader
from io import BytesIO
from typing import BinaryIO
import logging

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Handles PDF text extraction
    
    DESIGN PATTERN: Single Responsibility Principle
    This class does ONE thing: extract text from PDFs
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_file: BinaryIO) -> str:
        """
        Extract all text from a PDF file
        
        Args:
            pdf_file: Binary file object (from FastAPI UploadFile.file)
            
        Returns:
            Extracted text as a single string
            
        ALGORITHM:
        1. Create a PDF reader from binary stream
        2. Iterate through all pages
        3. Extract text from each page
        4. Join with newlines
        
        ERROR HANDLING:
        - Catches corrupt PDFs
        - Returns empty string if extraction fails
        - Logs errors for debugging
        """
        try:
            # CONCEPT: BytesIO creates an in-memory file-like object
            # This allows us to work with bytes as if they were a file
            pdf_reader = PdfReader(pdf_file)
            
            # CONCEPT: List comprehension - concise way to build lists
            # [expression for item in iterable]
            text_parts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    # extract_text() gets all text from one page
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                        logger.debug(f"Extracted {len(page_text)} chars from page {page_num + 1}")
                except Exception as page_error:
                    logger.warning(f"Failed to extract page {page_num + 1}: {page_error}")
                    continue
            
            # Join all pages with double newline
            full_text = "\n\n".join(text_parts)
            
            logger.info(f"Successfully extracted {len(full_text)} total characters")
            return full_text
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def clean_text(raw_text: str) -> str:
        """
        Clean extracted text for better AI parsing
        
        CONCEPT: Text preprocessing
        - Remove excessive whitespace
        - Normalize line breaks
        - Remove special characters that confuse LLMs
        
        Args:
            raw_text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        if not raw_text:
            return ""
        
        # Remove multiple spaces
        text = " ".join(raw_text.split())
        
        # Normalize line breaks (some PDFs have weird encoding)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Remove excessive newlines (more than 2 in a row)
        import re
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
