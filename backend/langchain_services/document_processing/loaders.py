"""
Multi-format document loaders using LangChain
"""
import io
import tempfile
import os
from typing import List, Optional, Dict, Any
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredMarkdownLoader
from langchain.schema import Document
from langchain_community.document_loaders.base import BaseLoader
import logging

logger = logging.getLogger(__name__)

class MultiFormatDocumentLoader:
    """Load documents from various formats using LangChain loaders"""
    
    def __init__(self):
        self.supported_formats = {
            'pdf': self._load_pdf,
            'docx': self._load_docx,
            'doc': self._load_docx,
            'txt': self._load_text,
            'md': self._load_markdown,
            'markdown': self._load_markdown
        }
    
    def load_document(self, content: bytes, file_type: str, 
                     metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Load document from bytes using appropriate loader"""
        if file_type.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        loader_func = self.supported_formats[file_type.lower()]
        documents = loader_func(content, metadata or {})
        
        # Add common metadata to all documents
        for doc in documents:
            doc.metadata.update({
                'file_type': file_type,
                'loader': 'langchain_multi_format'
            })
            if metadata:
                doc.metadata.update(metadata)
        
        logger.info(f"Loaded {len(documents)} documents from {file_type} file")
        return documents
    
    def _load_pdf(self, content: bytes, metadata: Dict[str, Any]) -> List[Document]:
        """Load PDF document"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()
            return documents
        finally:
            os.unlink(tmp_file_path)
    
    def _load_docx(self, content: bytes, metadata: Dict[str, Any]) -> List[Document]:
        """Load DOCX document"""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            loader = Docx2txtLoader(tmp_file_path)
            documents = loader.load()
            return documents
        finally:
            os.unlink(tmp_file_path)
    
    def _load_text(self, content: bytes, metadata: Dict[str, Any]) -> List[Document]:
        """Load text document"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as tmp_file:
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                text_content = content.decode('utf-8', errors='ignore')
            tmp_file.write(text_content)
            tmp_file_path = tmp_file.name
        
        try:
            loader = TextLoader(tmp_file_path, encoding='utf-8')
            documents = loader.load()
            return documents
        finally:
            os.unlink(tmp_file_path)
    
    def _load_markdown(self, content: bytes, metadata: Dict[str, Any]) -> List[Document]:
        """Load markdown document"""
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w') as tmp_file:
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                text_content = content.decode('utf-8', errors='ignore')
            tmp_file.write(text_content)
            tmp_file_path = tmp_file.name
        
        try:
            loader = UnstructuredMarkdownLoader(tmp_file_path)
            documents = loader.load()
            return documents
        finally:
            os.unlink(tmp_file_path)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return list(self.supported_formats.keys())
    
    def is_supported(self, file_type: str) -> bool:
        """Check if file type is supported"""
        return file_type.lower() in self.supported_formats
