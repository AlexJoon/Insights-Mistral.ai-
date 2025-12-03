/**
 * Chat service for handling chat operations.
 * Integrates SSE streaming with conversation management.
 */

import SSEClient, { SSEClientOptions } from './sse-client';
import { ChatRequest } from '@/types/chat';

export class ChatService {
  private sseClient: SSEClient;
  private apiUrl: string;

  constructor() {
    this.sseClient = new SSEClient();
    this.apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  /**
   * Send a chat message and stream the response.
   */
  async sendMessage(request: ChatRequest, options: SSEClientOptions): Promise<void> {
    const endpoint = `${this.apiUrl}/api/chat/stream`;
    return this.sseClient.streamChatCompletion(endpoint, request, options);
  }

  /**
   * Cancel the current streaming request.
   */
  cancelStream(): void {
    this.sseClient.cancel();
  }

  /**
   * Check if currently streaming.
   */
  isStreaming(): boolean {
    return this.sseClient.isStreaming();
  }
}

const chatService = new ChatService();
export default chatService;
