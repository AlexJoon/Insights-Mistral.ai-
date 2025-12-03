/**
 * useConversationPersistence Hook
 * Modular hook for syncing conversation state with persistence layer
 */

import { useEffect, useCallback, useRef } from 'react';
import { useChatStore } from '@/store/chat-store';
import { conversationPersistence } from '@/services/conversation-persistence';
import { Conversation } from '@/types/chat';

export function useConversationPersistence() {
  const { currentConversation, conversations, setConversations } = useChatStore();
  const loadedRef = useRef(false);

  // Load all conversations on mount (once)
  useEffect(() => {
    if (!loadedRef.current) {
      const loadConversations = async () => {
        const stored = await conversationPersistence.loadAll();
        if (stored.length > 0) {
          setConversations(stored);
        }
        loadedRef.current = true;
      };

      loadConversations();
    }
  }, [setConversations]);

  // Save current conversation whenever it changes
  useEffect(() => {
    if (currentConversation) {
      conversationPersistence.save(currentConversation);
    }
  }, [currentConversation]);

  // Sync conversations list to storage whenever it changes
  useEffect(() => {
    if (loadedRef.current && conversations.length > 0) {
      conversations.forEach(conv => {
        conversationPersistence.save(conv);
      });
    }
  }, [conversations]);

  const loadConversation = useCallback(async (conversationId: string): Promise<Conversation | null> => {
    return conversationPersistence.load(conversationId);
  }, []);

  const deleteConversation = useCallback(async (conversationId: string): Promise<void> => {
    await conversationPersistence.delete(conversationId);
  }, []);

  return {
    loadConversation,
    deleteConversation,
  };
}
