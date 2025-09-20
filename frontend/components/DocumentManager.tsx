'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  FileText, 
  Trash2, 
  Eye, 
  Download, 
  CheckCircle, 
  AlertCircle,
  Clock,
  RefreshCw
} from 'lucide-react';
import { useDocument } from '@/context/DocumentContext';

interface DocumentManagerProps {
  onViewChange: (view: string) => void;
}

const DocumentManager: React.FC<DocumentManagerProps> = ({ onViewChange }) => {
  const [uploading, setUploading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<any>(null);
  const { 
    documents, 
    loading,
    uploadDocument, 
    deleteDocument, 
    getDocumentStatus,
    refreshDocuments 
  } = useDocument();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    
    for (const file of acceptedFiles) {
      try {
        await uploadDocument(file, {
          tenant_id: 'org_123',
          doc_type: file.type.includes('pdf') ? 'pdf' : 'document',
          language: 'en'
        });
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }
    
    setUploading(false);
  }, [uploadDocument]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/markdown': ['.md']
    },
    multiple: true
  });

  const handleDelete = async (docId: string) => {
    try {
      await deleteDocument(docId);
      if (selectedDoc?.doc_id === docId) {
        setSelectedDoc(null);
      }
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'processing':
        return 'text-yellow-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Document List */}
      <div className="w-1/2 p-6 border-r border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Documents</h2>
          <button
            onClick={refreshDocuments}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`upload-area ${isDragActive ? 'dragover' : ''} mb-6`}
        >
          <input {...getInputProps()} />
          <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-600 mb-1">
            {isDragActive
              ? 'Drop files here...'
              : 'Drag & drop files here, or click to select'}
          </p>
          <p className="text-xs text-gray-500">
            Supports PDF, DOC, DOCX, TXT, MD files
          </p>
          {uploading && (
            <div className="mt-2 flex items-center justify-center space-x-2 text-blue-600">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span className="text-sm">Uploading...</span>
            </div>
          )}
        </div>

        {/* Document List */}
        <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
          {loading ? (
            <div className="text-center py-8 text-gray-500">
              <RefreshCw className="w-12 h-12 mx-auto mb-3 text-gray-300 animate-spin" />
              <p>Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No documents uploaded yet</p>
              <p className="text-sm">Upload some documents to get started</p>
            </div>
          ) : (
            documents.map((doc) => (
              <div
                key={doc.doc_id}
                className={`document-card cursor-pointer ${
                  selectedDoc?.doc_id === doc.doc_id ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => setSelectedDoc(doc)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <FileText className="w-5 h-5 text-gray-400 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {doc.original_path}
                      </h3>
                      <div className="flex items-center space-x-2 mt-1">
                        {getStatusIcon(doc.is_processed ? 'completed' : 'processing')}
                        <span className={`text-xs ${getStatusColor(doc.is_processed ? 'completed' : 'processing')}`}>
                          {doc.is_processed ? 'Processed' : 'Processing'}
                        </span>
                        <span className="text-xs text-gray-500">
                          • {formatFileSize(doc.file_size)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(doc.uploaded_at)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        // View document details
                      }}
                      className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(doc.doc_id);
                      }}
                      className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Document Details */}
      <div className="w-1/2 p-6">
        {selectedDoc ? (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Document Details
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">File Name</label>
                <p className="text-sm text-gray-900 mt-1">{selectedDoc.original_path}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Document ID</label>
                <p className="text-sm text-gray-900 mt-1 font-mono">{selectedDoc.doc_id}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Type</label>
                <p className="text-sm text-gray-900 mt-1 capitalize">{selectedDoc.doc_type}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Language</label>
                <p className="text-sm text-gray-900 mt-1 uppercase">{selectedDoc.language}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">File Size</label>
                <p className="text-sm text-gray-900 mt-1">{formatFileSize(selectedDoc.file_size)}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Uploaded</label>
                <p className="text-sm text-gray-900 mt-1">{formatDate(selectedDoc.uploaded_at)}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Status</label>
                <div className="flex items-center space-x-2 mt-1">
                  {getStatusIcon(selectedDoc.is_processed ? 'completed' : 'processing')}
                  <span className={`text-sm ${getStatusColor(selectedDoc.is_processed ? 'completed' : 'processing')}`}>
                    {selectedDoc.is_processed ? 'Processed and ready for queries' : 'Processing...'}
                  </span>
                </div>
              </div>
              
              {selectedDoc.metadata && Object.keys(selectedDoc.metadata).length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Metadata</label>
                  <div className="mt-1 p-3 bg-gray-50 rounded text-sm">
                    {Object.entries(selectedDoc.metadata).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-gray-600">{key}:</span>
                        <span className="text-gray-900">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <div className="mt-6 flex space-x-3">
              <button
                onClick={() => onViewChange('chat')}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Ask Questions
              </button>
              <button
                onClick={() => handleDelete(selectedDoc.doc_id)}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
              >
                Delete Document
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <FileText className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Select a document
            </h3>
            <p className="text-gray-600">
              Choose a document from the list to view its details
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentManager;
