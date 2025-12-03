/**
 * RAG Service
 * Frontend service for querying RAG API endpoints
 */

import apiClient from './api-client';
import { ApiResponse } from '@/types/api';

export interface RAGQueryRequest {
  question: string;
  course_code?: string;
  instructor?: string;
  semester?: string;
  top_k?: number;
  stream?: boolean;
}

export interface RAGSource {
  id: string;
  content: string;
  similarity_score: number;
  metadata: {
    course_code?: string;
    instructor?: string;
    semester?: string;
    source_file?: string;
    [key: string]: any;
  };
}

export interface RAGQueryResponse {
  answer: string;
  sources: RAGSource[];
  metadata: {
    num_sources: number;
    filters_applied: Record<string, string>;
    top_k: number;
  };
}

export interface CourseResult {
  course_code: string;
  source_file: string;
  instructor?: string;
  semester?: string;
  relevance_score: number;
}

export interface CoursesResponse {
  courses: CourseResult[];
  count: number;
}

export interface RAGStats {
  vector_db: {
    total_vectors: number;
    dimension: number;
    index_fullness: number;
    namespaces: Record<string, any>;
  };
  status: string;
}

export interface RAGHealth {
  status: 'healthy' | 'unhealthy';
  vector_db: 'connected' | 'disconnected';
  error?: string;
}

export class RAGService {
  /**
   * Query syllabi using RAG.
   */
  async query(request: RAGQueryRequest): Promise<ApiResponse<RAGQueryResponse>> {
    return apiClient.post<RAGQueryResponse>('/api/rag/query', request);
  }

  /**
   * Get relevant courses for a search query.
   */
  async getCourses(query: string, topK: number = 10): Promise<ApiResponse<CoursesResponse>> {
    return apiClient.get<CoursesResponse>(`/api/rag/courses?q=${encodeURIComponent(query)}&top_k=${topK}`);
  }

  /**
   * Get RAG system statistics.
   */
  async getStats(): Promise<ApiResponse<RAGStats>> {
    return apiClient.get<RAGStats>('/api/rag/stats');
  }

  /**
   * Check RAG system health.
   */
  async checkHealth(): Promise<ApiResponse<RAGHealth>> {
    return apiClient.get<RAGHealth>('/api/rag/health');
  }

  /**
   * Delete a syllabus document.
   */
  async deleteSyllabus(documentId: string): Promise<ApiResponse<{ message: string; document_id: string }>> {
    return apiClient.delete(`/api/rag/syllabi/${documentId}`);
  }
}

// Create singleton instance
const ragService = new RAGService();
export default ragService;
