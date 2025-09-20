'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { apiService, Document, DocumentUploadRequest } from '@/lib/api';

// Document interface is now imported from api.ts

interface DocumentContextType {
  documents: Document[];
  loading: boolean;
  uploadDocument: (file: File, metadata: any) => Promise<void>;
  deleteDocument: (docId: string) => Promise<void>;
  getDocumentStatus: (docId: string) => Promise<any>;
  refreshDocuments: () => Promise<void>;
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export const useDocument = () => {
  const context = useContext(DocumentContext);
  if (!context) {
    throw new Error('useDocument must be used within a DocumentProvider');
  }
  return context;
};

export const DocumentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);

  // Load documents on mount
  useEffect(() => {
    refreshDocuments();
  }, []);

  const uploadDocument = useCallback(async (file: File, metadata: any) => {
    setLoading(true);
    try {
      const uploadRequest: DocumentUploadRequest = {
        file,
        tenant_id: metadata.tenant_id,
        doc_type: metadata.doc_type,
        language: metadata.language || 'en'
      };

      const response = await apiService.uploadDocument(uploadRequest);
      
      // Add the new document to the list
      setDocuments(prev => [response, ...prev]);
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteDocument = useCallback(async (docId: string) => {
    try {
      await apiService.deleteDocument(docId);
      
      // Remove the document from the list
      setDocuments(prev => prev.filter(doc => doc.doc_id !== docId));
    } catch (error) {
      console.error('Error deleting document:', error);
      throw error;
    }
  }, []);

  const getDocumentStatus = useCallback(async (docId: string) => {
    try {
      return await apiService.getDocumentStatus(docId);
    } catch (error) {
      console.error('Error getting document status:', error);
      throw error;
    }
  }, []);

  const refreshDocuments = useCallback(async () => {
    setLoading(true);
    try {
      const docs = await apiService.getDocuments('org_123', 100);
      setDocuments(docs);
    } catch (error) {
      console.error('Error refreshing documents:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <DocumentContext.Provider value={{
      documents,
      loading,
      uploadDocument,
      deleteDocument,
      getDocumentStatus,
      refreshDocuments,
    }}>
      {children}
    </DocumentContext.Provider>
  );
};
