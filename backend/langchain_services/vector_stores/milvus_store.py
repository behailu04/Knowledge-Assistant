"""
Milvus vector store implementation with tenant isolation
"""
import os
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4, UUID

from pymilvus import (
    connections, Collection, FieldSchema, CollectionSchema, DataType,
    utility, MilvusException
)
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

from config import settings

logger = logging.getLogger(__name__)

class TenantAwareMilvusStore(VectorStore):
    """Milvus vector store with tenant isolation"""
    
    def __init__(self, 
                 embedding_function: Embeddings,
                 collection_name: str = None,
                 connection_args: Dict[str, Any] = None):
        """
        Initialize Milvus vector store
        
        Args:
            embedding_function: Embedding function to use
            collection_name: Base collection name (tenant_id will be appended)
            connection_args: Milvus connection arguments
        """
        self.embedding_function = embedding_function
        self.collection_name = collection_name or settings.MILVUS_COLLECTION_NAME
        self.connection_args = connection_args or {
            "host": settings.MILVUS_HOST,
            "port": settings.MILVUS_PORT
        }
        
        # Connect to Milvus
        self._connect()
        
        # Store tenant collections
        self.tenant_collections: Dict[str, Collection] = {}
        
        logger.info(f"Initialized Milvus store with collection: {self.collection_name}")
    
    def _connect(self):
        """Connect to Milvus"""
        try:
            connections.connect("default", **self.connection_args)
            logger.info(f"Connected to Milvus at {self.connection_args['host']}:{self.connection_args['port']}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def _get_collection_name(self, tenant_id: str) -> str:
        """Get collection name for tenant"""
        return f"{self.collection_name}_{tenant_id}"
    
    def _create_collection(self, tenant_id: str) -> Collection:
        """Create a new collection for tenant"""
        collection_name = self._get_collection_name(tenant_id)
        
        # Check if collection already exists
        if utility.has_collection(collection_name):
            logger.info(f"Collection {collection_name} already exists")
            return Collection(collection_name)
        
        # Define collection schema
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="tenant_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="metadata", dtype=DataType.JSON),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.MILVUS_DIMENSION)
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description=f"Knowledge chunks for tenant {tenant_id}",
            enable_dynamic_field=True
        )
        
        # Create collection
        collection = Collection(
            name=collection_name,
            schema=schema,
            using='default',
            shards_num=2
        )
        
        # Create index
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        
        collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        logger.info(f"Created collection {collection_name} for tenant {tenant_id}")
        return collection
    
    def _get_collection(self, tenant_id: str) -> Collection:
        """Get or create collection for tenant"""
        if tenant_id not in self.tenant_collections:
            self.tenant_collections[tenant_id] = self._create_collection(tenant_id)
        
        collection = self.tenant_collections[tenant_id]
        
        # Load collection if not loaded
        if not collection.has_index():
            collection.load()
        elif not collection.is_empty:
            # Check if collection is loaded, if not load it
            try:
                collection.load()
            except Exception as e:
                logger.warning(f"Collection already loaded or error loading: {e}")
        
        return collection
    
    def add_documents(self, documents: List[Document], tenant_id: str) -> List[str]:
        """Add documents to Milvus collection"""
        if not documents:
            return []
        
        collection = self._get_collection(tenant_id)
        
        # Prepare data
        ids = []
        texts = []
        tenant_ids = []
        doc_ids = []
        metadatas = []
        embeddings = []
        
        for doc in documents:
            doc_id = str(uuid4())
            ids.append(doc_id)
            texts.append(doc.page_content)
            tenant_ids.append(tenant_id)
            doc_ids.append(str(doc.metadata.get("doc_id", "")))
            # Convert UUIDs to strings in metadata for JSON serialization
            metadata = {}
            for key, value in doc.metadata.items():
                if isinstance(value, UUID):
                    metadata[key] = str(value)
                else:
                    metadata[key] = value
            metadatas.append(metadata)
            
            # Generate embedding
            embedding = self.embedding_function.embed_query(doc.page_content)
            embeddings.append(embedding)
        
        # Insert data
        data = [
            ids,
            texts,
            tenant_ids,
            doc_ids,
            metadatas,
            embeddings
        ]
        
        try:
            collection.insert(data)
            collection.flush()
            logger.info(f"Added {len(documents)} documents to tenant {tenant_id}")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to Milvus: {e}")
            raise
    
    @classmethod
    def from_texts(cls, 
                   texts: List[str], 
                   embedding: Embeddings,
                   metadatas: List[Dict] = None,
                   tenant_id: str = "default",
                   **kwargs) -> "TenantAwareMilvusStore":
        """Create Milvus store from texts (required by VectorStore interface)"""
        store = cls(embedding_function=embedding, **kwargs)
        
        # Convert texts to documents
        documents = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            documents.append(Document(page_content=text, metadata=metadata))
        
        # Add documents to store
        store.add_documents(documents, tenant_id)
        return store
    
    def similarity_search(self, 
                         query: str, 
                         k: int = 4, 
                         tenant_id: str = "default",
                         **kwargs) -> List[Document]:
        """Perform similarity search"""
        collection = self._get_collection(tenant_id)
        
        # Generate query embedding
        query_embedding = self.embedding_function.embed_query(query)
        
        # Search parameters
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        # Perform search
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=k,
            expr=f'tenant_id == "{tenant_id}"',
            output_fields=["text", "metadata", "doc_id"]
        )
        
        # Convert results to documents
        documents = []
        for hits in results:
            for hit in hits:
                doc = Document(
                    page_content=hit.entity.get("text"),
                    metadata={
                        **hit.entity.get("metadata", {}),
                        "score": hit.score,
                        "doc_id": hit.entity.get("doc_id")
                    }
                )
                documents.append(doc)
        
        return documents
    
    def as_retriever(self, tenant_id: str = "default", **kwargs) -> BaseRetriever:
        """Get retriever for tenant"""
        return MilvusRetriever(
            vectorstore=self,
            tenant_id=tenant_id,
            **kwargs
        )
    
    def delete_collection(self, tenant_id: str):
        """Delete collection for tenant"""
        collection_name = self._get_collection_name(tenant_id)
        
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
            logger.info(f"Dropped collection {collection_name}")
        
        if tenant_id in self.tenant_collections:
            del self.tenant_collections[tenant_id]

class MilvusRetriever(BaseRetriever):
    """Milvus retriever with tenant isolation"""
    
    vectorstore: TenantAwareMilvusStore = Field(...)
    tenant_id: str = Field(default="default")
    search_kwargs: Dict[str, Any] = Field(default_factory=lambda: {"k": 4})
    
    class Config:
        arbitrary_types_allowed = True
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Get relevant documents for query"""
        return self.vectorstore.similarity_search(
            query=query,
            tenant_id=self.tenant_id,
            **self.search_kwargs
        )
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Get relevant documents (deprecated method)"""
        return self._get_relevant_documents(query)
