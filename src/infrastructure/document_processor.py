import PyPDF2
import io
from typing import List
import uuid
from datetime import datetime
from src.domain.document import Document, DocumentChunk

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_pdf(self, file_content: bytes, filename: str) -> Document:
        """Process PDF file and create document with chunks"""
        # Extract text from PDF
        text = self._extract_text_from_pdf(file_content)
        
        # Create chunks
        chunks = self._create_chunks(text, filename)
        
        # Create document
        document = Document(
            id=str(uuid.uuid4()),
            filename=filename,
            content=text,
            chunks=chunks,
            uploaded_at=datetime.now()
        )
        
        return document

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {e}")

    def _create_chunks(self, text: str, document_id: str) -> List[DocumentChunk]:
        """Create text chunks with overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + self.chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    content=chunk_text,
                    metadata={
                        "start_pos": start,
                        "end_pos": end,
                        "chunk_index": len(chunks)
                    }
                )
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks 