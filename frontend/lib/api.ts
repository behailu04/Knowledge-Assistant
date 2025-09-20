/**
 * API service for backend communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface QueryRequest {
  tenant_id: string;
  user_id: string;
  question: string;
  options?: {
    use_multi_hop?: boolean;
    use_self_consistency?: boolean;
    use_cot?: boolean;
    self_consistency_samples?: number;
    max_hops?: number;
  };
}

export interface QueryResponse {
  answer: string;
  sources: Array<{
    content: string;
    metadata: Record<string, any>;
    score: number;
  }>;
  confidence: number;
  reasoning_traces?: Array<{
    step: number;
    thought: string;
    action: string;
    observation: string;
  }>;
  hop_count: number;
  processing_time: number;
  query_id: string;
}

export interface Document {
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

export interface DocumentUploadRequest {
  file: File;
  tenant_id: string;
  doc_type?: string;
  language?: string;
}

export interface DocumentUploadResponse {
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

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    // Only set default Content-Type for non-FormData requests
    const defaultHeaders: Record<string, string> = options.body instanceof FormData 
      ? {} 
      : { 'Content-Type': 'application/json' };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error(`API Error for ${endpoint}:`, {
          status: response.status,
          statusText: response.statusText,
          errorData,
          url: response.url
        });
        throw new Error(
          errorData.detail || 
          errorData.message || 
          `HTTP error! status: ${response.status} - ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Query API
  async processQuery(request: QueryRequest): Promise<QueryResponse> {
    return this.request<QueryResponse>('/query', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Document API
  async uploadDocument(request: DocumentUploadRequest): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('tenant_id', request.tenant_id);
    formData.append('doc_type', request.doc_type || 'document');
    formData.append('language', request.language || 'en');

    return this.request<DocumentUploadResponse>('/documents/upload', {
      method: 'POST',
      headers: {
        // Don't set Content-Type, let browser set it with boundary
      },
      body: formData,
    });
  }

  async getDocuments(tenantId: string, limit: number = 100): Promise<Document[]> {
    return this.request<Document[]>(`/documents?tenant_id=${tenantId}&limit=${limit}`);
  }

  async getDocument(docId: string): Promise<Document> {
    return this.request<Document>(`/documents/${docId}`);
  }

  async deleteDocument(docId: string): Promise<void> {
    return this.request<void>(`/documents/${docId}`, {
      method: 'DELETE',
    });
  }

  async getDocumentStatus(docId: string): Promise<{
    doc_id: string;
    is_processed: boolean;
    status: string;
    metadata: Record<string, any>;
  }> {
    return this.request(`/documents/${docId}/status`);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/health');
  }
}

export const apiService = new ApiService();
export default apiService;
