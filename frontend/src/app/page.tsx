/**
 * Home Page - Copilot-inspired chat interface
 * Main entry point with modular components
 */
'use client';

import { useState, useEffect } from 'react';
import { LuSquarePen, LuCompass } from 'react-icons/lu';
import { AppLayout } from '@/components/layout/AppLayout';
import { CenteredWelcome } from '@/components/layout/CenteredWelcome';
import { NavigationSidebar } from '@/components/navigation/NavigationSidebar';
import { ChatInput } from '@/components/input/ChatInput';
import { SuggestionPills } from '@/components/ui/SuggestionPills';
import { ConversationList } from '@/components/conversation/ConversationList';
import { Message } from '@/components/chat/Message';
import { useChatHandler } from '@/hooks/useChatHandler';
import { useConversationPersistence } from '@/hooks/useConversationPersistence';
import { useConversationRouter } from '@/hooks/useConversationRouter';
import { useSearchMode } from '@/hooks/useSearchMode';
import { useChatStore } from '@/store/chat-store';
import { fileUploadService } from '@/services/file-upload-service';
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
  const { searchMode, setSearchMode } = useSearchMode();

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

  const handleFileUpload = async (file: File) => {
    try {
      setShowWelcome(false);

      // Upload file to backend
      const response = await fileUploadService.uploadFile(
        file,
        currentConversation?.id
      );

      // Notify user of successful upload
      console.log('File uploaded successfully:', response);

      // Optionally send a message about the uploaded file
      await sendMessage(`I've uploaded a file: ${file.name}. Can you help me understand it?`);
    } catch (error) {
      console.error('File upload error:', error);
      alert('Failed to upload file. Please try again.');
    }
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
      icon: <LuSquarePen size={20} />,
      onClick: handleNewChat,
    },
    {
      id: 'explore',
      label: 'Explore',
      icon: <LuCompass size={20} />,
      onClick: () => {
        // TODO: Implement explore functionality
        window.location.hash = '#explore';
      },
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
              onFileUpload={handleFileUpload}
              searchMode={searchMode}
              onSearchModeChange={setSearchMode}
              disabled={isStreaming}
              placeholder="Message Insights..."
            />
          }
          suggestions={<SuggestionPills suggestions={suggestions} />}
        />
      ) : (
        <div className={styles.chatView}>
          <div className={styles.messages}>
            {currentConversation?.messages.map((message, index) => {
              // Find the corresponding user message for retry functionality
              const userMessage = message.role === 'assistant' && index > 0
                ? currentConversation.messages[index - 1]
                : null;

              const handleRetry = userMessage?.role === 'user'
                ? () => handleSend(userMessage.content)
                : undefined;

              return (
                <Message
                  key={message.id}
                  content={message.content}
                  role={message.role}
                  onRetry={handleRetry}
                />
              );
            })}

            {isStreaming && currentStreamingMessage && (
              <Message
                content={currentStreamingMessage}
                role="assistant"
                isStreaming={true}
              />
            )}
          </div>

          <div className={styles.inputContainer}>
            <ChatInput
              onSend={handleSend}
              onFileUpload={handleFileUpload}
              searchMode={searchMode}
              onSearchModeChange={setSearchMode}
              disabled={isStreaming}
              placeholder="Message Insights..."
            />
          </div>
        </div>
      )}
    </AppLayout>
  );
}
