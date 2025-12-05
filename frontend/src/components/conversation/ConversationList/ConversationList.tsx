/**
 * ConversationList - Displays list of conversations
 * Modular component for conversation history
 */
'use client';

import { Conversation } from '@/types/chat';
import styles from './ConversationList.module.css';

interface ConversationListProps {
  conversations: Conversation[];
  currentConversationId?: string;
  onConversationClick: (conversationId: string) => void;
  onConversationDelete?: (conversationId: string) => void;
}

export function ConversationList({
  conversations,
  currentConversationId,
  onConversationClick,
  onConversationDelete,
}: ConversationListProps) {
  const getConversationTitle = (conversation: Conversation): string => {
    if (conversation.title && conversation.title !== 'New Chat') {
      return conversation.title;
    }

    // Use first user message as title
    const firstMessage = conversation.messages.find((m) => m.role === 'user');
    if (firstMessage) {
      return firstMessage.content.slice(0, 50) + (firstMessage.content.length > 50 ? '...' : '');
    }

    return 'New Chat';
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;

    return date.toLocaleDateString();
  };

  if (conversations.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyText}>No conversations yet</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.heading}>Recent Threads</h2>
      <div className={styles.list}>
        {conversations.map((conversation) => (
        <div
          key={conversation.id}
          className={`${styles.item} ${
            currentConversationId === conversation.id ? styles.active : ''
          }`}
        >
          <button
            className={styles.itemButton}
            onClick={() => onConversationClick(conversation.id)}
          >
            <div className={styles.itemContent}>
              <span className={styles.itemTitle}>{getConversationTitle(conversation)}</span>
            </div>
          </button>

          {onConversationDelete && (
            <button
              className={styles.deleteButton}
              onClick={(e) => {
                e.stopPropagation();
                onConversationDelete(conversation.id);
              }}
              aria-label="Delete conversation"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path
                  d="M2 4H14M6 4V2.66667C6 2.29848 6.29848 2 6.66667 2H9.33333C9.70152 2 10 2.29848 10 2.66667V4M12.6667 4V13.3333C12.6667 13.7015 12.3682 14 12 14H4C3.63181 14 3.33333 13.7015 3.33333 13.3333V4"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          )}
        </div>
        ))}
      </div>
    </div>
  );
}
