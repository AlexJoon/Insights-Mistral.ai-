/**
 * Type definitions for chat functionality.
 * Centralized type safety for the application.
 */

export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

export interface ChatRequest {
  conversation_id?: string;
  message: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface StreamChunk {
  content: string;
  is_final: boolean;
  conversation_id?: string;
  message_id?: string;
}

export interface ApiError {
  error: string;
  message: string;
  type?: string;
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}
