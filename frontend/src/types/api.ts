/**
 * API-related type definitions.
 */

export interface ApiConfig {
  baseUrl: string;
  timeout?: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: {
    message: string;
    type: string;
  };
}

export type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

export interface RequestOptions {
  method?: HTTPMethod;
  headers?: Record<string, string>;
  body?: any;
  signal?: AbortSignal;
}

export interface FileUploadResponse {
  success: boolean;
  file_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  chunks_created?: number;
  message?: string;
  error?: string;
}

export interface FileMetadata {
  file_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  conversation_id?: string;
}
