/**
 * Server-Sent Events (SSE) client for streaming chat responses.
 * Handles real-time streaming with elegant error handling.
 */

import { StreamChunk } from '@/types/chat';

export type StreamCallback = (chunk: StreamChunk) => void;
export type ErrorCallback = (error: Error) => void;
export type CompleteCallback = () => void;

export interface SSEClientOptions {
  onChunk: StreamCallback;
  onError?: ErrorCallback;
  onComplete?: CompleteCallback;
}

export class SSEClient {
  private controller: AbortController | null = null;

  /**
   * Stream chat completion from the API.
   */
  async streamChatCompletion(
    endpoint: string,
    body: any,
    options: SSEClientOptions
  ): Promise<void> {
    this.controller = new AbortController();

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify(body),
        signal: this.controller.signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          message: 'Stream request failed',
        }));
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;

          if (line.startsWith('data: ')) {
            const data = line.slice(6);

            if (data.trim() === '[DONE]') {
              options.onComplete?.();
              return;
            }

            try {
              const chunk: StreamChunk = JSON.parse(data);

              if (chunk.is_final) {
                options.onComplete?.();
                return;
              }

              options.onChunk(chunk);
            } catch (e) {
              console.warn('Failed to parse SSE data:', data);
            }
          }
        }
      }

      options.onComplete?.();
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          // Stream was cancelled, don't treat as error
          return;
        }
        options.onError?.(error);
      } else {
        options.onError?.(new Error('Unknown error during streaming'));
      }
    } finally {
      this.controller = null;
    }
  }

  /**
   * Cancel the current stream.
   */
  cancel(): void {
    if (this.controller) {
      this.controller.abort();
      this.controller = null;
    }
  }

  /**
   * Check if a stream is currently active.
   */
  isStreaming(): boolean {
    return this.controller !== null;
  }
}

export default SSEClient;
