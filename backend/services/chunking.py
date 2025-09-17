"""
Document chunking service with hybrid approach
"""
import logging
import uuid
import re
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ChunkMetadata:
    """Metadata for a text chunk"""
    doc_id: str
    chunk_id: str
    start_pos: int
    end_pos: int
    heading: str = None
    language: str = "en"
    entities: List[str] = None
    chunk_type: str = "paragraph"  # paragraph, semantic, sentence

class ChunkingService:
    """Service for intelligent text chunking"""
    
    def __init__(self, chunk_size: int = 400, overlap: int = 50, min_chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
    
    async def chunk_text(self, text: str, doc_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Chunk text using hybrid approach (paragraph + semantic)"""
        try:
            # Clean and preprocess text
            cleaned_text = self._clean_text(text)
            
            # Split into paragraphs first
            paragraphs = self._split_paragraphs(cleaned_text)
            
            chunks = []
            current_pos = 0
            
            for paragraph in paragraphs:
                if len(paragraph.strip()) < self.min_chunk_size:
                    # Skip very short paragraphs
                    current_pos += len(paragraph)
                    continue
                
                if len(paragraph) <= self.chunk_size:
                    # Paragraph fits in one chunk
                    chunk = self._create_chunk(
                        text=paragraph,
                        doc_id=doc_id,
                        tenant_id=tenant_id,
                        start_pos=current_pos,
                        end_pos=current_pos + len(paragraph),
                        chunk_type="paragraph"
                    )
                    chunks.append(chunk)
                    current_pos += len(paragraph)
                else:
                    # Split large paragraph into smaller chunks
                    sub_chunks = self._split_large_paragraph(
                        paragraph, doc_id, tenant_id, current_pos
                    )
                    chunks.extend(sub_chunks)
                    current_pos += len(paragraph)
            
            # Apply semantic chunking for better context preservation
            chunks = self._apply_semantic_chunking(chunks)
            
            # Add overlap between chunks
            chunks = self._add_chunk_overlap(chunks)
            
            logger.info(f"Created {len(chunks)} chunks for document {doc_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text for document {doc_id}: {e}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere with chunking
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return text.strip()
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split on double newlines or paragraph breaks
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_large_paragraph(self, paragraph: str, doc_id: str, tenant_id: str, start_pos: int) -> List[Dict[str, Any]]:
        """Split a large paragraph into smaller chunks"""
        chunks = []
        sentences = self._split_sentences(paragraph)
        
        current_chunk = ""
        current_start = start_pos
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunk = self._create_chunk(
                        text=current_chunk.strip(),
                        doc_id=doc_id,
                        tenant_id=tenant_id,
                        start_pos=current_start,
                        end_pos=current_start + len(current_chunk),
                        chunk_type="semantic"
                    )
                    chunks.append(chunk)
                    current_start += len(current_chunk)
                
                current_chunk = sentence + " "
        
        # Add remaining text
        if current_chunk.strip():
            chunk = self._create_chunk(
                text=current_chunk.strip(),
                doc_id=doc_id,
                tenant_id=tenant_id,
                start_pos=current_start,
                end_pos=current_start + len(current_chunk),
                chunk_type="semantic"
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - in production, use more sophisticated NLP
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() + '.' for s in sentences if s.strip()]
    
    def _create_chunk(self, text: str, doc_id: str, tenant_id: str, start_pos: int, 
                     end_pos: int, chunk_type: str) -> Dict[str, Any]:
        """Create a chunk with metadata"""
        chunk_id = str(uuid.uuid4())
        
        # Extract heading if present
        heading = self._extract_heading(text)
        
        # Extract entities (simplified)
        entities = self._extract_entities(text)
        
        return {
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "tenant_id": tenant_id,
            "text": text,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "heading": heading,
            "language": "en",
            "entities": entities,
            "chunk_type": chunk_type,
            "metadata": {
                "chunk_type": chunk_type,
                "length": len(text),
                "word_count": len(text.split())
            }
        }
    
    def _extract_heading(self, text: str) -> str:
        """Extract heading from text chunk"""
        # Look for common heading patterns
        lines = text.split('\n')
        for line in lines[:3]:  # Check first few lines
            line = line.strip()
            if len(line) < 100 and (line.isupper() or line.endswith(':')):
                return line
        return None
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text (simplified)"""
        # Simple entity extraction - in production, use NER models
        entities = []
        
        # Look for common patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        entities.extend(emails)
        
        # Look for capitalized words that might be entities
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
        entities.extend(capitalized[:5])  # Limit to first 5
        
        return list(set(entities))  # Remove duplicates
    
    def _apply_semantic_chunking(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply semantic chunking to improve context preservation"""
        # This is a simplified version - in production, use semantic similarity
        # to merge related chunks or split unrelated content
        
        merged_chunks = []
        i = 0
        
        while i < len(chunks):
            current_chunk = chunks[i]
            
            # Try to merge with next chunk if both are small
            if (i + 1 < len(chunks) and 
                len(current_chunk["text"]) < self.chunk_size // 2 and
                len(chunks[i + 1]["text"]) < self.chunk_size // 2):
                
                # Merge chunks
                next_chunk = chunks[i + 1]
                merged_text = current_chunk["text"] + " " + next_chunk["text"]
                
                merged_chunk = self._create_chunk(
                    text=merged_text,
                    doc_id=current_chunk["doc_id"],
                    tenant_id=current_chunk["tenant_id"],
                    start_pos=current_chunk["start_pos"],
                    end_pos=next_chunk["end_pos"],
                    chunk_type="merged"
                )
                merged_chunks.append(merged_chunk)
                i += 2  # Skip both chunks
            else:
                merged_chunks.append(current_chunk)
                i += 1
        
        return merged_chunks
    
    def _add_chunk_overlap(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add overlap between chunks for better context"""
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                # First chunk - no overlap needed
                overlapped_chunks.append(chunk)
            else:
                # Add overlap from previous chunk
                prev_chunk = chunks[i - 1]
                overlap_text = self._get_overlap_text(prev_chunk["text"], self.overlap)
                
                if overlap_text:
                    overlapped_text = overlap_text + " " + chunk["text"]
                    
                    overlapped_chunk = self._create_chunk(
                        text=overlapped_text,
                        doc_id=chunk["doc_id"],
                        tenant_id=chunk["tenant_id"],
                        start_pos=chunk["start_pos"],
                        end_pos=chunk["end_pos"],
                        chunk_type=chunk["chunk_type"]
                    )
                    overlapped_chunks.append(overlapped_chunk)
                else:
                    overlapped_chunks.append(chunk)
        
        return overlapped_chunks
    
    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """Get overlap text from the end of a chunk"""
        words = text.split()
        if len(words) <= overlap_size:
            return text
        
        overlap_words = words[-overlap_size:]
        return " ".join(overlap_words)
