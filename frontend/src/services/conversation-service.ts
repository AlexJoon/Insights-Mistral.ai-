/**
 * Conversation service for managing chat conversations.
 * Provides high-level API for conversation operations.
 */

import apiClient from './api-client';
import { Conversation } from '@/types/chat';
import { ApiResponse } from '@/types/api';

export class ConversationService {
  /**
   * Get all conversations.
   */
  async getAllConversations(): Promise<ApiResponse<{ conversations: Conversation[] }>> {
    return apiClient.get<{ conversations: Conversation[] }>('/api/conversations');
  }

  /**
   * Get a specific conversation by ID.
   */
  async getConversation(conversationId: string): Promise<ApiResponse<Conversation>> {
    return apiClient.get<Conversation>(`/api/conversations/${conversationId}`);
  }

  /**
   * Create a new conversation.
   */
  async createConversation(title: string = 'New Conversation'): Promise<ApiResponse<Conversation>> {
    return apiClient.post<Conversation>('/api/conversations', { title });
  }

  /**
   * Update a conversation's title.
   */
  async updateConversation(
    conversationId: string,
    title: string
  ): Promise<ApiResponse<Conversation>> {
    return apiClient.put<Conversation>(`/api/conversations/${conversationId}`, { title });
  }

  /**
   * Delete a conversation.
   */
  async deleteConversation(conversationId: string): Promise<ApiResponse<{ message: string }>> {
    return apiClient.delete<{ message: string }>(`/api/conversations/${conversationId}`);
  }
}

const conversationService = new ConversationService();
export default conversationService;
