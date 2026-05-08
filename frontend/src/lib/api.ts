import type {
  Document,
  DocumentListResponse,
  QueryRequest,
  QueryResponse,
  QueryListResponse,
  HealthCheck,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    return response.json();
  }

  async fetchDocuments(
    limit: number = 50,
    offset: number = 0,
    status?: string
  ): Promise<DocumentListResponse> {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    });
    if (status) params.set("status", status);
    return this.request<DocumentListResponse>(`/api/documents?${params}`);
  }

  async uploadDocument(files: File[]): Promise<{ documents: Document[] }> {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    const response = await fetch(`${this.baseUrl}/api/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `Upload failed: ${response.status}`);
    }

    return response.json();
  }

  async deleteDocument(documentId: string): Promise<void> {
    await this.request<void>(`/api/documents/${documentId}`, {
      method: "DELETE",
    });
  }

  async getDocument(documentId: string): Promise<Document> {
    return this.request<Document>(`/api/documents/${documentId}`);
  }

  async askQuestion(request: QueryRequest): Promise<QueryResponse> {
    return this.request<QueryResponse>("/api/queries", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getQueryHistory(
    limit: number = 20,
    offset: number = 0
  ): Promise<QueryListResponse> {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    });
    return this.request<QueryListResponse>(`/api/queries?${params}`);
  }

  async getQueryDetail(queryId: string): Promise<QueryResponse> {
    return this.request<QueryResponse>(`/api/queries/${queryId}`);
  }

  async healthCheck(): Promise<HealthCheck> {
    return this.request<HealthCheck>("/api/health");
  }
}

export const apiClient = new ApiClient(API_BASE);
