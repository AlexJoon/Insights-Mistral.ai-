/**
 * Conversation Persistence Service
 * Modular service for persisting conversations to localStorage
 * Can be swapped with DB implementation later
 */

import { Conversation } from '@/types/chat';

const STORAGE_KEY = 'insights_conversations';

export interface ConversationPersistence {
  save(conversation: Conversation): Promise<void>;
  load(conversationId: string): Promise<Conversation | null>;
  loadAll(): Promise<Conversation[]>;
  delete(conversationId: string): Promise<void>;
  clear(): Promise<void>;
}

class LocalStoragePersistence implements ConversationPersistence {
  private getStoredConversations(): Conversation[] {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Failed to load conversations:', error);
      return [];
    }
  }

  private setStoredConversations(conversations: Conversation[]): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
    } catch (error) {
      console.error('Failed to save conversations:', error);
    }
  }

  async save(conversation: Conversation): Promise<void> {
    const conversations = this.getStoredConversations();
    const index = conversations.findIndex((c) => c.id === conversation.id);

    if (index !== -1) {
      conversations[index] = conversation;
    } else {
      conversations.unshift(conversation);
    }

    this.setStoredConversations(conversations);
  }

  async load(conversationId: string): Promise<Conversation | null> {
    const conversations = this.getStoredConversations();
    return conversations.find((c) => c.id === conversationId) || null;
  }

  async loadAll(): Promise<Conversation[]> {
    return this.getStoredConversations();
  }

  async delete(conversationId: string): Promise<void> {
    const conversations = this.getStoredConversations();
    const filtered = conversations.filter((c) => c.id !== conversationId);
    this.setStoredConversations(filtered);
  }

  async clear(): Promise<void> {
    localStorage.removeItem(STORAGE_KEY);
  }
}

// Export singleton instance
export const conversationPersistence: ConversationPersistence = new LocalStoragePersistence();
