/**
 * Base API client for HTTP requests.
 * Provides a clean abstraction over fetch API.
 */

import { ApiConfig, ApiResponse, RequestOptions } from '@/types/api';

export class ApiClient {
  private baseUrl: string;
  private timeout: number;

  constructor(config: ApiConfig) {
    this.baseUrl = config.baseUrl;
    this.timeout = config.timeout || 30000;
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method: options.method || 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        body: options.body ? JSON.stringify(options.body) : undefined,
        signal: options.signal || controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          message: 'An error occurred',
          type: 'unknown_error',
        }));

        return {
          error: {
            message: errorData.message || 'Request failed',
            type: errorData.type || 'api_error',
          },
        };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          return {
            error: {
              message: 'Request timeout',
              type: 'timeout_error',
            },
          };
        }

        return {
          error: {
            message: error.message || 'Network error',
            type: 'network_error',
          },
        };
      }

      return {
        error: {
          message: 'Unknown error occurred',
          type: 'unknown_error',
        },
      };
    }
  }

  async get<T>(endpoint: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body });
  }

  async put<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body });
  }

  async delete<T>(endpoint: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  getBaseUrl(): string {
    return this.baseUrl;
  }
}

// Create singleton instance
const apiClient = new ApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

export default apiClient;
