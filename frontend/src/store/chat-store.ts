/**
 * Chat state management store.
 * Uses Zustand for lightweight, modular state management.
 */

import { create } from 'zustand';
import { Conversation, Message } from '@/types/chat';

interface ChatState {
  // Current conversation
  currentConversation: Conversation | null;

  // All conversations
  conversations: Conversation[];

  // Streaming state
  isStreaming: boolean;
  currentStreamingMessage: string;

  // Error state
  error: string | null;

  // Actions
  setCurrentConversation: (conversation: Conversation | null) => void;
  setConversations: (conversations: Conversation[]) => void;
  addConversation: (conversation: Conversation) => void;
  updateConversation: (conversationId: string, updates: Partial<Conversation>) => void;
  deleteConversation: (conversationId: string) => void;

  addMessage: (conversationId: string, message: Message) => void;
  updateMessageContent: (conversationId: string, messageId: string, content: string) => void;

  setIsStreaming: (isStreaming: boolean) => void;
  setCurrentStreamingMessage: (message: string) => void;
  appendToStreamingMessage: (chunk: string) => void;
  clearStreamingMessage: () => void;

  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  currentConversation: null,
  conversations: [],
  isStreaming: false,
  currentStreamingMessage: '',
  error: null,

  setCurrentConversation: (conversation) => {
    set({ currentConversation: conversation });
  },

  setConversations: (conversations) => {
    set({ conversations });
  },

  addConversation: (conversation) => {
    set((state) => ({
      conversations: [conversation, ...state.conversations],
    }));
  },

  updateConversation: (conversationId, updates) => {
    set((state) => ({
      conversations: state.conversations.map((conv) =>
        conv.id === conversationId ? { ...conv, ...updates } : conv
      ),
      currentConversation:
        state.currentConversation?.id === conversationId
          ? { ...state.currentConversation, ...updates }
          : state.currentConversation,
    }));
  },

  deleteConversation: (conversationId) => {
    set((state) => ({
      conversations: state.conversations.filter((conv) => conv.id !== conversationId),
      currentConversation:
        state.currentConversation?.id === conversationId
          ? null
          : state.currentConversation,
    }));
  },

  addMessage: (conversationId, message) => {
    set((state) => {
      const updateMessages = (conv: Conversation) => ({
        ...conv,
        messages: [...conv.messages, message],
        updated_at: new Date().toISOString(),
      });

      return {
        conversations: state.conversations.map((conv) =>
          conv.id === conversationId ? updateMessages(conv) : conv
        ),
        currentConversation:
          state.currentConversation?.id === conversationId
            ? updateMessages(state.currentConversation)
            : state.currentConversation,
      };
    });
  },

  updateMessageContent: (conversationId, messageId, content) => {
    set((state) => {
      const updateMessages = (conv: Conversation) => ({
        ...conv,
        messages: conv.messages.map((msg) =>
          msg.id === messageId ? { ...msg, content } : msg
        ),
      });

      return {
        conversations: state.conversations.map((conv) =>
          conv.id === conversationId ? updateMessages(conv) : conv
        ),
        currentConversation:
          state.currentConversation?.id === conversationId
            ? updateMessages(state.currentConversation)
            : state.currentConversation,
      };
    });
  },

  setIsStreaming: (isStreaming) => {
    set({ isStreaming });
  },

  setCurrentStreamingMessage: (message) => {
    set({ currentStreamingMessage: message });
  },

  appendToStreamingMessage: (chunk) => {
    set((state) => ({
      currentStreamingMessage: state.currentStreamingMessage + chunk,
    }));
  },

  clearStreamingMessage: () => {
    set({ currentStreamingMessage: '' });
  },

  setError: (error) => {
    set({ error });
  },

  clearError: () => {
    set({ error: null });
  },
}));
