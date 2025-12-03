/**
 * Home Page - Copilot-inspired chat interface
 * Main entry point with modular components
 */
'use client';

import { useState, useEffect } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { CenteredWelcome } from '@/components/layout/CenteredWelcome';
import { NavigationSidebar } from '@/components/navigation/NavigationSidebar';
import { ChatInput } from '@/components/input/ChatInput';
import { SuggestionPills } from '@/components/ui/SuggestionPills';
import { ConversationList } from '@/components/conversation/ConversationList';
import { useChatHandler } from '@/hooks/useChatHandler';
import { useConversationPersistence } from '@/hooks/useConversationPersistence';
import { useConversationRouter } from '@/hooks/useConversationRouter';
import { useChatStore } from '@/store/chat-store';
import styles from './page.module.css';

export default function HomePage() {
  const {
    currentConversation,
    isStreaming,
    currentStreamingMessage,
    sendMessage,
    createNewConversation,
  } = useChatHandler();

  const { conversations, deleteConversation: deleteConversationFromStore, setCurrentConversation } = useChatStore();
  const { deleteConversation } = useConversationPersistence();
  const { navigateToConversation, navigateToHome } = useConversationRouter();

  useConversationPersistence(); // Initialize persistence

  const [showWelcome, setShowWelcome] = useState(true);

  useEffect(() => {
    // Hide welcome if there's a current conversation with messages
    if (currentConversation && currentConversation.messages.length > 0) {
      setShowWelcome(false);
    }
  }, [currentConversation]);

  const handleSend = async (message: string) => {
    setShowWelcome(false);
    await sendMessage(message);
  };

  const handleSuggestionClick = (prompt: string) => {
    setShowWelcome(false);
    sendMessage(prompt);
  };

  const handleNewChat = () => {
    setCurrentConversation(null);
    navigateToHome();
    setShowWelcome(true);
  };

  const handleConversationClick = (conversationId: string) => {
    setShowWelcome(false);
    navigateToConversation(conversationId);
  };

  const handleConversationDelete = async (conversationId: string) => {
    await deleteConversation(conversationId);
    deleteConversationFromStore(conversationId);

    // If deleting current conversation, go home
    if (currentConversation?.id === conversationId) {
      navigateToHome();
      setShowWelcome(true);
    }
  };

  // Navigation items
  const navItems = [
    {
      id: 'new-chat',
      label: 'New Chat',
      icon: (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path
            d="M10 4.16667V15.8333M4.16667 10H15.8333"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ),
      onClick: handleNewChat,
    },
  ];

  // Suggestion pills (Copilot-style)
  const suggestions = [
    {
      id: '1',
      label: 'Create an image',
      onClick: () => handleSuggestionClick('Create an image for me'),
    },
    {
      id: '2',
      label: 'Simplify a topic',
      onClick: () => handleSuggestionClick('Simplify a complex topic'),
    },
    {
      id: '3',
      label: 'Write a first draft',
      onClick: () => handleSuggestionClick('Write a first draft'),
    },
    {
      id: '4',
      label: 'Improve writing',
      onClick: () => handleSuggestionClick('Improve my writing'),
    },
    {
      id: '5',
      label: 'Predict the future',
      onClick: () => handleSuggestionClick('Predict future trends'),
    },
    {
      id: '6',
      label: 'Rewrite a classic',
      onClick: () => handleSuggestionClick('Rewrite a classic story'),
    },
    {
      id: '7',
      label: 'Improve communication',
      onClick: () => handleSuggestionClick('Improve my communication'),
    },
    {
      id: '8',
      label: 'Make a meme',
      onClick: () => handleSuggestionClick('Make a meme'),
    },
  ];

  // Branding
  const branding = (
    <div className={styles.logo}>
      <div className={styles.logoIcon}>
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="8" fill="var(--color-interactive-primary)" />
          <path d="M16 8L20 16H12L16 8Z" fill="white" />
          <path d="M12 18H20L16 24L12 18Z" fill="white" />
        </svg>
      </div>
    </div>
  );

  return (
    <AppLayout
      sidebar={
        <NavigationSidebar items={navItems} branding={branding}>
          <ConversationList
            conversations={conversations}
            currentConversationId={currentConversation?.id}
            onConversationClick={handleConversationClick}
            onConversationDelete={handleConversationDelete}
          />
        </NavigationSidebar>
      }
    >
      {showWelcome && (!currentConversation || currentConversation.messages.length === 0) ? (
        <CenteredWelcome
          greeting="Hi there. What should we dive into today?"
          input={
            <ChatInput
              onSend={handleSend}
              disabled={isStreaming}
              placeholder="Message Insights..."
            />
          }
          suggestions={<SuggestionPills suggestions={suggestions} />}
        />
      ) : (
        <div className={styles.chatView}>
          <div className={styles.messages}>
            {currentConversation?.messages.map((message) => (
              <div
                key={message.id}
                className={`${styles.message} ${
                  message.role === 'user' ? styles.userMessage : styles.assistantMessage
                }`}
              >
                <div className={styles.messageContent}>
                  {message.content}
                </div>
              </div>
            ))}

            {isStreaming && currentStreamingMessage && (
              <div className={`${styles.message} ${styles.assistantMessage}`}>
                <div className={styles.messageContent}>
                  {currentStreamingMessage}
                </div>
              </div>
            )}
          </div>

          <div className={styles.inputContainer}>
            <ChatInput
              onSend={handleSend}
              disabled={isStreaming}
              placeholder="Message Insights..."
            />
          </div>
        </div>
      )}
    </AppLayout>
  );
}
