"""
Text splitters using LangChain with hybrid approach
"""
from typing import List, Optional
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter, 
    TokenTextSplitter,
    NLTKTextSplitter
)
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

class HybridTextSplitter:
    """Hybrid text splitter combining multiple splitting strategies"""
    
    def __init__(self, 
                 chunk_size: int = 1000, 
                 chunk_overlap: int = 200,
                 separators: Optional[List[str]] = None,
                 use_token_based: bool = False,
                 token_model: str = "gpt-3.5-turbo"):
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_token_based = use_token_based
        
        # Initialize recursive character splitter (default)
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]
        
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=separators
        )
        
        # Initialize token-based splitter if requested
        if use_token_based:
            self.token_splitter = TokenTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                model_name=token_model
            )
        else:
            self.token_splitter = None
    
    def split_documents(self, 
                       documents: List[Document], 
                       splitter_type: str = "recursive",
                       preserve_metadata: bool = True) -> List[Document]:
        """
        Split documents using specified strategy
        
        Args:
            documents: List of documents to split
            splitter_type: Type of splitter to use ("recursive", "token", "nltk")
            preserve_metadata: Whether to preserve original metadata
        """
        try:
            if splitter_type == "recursive":
                split_docs = self.recursive_splitter.split_documents(documents)
            elif splitter_type == "token" and self.token_splitter:
                split_docs = self.token_splitter.split_documents(documents)
            elif splitter_type == "nltk":
                # Use NLTK splitter for sentence-aware splitting
                nltk_splitter = NLTKTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
                split_docs = nltk_splitter.split_documents(documents)
            else:
                # Fallback to recursive
                split_docs = self.recursive_splitter.split_documents(documents)
            
            # Add chunk metadata
            if preserve_metadata:
                for i, doc in enumerate(split_docs):
                    doc.metadata.update({
                        'chunk_index': i,
                        'chunk_size': len(doc.page_content),
                        'splitter_type': splitter_type,
                        'chunk_overlap': self.chunk_overlap
                    })
            
            logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks using {splitter_type} splitter")
            return split_docs
            
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            # Fallback to simple splitting
            return self._fallback_split(documents)
    
    def split_text(self, text: str, splitter_type: str = "recursive") -> List[str]:
        """Split text using specified strategy"""
        try:
            if splitter_type == "recursive":
                return self.recursive_splitter.split_text(text)
            elif splitter_type == "token" and self.token_splitter:
                return self.token_splitter.split_text(text)
            else:
                return self.recursive_splitter.split_text(text)
        except Exception as e:
            logger.error(f"Error splitting text: {e}")
            # Fallback to simple splitting
            return self._fallback_text_split(text)
    
    def _fallback_split(self, documents: List[Document]) -> List[Document]:
        """Fallback splitting method"""
        split_docs = []
        for doc in documents:
            # Simple split by newlines
            chunks = doc.page_content.split('\n\n')
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    new_doc = Document(
                        page_content=chunk.strip(),
                        metadata={
                            **doc.metadata,
                            'chunk_index': i,
                            'chunk_size': len(chunk),
                            'splitter_type': 'fallback'
                        }
                    )
                    split_docs.append(new_doc)
        return split_docs
    
    def _fallback_text_split(self, text: str) -> List[str]:
        """Fallback text splitting method"""
        # Simple split by double newlines
        chunks = text.split('\n\n')
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    def get_chunk_stats(self, documents: List[Document]) -> dict:
        """Get statistics about chunked documents"""
        if not documents:
            return {}
        
        chunk_sizes = [len(doc.page_content) for doc in documents]
        
        return {
            'total_chunks': len(documents),
            'avg_chunk_size': sum(chunk_sizes) / len(chunk_sizes),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes),
            'total_characters': sum(chunk_sizes)
        }

class SemanticTextSplitter:
    """Semantic-aware text splitter for better context preservation"""
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 similarity_threshold: float = 0.8):
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_threshold = similarity_threshold
        
        # Use recursive splitter as base
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents with semantic awareness"""
        # First, use base splitter
        base_chunks = self.base_splitter.split_documents(documents)
        
        # Then apply semantic merging/splitting
        semantic_chunks = self._apply_semantic_processing(base_chunks)
        
        return semantic_chunks
    
    def _apply_semantic_processing(self, chunks: List[Document]) -> List[Document]:
        """Apply semantic processing to merge/split chunks"""
        # For now, return base chunks
        # In production, implement semantic similarity-based merging
        return chunks
