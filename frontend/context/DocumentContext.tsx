'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import axios from 'axios';

interface Document {
  doc_id: string;
  tenant_id: string;
  original_path: string;
  doc_type: string;
  language: string;
  uploaded_at: string;
  is_processed: boolean;
  file_size: number;
  metadata: Record<string, any>;
}

interface DocumentContextType {
  documents: Document[];
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

  const uploadDocument = useCallback(async (file: File, metadata: any) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tenant_id', metadata.tenant_id);
    formData.append('doc_type', metadata.doc_type);
    formData.append('language', metadata.language);

    try {
      const response = await axios.post('/api/v1/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Add the new document to the list
      setDocuments(prev => [response.data, ...prev]);
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  }, []);

  const deleteDocument = useCallback(async (docId: string) => {
    try {
      await axios.delete(`/api/v1/documents/${docId}`);
      
      // Remove the document from the list
      setDocuments(prev => prev.filter(doc => doc.doc_id !== docId));
    } catch (error) {
      console.error('Error deleting document:', error);
      throw error;
    }
  }, []);

  const getDocumentStatus = useCallback(async (docId: string) => {
    try {
      const response = await axios.get(`/api/v1/documents/${docId}/status`);
      return response.data;
    } catch (error) {
      console.error('Error getting document status:', error);
      throw error;
    }
  }, []);

  const refreshDocuments = useCallback(async () => {
    try {
      const response = await axios.get('/api/v1/documents', {
        params: {
          tenant_id: 'org_123',
          limit: 100
        }
      });
      
      setDocuments(response.data);
    } catch (error) {
      console.error('Error refreshing documents:', error);
      throw error;
    }
  }, []);

  return (
    <DocumentContext.Provider value={{
      documents,
      uploadDocument,
      deleteDocument,
      getDocumentStatus,
      refreshDocuments,
    }}>
      {children}
    </DocumentContext.Provider>
  );
};
