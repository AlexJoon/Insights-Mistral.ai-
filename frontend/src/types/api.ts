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
